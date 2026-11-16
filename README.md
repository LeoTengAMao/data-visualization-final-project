# Pokémon VisualDex

四人資料視覺化期末專題：離線執行的 HTML、CSS、JavaScript 與 D3 程式。此版本只有初始化骨架和種族值載入測試，並非九個分析模組的完成版。

## 一次性初始化（需要網路）

1. 將本資料夾的內容放入自己已 clone 的 GitHub 專案根目錄。不要覆蓋既有 README 或其他檔案；先檢查合併。
2. 安裝 Python 3.10+ 與 Git，開啟 PowerShell，切換到 `index.html` 所在位置。
3. 執行 `py -3 scripts/setup.py`（或 `python scripts/setup.py`）。程式下載 PokéAPI CSV、鎖定資料快照、下載本機 D3 7.9.0，產生 JavaScript 資料包，並下載寶可夢及道具圖片。下載中斷可再次執行，已有非空檔案會保留。
4. 完成後雙擊 `index.html`；測試畫面應顯示資料載入成功，選擇一隻寶可夢可顯示種族值及普通／色違立繪。之後不需要網路、API 或伺服器。
5. 若 GitHub 有預先下載的資料包和 D3，其餘組員不需要重新下載。檢查資料包檔案大小、資料授權及學校要求，再決定是否提交。

## 資料與版本

- `data/raw/pokeapi/`：原始 CSV 和來源 commit，CSV 預設不提交 Git，以免體積過大。
- `data/generated/pokemon-data.js`：網頁執行時所需的本機資料、`manifest.json` 記錄快照、欄位、筆數與 SHA-256。請勿手改生成檔案。
- `data/manual/`：色違、道館、版本遭遇及特殊道具規則需補充。PokéAPI 的資料覆蓋不等於任何一代的完整合法機制。
- `assets/images/`：本機圖片；`pokemon/` 普通立繪、`pokemon/shiny/` 色違、`items/` 道具、`sprites-manifest.json` 圖片來源。首次圖片下載可能較久。圖片目錄預設不提交 Git。
- `vendor/`：D3 固定版本與授權文件。

資料包含跨世代基礎資訊。AC2、AC5、AC7、AC8、AC9 必須依遊戲版本過濾；`pokemon_id` 指寶可夢資料列／型態，`species_id` 指物種，`version_group_id` 指共同機制版本組，`version_id` 指個別版本。不要將當代種族值直接當作舊世代數值；歷史資料需額外驗證。

### 初始化選項

- `python scripts/setup.py --images-only`：只下載圖片，適合已有 CSV 的組員。
- `python scripts/setup.py --skip-images`：只下載資料及 D3。
- `python scripts/setup.py --build-only`：從本機 CSV 重建資料包，不連網。

JavaScript 統一以 `VisualDex.pokemonImagePath(pokemon.id, false)` 或 `VisualDex.pokemonImagePath(pokemon.id, true)` 取得普通／色違本機圖片路徑，以 `VisualDex.itemImagePath(item.identifier)` 取得道具路徑。若圖檔不存在，應顯示缺圖提示，不能用其他型態代替。

## 四人實作分工

-代訂

新增模組 JS 至 `js/modules/`，各自使用分支開發，整合時統一使用 `js/core/data.js` 的 `VisualDex.table(name)` 與 `js/core/state.js` 的共享狀態。`app.js` 目前只是一個測試頁面。

## 資料來源

- [PokéAPI CSV](https://github.com/PokeAPI/pokeapi/tree/master/data/v2/csv)、[文件](https://pokeapi.co/docs/v2)
- [PokéAPI Sprites](https://github.com/PokeAPI/sprites)：寶可夢立繪、色違與道具圖片
- [D3](https://d3js.org/getting-started)
- [劍盾道館陣容](https://pokemondb.net/sword-shield/gymleaders)
- [色違機制](https://www.serebii.net/swordshield/shinypokemon.shtml)
- [EV 訓練](https://www.serebii.net/swordshield/evtraining.shtml)
- [Pokémon Showdown 資料](https://github.com/smogon/pokemon-showdown/tree/master/data)
- Kaggle 補充：[Complete Pokémon Dataset](https://www.kaggle.com/datasets/rounakbanik/pokemon)、[Sun Moon Gen 7 Stats](https://www.kaggle.com/datasets/mylesoneill/pokemon-sun-and-moon-gen-7-stats)。核對資料來源、授權與版本後再整合。

Pokémon 名稱、角色與圖像之相關權利屬於各權利人；本專案供課程學習及分析，非官方產品。公開 GitHub 前確認第三方資料與圖像的使用條款。
