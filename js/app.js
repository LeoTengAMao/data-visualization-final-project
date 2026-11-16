(() => {
  const status = document.querySelector('#status');
  const picker = document.querySelector('#pokemon');
  const shiny = document.querySelector('#shiny');
  const pokemonImage = document.querySelector('#pokemon-image');
  const imageStatus = document.querySelector('#image-status');
  for (const [id, title, file] of VisualDex.modules) {
    const card = document.createElement('div'); card.className = 'module';
    const h = document.createElement('strong'); h.textContent = `${id} ${title}`;
    const s = document.createElement('span'); s.textContent = `待開發：js/modules/${file}`;
    card.append(h,s); document.querySelector('#modules').append(card);
  }
  if (!window.d3 || !VisualDex.hasTable('pokemon') || !VisualDex.hasTable('pokemon_stats')) {
    status.textContent = '尚未完成資料初始化。請在專案根目錄執行：python scripts/setup.py';
    return;
  }
  const rows = VisualDex.table('pokemon');
  const names = new Map(VisualDex.table('pokemon_species_names').filter(d => d.local_language_id === 4).map(d => [d.pokemon_species_id,d.name]));
  const stats = VisualDex.table('pokemon_stats');
  const statNames = new Map([[1,'HP'],[2,'攻擊'],[3,'防禦'],[4,'特攻'],[5,'特防'],[6,'速度']]);
  status.textContent = '初始化成功：D3 與本機資料已載入。';
  document.querySelector('#dataset').textContent = `寶可夢／型態資料：${rows.length} 筆；資料快照：${VisualDexData.revision || '本機'}`;
  for(const p of rows.filter(d => d.is_default === 1)) {
    const opt = document.createElement('option'); opt.value = p.id; opt.textContent = `${p.species_id} ${names.get(p.species_id) || p.identifier}`; picker.append(opt);
  }
  picker.disabled = false;
  shiny.disabled = false;
  pokemonImage.addEventListener('load', () => { pokemonImage.hidden = false; imageStatus.textContent = ''; });
  pokemonImage.addEventListener('error', () => { pokemonImage.hidden = true; imageStatus.textContent = '此型態的圖片尚未收錄或未下載。'; });
  function updateImage() {
    if (!picker.value) return;
    pokemonImage.hidden = true;
    imageStatus.textContent = '載入圖片…';
    pokemonImage.alt = `${picker.selectedOptions[0]?.textContent || '寶可夢'}${shiny.checked ? '（色違）' : ''}`;
    pokemonImage.src = VisualDex.pokemonImagePath(picker.value, shiny.checked);
  }
  function render() {
    const id = Number(picker.value);
    VisualDex.setState({pokemon_id: id});
    updateImage();
    const data = stats.filter(d => d.pokemon_id === id && statNames.has(d.stat_id));
    const target = d3.select('#chart'); target.selectAll('*').remove();
    const svg = target.append('svg').attr('viewBox','0 0 650 230').attr('role','img').attr('aria-label','基礎種族值示範');
    const x = d3.scaleLinear().domain([0, Math.max(1,d3.max(data,d=>d.base_stat) || 1)]).range([0,480]);
    const y = d3.scaleBand().domain(data.map(d=>statNames.get(d.stat_id))).range([8,220]).padding(.25);
    svg.append('g').attr('transform','translate(65,0)').call(d3.axisLeft(y));
    svg.selectAll('rect').data(data).join('rect').attr('x',65).attr('y',d=>y(statNames.get(d.stat_id))).attr('width',d=>x(d.base_stat)).attr('height',y.bandwidth()).attr('fill','#177f83');
    svg.selectAll('.value').data(data).join('text').attr('class','value').attr('x',d=>73+x(d.base_stat)).attr('y',d=>y(statNames.get(d.stat_id))+y.bandwidth()/2).attr('dominant-baseline','middle').text(d=>d.base_stat);
  }
  picker.addEventListener('change',render); if(picker.options.length) render();
  shiny.addEventListener('change',updateImage);
})();
