"""Download PokéAPI CSV, D3 and image resources for a fully offline VisualDex."""
import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/pokeapi'
GENERATED = ROOT / 'data/generated'
VENDOR = ROOT / 'vendor'
IMAGES = ROOT / 'assets/images'
REPO = 'https://github.com/PokeAPI/pokeapi.git'
SPRITES_REPO = 'https://github.com/PokeAPI/sprites.git'
D3 = 'https://cdn.jsdelivr.net/npm/d3@7.9.0/'
REQUIRED = (
    'pokemon', 'pokemon_species', 'pokemon_species_names', 'pokemon_stats',
    'pokemon_types', 'pokemon_abilities', 'pokemon_moves', 'moves', 'types',
    'type_efficacy', 'stats', 'abilities', 'pokemon_evolution',
    'pokemon_egg_groups', 'egg_groups', 'items', 'versions', 'version_groups',
)
OPTIONAL = (
    'pokemon_forms', 'pokemon_form_names', 'pokemon_types_past', 'pokemon_stats_past',
    'type_efficacy_past', 'pokemon_abilities_past', 'languages', 'type_names',
    'move_names', 'move_meta', 'move_damage_classes', 'move_effect_prose',
    'pokemon_move_methods', 'move_changelog', 'evolution_chains', 'evolution_triggers',
    'item_names', 'item_prose', 'item_categories', 'item_flavor_text', 'pokemon_items',
    'locations', 'location_names', 'location_areas', 'location_area_prose',
    'encounters', 'encounter_slots', 'encounter_methods', 'encounter_conditions',
    'encounter_condition_values', 'encounter_condition_value_map', 'generations',
    'natures', 'machines', 'regions', 'pokemon_dex_numbers', 'pokedexes',
)

def download(url, path):
    if path.is_file() and path.stat().st_size: return
    req = Request(url, headers={'User-Agent': 'VisualDex-course-project/1.0'})
    with urlopen(req, timeout=90) as res:
        content = res.read()
    if not content: raise ValueError(f'Empty download: {url}')
    tmp = path.with_name(path.name + '.part')
    tmp.write_bytes(content); tmp.replace(path)

def snapshot_revision():
    result = subprocess.run(['git','ls-remote',REPO,'refs/heads/master'], check=True, text=True, capture_output=True, timeout=45)
    revision = result.stdout.split()[0]
    if len(revision) != 40: raise ValueError('Cannot resolve PokéAPI commit')
    return revision

def copy_sprite_files(repo, destination):
    sources = (
        ('sprites/pokemon/other/official-artwork', 'pokemon'),
        ('sprites/items', 'items'),
    )
    records = []
    for source, target in sources:
        src = repo / source
        files = sorted(src.rglob('*.png'))
        if not files:
            raise ValueError(f'No PNG files found in {src}')
        for file in files:
            rel = Path(target) / file.relative_to(src)
            output = destination / rel
            output.parent.mkdir(parents=True, exist_ok=True)
            # Preserve custom/local images instead of overwriting them.
            if not output.is_file() or output.stat().st_size == 0:
                part = output.with_name(output.name + '.part')
                shutil.copy2(file, part)
                part.replace(output)
            records.append({'path': rel.as_posix(), 'bytes': output.stat().st_size})
    return records

def download_images(destination):
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / 'sprites-manifest.json'
    previous = None
    if manifest_path.is_file():
        try:
            previous = json.loads(manifest_path.read_text(encoding='utf-8'))
            files = previous.get('files', [])
            if files and all((destination / f['path']).is_file() and (destination / f['path']).stat().st_size == f['bytes'] for f in files):
                print(f'Images already prepared: {len(files)} PNG files'); return
        except (OSError, ValueError, KeyError, TypeError):
            previous = None
    print('Downloading PokéAPI images (first download may take a while)...', flush=True)
    with tempfile.TemporaryDirectory(prefix='visualdex-sprites-') as temp:
        repo = Path(temp) / 'sprites'
        subprocess.run(['git','clone','--depth','1','--filter=blob:none','--sparse',SPRITES_REPO,str(repo)],check=True,timeout=900)
        # Recover an earlier snapshot when re-downloading missing images.
        old_revision = previous.get('revision') if isinstance(previous, dict) else None
        if old_revision and len(old_revision) == 40 and all(c in '0123456789abcdef' for c in old_revision):
            subprocess.run(['git','-C',str(repo),'fetch','--depth','1','origin',old_revision],check=True,timeout=900)
            subprocess.run(['git','-C',str(repo),'checkout','--detach',old_revision],check=True,timeout=900)
        subprocess.run(['git','-C',str(repo),'sparse-checkout','set','sprites/pokemon/other/official-artwork','sprites/items'],check=True,timeout=1800)
        revision = subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
        files = copy_sprite_files(repo,destination)
    counts = {
        'pokemon': sum(f['path'].startswith('pokemon/') and not f['path'].startswith('pokemon/shiny/') for f in files),
        'shiny': sum(f['path'].startswith('pokemon/shiny/') for f in files),
        'items': sum(f['path'].startswith('items/') for f in files),
    }
    manifest = {'source': SPRITES_REPO,'revision': revision,'generated_at': datetime.now(timezone.utc).isoformat(),'counts':counts,'files':files}
    tmp = manifest_path.with_suffix('.tmp'); tmp.write_text(json.dumps(manifest,indent=2),encoding='utf-8'); tmp.replace(manifest_path)
    print('Images ready:', counts)

