# 寶可夢圖片

`python scripts/setup.py --images-only` 會從 [PokéAPI Sprites](https://github.com/PokeAPI/sprites) 下載普通立繪、色違立繪及道具 PNG。所有圖片在本機載入，不需 API。

- `pokemon/{pokemon_id}.png`：普通立繪。
- `pokemon/shiny/{pokemon_id}.png`：色違立繪（部分為社群製作、少數型態缺圖）。
- `items/{identifier}.png`：道具圖示，例如 `leftovers.png`。
- `sprites-manifest.json`：資料來源、原始 commit、檔案筆數。

Git 預設忽略下載的圖片目錄，以免儲存庫過大及無意重新散布圖片。公開前確認 Pokémon 圖像與第三方作品的使用權利。
