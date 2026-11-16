"""Download a pinned PokéAPI CSV snapshot and D3, then build an offline JS bundle."""
import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/pokeapi'
GENERATED = ROOT / 'data/generated'
VENDOR = ROOT / 'vendor'
REPO = 'https://github.com/PokeAPI/pokeapi.git'
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
    parser=argparse.ArgumentParser(); parser.add_argument('--build-only',action='store_true',help='Use already downloaded CSV files; no network'); args=parser.parse_args()
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

if __name__=='__main__':
    try: main()
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        print('Setup failed:',exc,file=sys.stderr); sys.exit(1)