def package(raw, generated, revision):
    tables = {}; records = {}; missing=[]
    for key in REQUIRED + OPTIONAL:
        path = raw / f'{key}.csv'
        if not path.is_file():
            if key in REQUIRED: raise FileNotFoundError(f'Missing required CSV: {path}')
            missing.append(key); continue
        text = path.read_text(encoding='utf-8-sig')
        reader = csv.reader(text.splitlines(keepends=True))
        header = next(reader, [])
        if not header or len(header) < 2: raise ValueError(f'Invalid CSV: {path}')
        count = sum(1 for row in reader if row)
        if key in REQUIRED and not count: raise ValueError(f'Empty required table: {path}')
        tables[key]=text
        records[key]={'rows':count,'columns':header,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    manifest={'revision':revision, 'generated_at':datetime.now(timezone.utc).isoformat(), 'source':REPO,'tables':records,'missing_optional':missing}
    payload={'revision':revision,'tables':tables}
    generated.mkdir(parents=True,exist_ok=True)
    target=generated/'pokemon-data.js'; tmp=target.with_suffix('.tmp')
    tmp.write_text('window.VisualDexData = '+json.dumps(payload,ensure_ascii=True,separators=(',',':'))+';\n',encoding='utf-8');tmp.replace(target)
    (generated/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'OK: {len(tables)} tables, {target.stat().st_size/1024/1024:.2f} MiB. Missing optional: {missing}')

def main():
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--build-only',action='store_true',help='Use already downloaded CSV files; no network')
    mode.add_argument('--images-only',action='store_true',help='Download images only; keep existing data untouched')
    mode.add_argument('--skip-images',action='store_true',help='Download CSV and D3 only')
    args=parser.parse_args()
    if args.images_only:
        download_images(IMAGES); return
    for path in (RAW, GENERATED, VENDOR): path.mkdir(parents=True,exist_ok=True)
    revfile=RAW/'revision.txt'
    if args.build_only:
        revision=revfile.read_text().strip() if revfile.exists() else 'local-unverified'
        if not (VENDOR/'d3.min.js').is_file(): print('WARNING: vendor/d3.min.js is missing; index.html needs it.')
    else:
        revision=revfile.read_text().strip() if revfile.exists() else snapshot_revision()
        if len(revision)!=40: raise ValueError('Invalid pinned revision in revision.txt')
        revfile.write_text(revision+'\n')
        base=f'https://raw.githubusercontent.com/PokeAPI/pokeapi/{revision}/data/v2/csv/'
        def get(key):
            try: download(base+key+'.csv',RAW/(key+'.csv')); print('OK',key,flush=True)
            except HTTPError as err:
                if key in OPTIONAL and err.code==404: print('Not available:',key,flush=True)
                else: raise
        with ThreadPoolExecutor(max_workers=5) as pool: list(pool.map(get,REQUIRED+OPTIONAL))
        download(D3+'dist/d3.min.js',VENDOR/'d3.min.js')
        download(D3+'LICENSE',VENDOR/'D3-LICENSE.txt')
    package(RAW,GENERATED,revision)
    if not args.build_only and not args.skip_images:
        download_images(IMAGES)

if __name__=='__main__':
    try: main()
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        print('Setup failed:',exc,file=sys.stderr); sys.exit(1)
