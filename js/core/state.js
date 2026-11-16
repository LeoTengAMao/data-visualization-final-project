// Shared selection state: a team contains pokemon_id, not species_id.
window.VisualDex = window.VisualDex || {};
VisualDex.state = { version_group_id: null, version_id: null, pokemon_id: null, team: [], gym_id: null };
VisualDex.setState = changes => {
  Object.assign(VisualDex.state, changes);
  document.dispatchEvent(new CustomEvent('visualdex:state', {detail: {...VisualDex.state}}));
};
