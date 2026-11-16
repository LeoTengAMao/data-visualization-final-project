// Local paths: use pokemon.id (not species_id) for alternate forms.
window.VisualDex = window.VisualDex || {};
VisualDex.pokemonImagePath = (pokemonId, shiny = false) => {
  const id = Number(pokemonId);
  if (!Number.isSafeInteger(id) || id < 1) return null;
  return `assets/images/pokemon/${shiny ? 'shiny/' : ''}${id}.png`;
};
VisualDex.itemImagePath = (identifier) => {
  return typeof identifier === 'string' && /^[a-z0-9-]+$/.test(identifier) ? `assets/images/items/${identifier}.png` : null;
};
