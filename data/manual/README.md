# 版本專屬補充資料

先定案遊戲版本，例如 Sword / Shield；以下 CSV 是待收集資料的欄位建議，尚未填入實際數據。

- `gym_teams.csv`: version_id, gym_id, leader, pokemon_id, level, move_id（館主陣容及招式）
- `shiny_rules.csv`: version_group_id, method, condition, probability, attempt_seconds, source_url（機率及條件；時間可由實測取得）
- `encounter_details.csv`: version_id, location_id, pokemon_id, encounter_method, weather, encounter_rate, unlock_condition, source_url（出現與解鎖條件）
- `held_item_rules.csv`: version_group_id, item_id, trigger, effect_type, multiplier, restriction, source_url（戰鬥規則及版本）
- `breeding_rules.csv`: version_group_id, method, condition, source_url（遺傳例外及傳承規則）

不要把空白欄位視為 0，也不要把不同版本的資料直接接在一起。每筆資料應有可追溯來源。
