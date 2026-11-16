// The setup script generates local CSV strings. No fetch() is needed at runtime.
window.VisualDex = window.VisualDex || {};
(() => {
  const cache = new Map();
  VisualDex.table = function(name) {
    if (!window.d3 || !window.VisualDexData?.tables?.[name]) return [];
    if (!cache.has(name)) cache.set(name, d3.csvParse(VisualDexData.tables[name], d3.autoType));
    return cache.get(name);
  };
  VisualDex.hasTable = name => Boolean(window.VisualDexData?.tables?.[name]);
})();
