# Grind 日记录格式

权威数据是 **JSON，一天一个文件**：`data/days/YYYY-MM-DD.json`。  
同一文件里同时记 **运动记录** 和 **饮食记录**，并带当日合计与相对目标的剩余。不要用 Markdown 当数据源。

照片不进 git。餐次照片在聊天里发，仓库只存估算后的热量和宏量营养素。

档案和起步目标：`data/profile.json`、`data/targets.json`（暂定 2600 kcal / 蛋白 120 g / 脂肪 60 g / 碳水 390 g）。当前训练计划（尚未设定，不是日记录）：[data/training-plan.md](../data/training-plan.md)。当前蛋白粉：[data/supplements.json](../data/supplements.json)。

新的一天：复制 `data/day.template.json` 为 `data/days/YYYY-MM-DD.json`，改 `date`，按下面字段填。改餐次或组数后，重算 `totals` 和 `leftover`（`leftover = targets - totals`，可吃超成为负数）。

周报以后从这些 JSON **生成**，例如 `python3 scripts/week_stats.py 2026-W42`。

## 字段

| 字段 | 含义 |
| --- | --- |
| `schema_version` | 目前为 `1` |
| `date` | 日历日，ISO `YYYY-MM-DD` |
| `targets` | 当天目标快照（kcal / protein_g / fat_g / carbs_g）。目标改了也不回写旧文件 |
| `bodyweight_kg` | 可选。没称就 `null` |
| `trained` | 当天有训练则为 `true`（周统计数训练日） |
| `workouts[]` | 训练课：`name`、`time`（可选）、`lifts` |
| `workouts[].lifts[]` | `exercise` + `sets[]`（`reps`、`weight_kg`，可选 `rpe` / `notes`） |
| `meals[]` | 一餐。`source` 用 `chat-photo-estimate` 表示来自聊天照片估算 |
| `meals[].items[]` | 实际吃下去的食物（吃前 − 吃后剩余） |
| `meals[].photos_in_chat` | 照片在聊天里，不进仓库 |
| `totals` | 当日各餐 `items` 之和 |
| `leftover` | 目标 − 已吃 |
| `notes` | 当天备注 |

数字用 JSON number，不用字符串。文件 UTF-8、2 空格缩进、稳定键顺序，方便看 git diff。

聚合一周：`data/days/2026-10-13.json` … `2026-10-19.json`（ISO 周一到周日）。缺的文件 = 未记录，不要当成 0。周统计对已记录的天数：加总 `totals`、数 `trained == true`、列出全部 `lifts`、加总 `leftover`。

## 示例（已填的一天）

```json
{
  "schema_version": 1,
  "date": "2026-10-17",
  "targets": {
    "kcal": 2600,
    "protein_g": 120,
    "fat_g": 60,
    "carbs_g": 390
  },
  "bodyweight_kg": 58.0,
  "trained": true,
  "workouts": [
    {
      "name": "推日",
      "time": "18:30",
      "lifts": [
        {
          "exercise": "杠铃卧推",
          "sets": [
            { "set": 1, "reps": 8, "weight_kg": 40, "rpe": 7, "notes": "" },
            { "set": 2, "reps": 8, "weight_kg": 40, "rpe": 8, "notes": "" },
            { "set": 3, "reps": 7, "weight_kg": 40, "rpe": 9, "notes": "" }
          ]
        },
        {
          "exercise": "哑铃肩推",
          "sets": [
            { "set": 1, "reps": 10, "weight_kg": 12, "rpe": null, "notes": "" },
            { "set": 2, "reps": 10, "weight_kg": 12, "rpe": null, "notes": "" },
            { "set": 3, "reps": 10, "weight_kg": 12, "rpe": null, "notes": "" }
          ]
        }
      ],
      "notes": ""
    }
  ],
  "meals": [
    {
      "id": "breakfast",
      "name": "早餐",
      "time": "08:20",
      "source": "chat-photo-estimate",
      "photos_in_chat": true,
      "leftover_note": "吃完",
      "items": [
        {
          "food": "燕麦牛奶",
          "amount": "燕麦 80g + 牛奶 250ml",
          "kcal": 470,
          "protein_g": 20,
          "fat_g": 10,
          "carbs_g": 72
        }
      ],
      "totals": {
        "kcal": 470,
        "protein_g": 20,
        "fat_g": 10,
        "carbs_g": 72
      }
    },
    {
      "id": "lunch",
      "name": "午餐",
      "time": "12:15",
      "source": "chat-photo-estimate",
      "photos_in_chat": true,
      "leftover_note": "米饭剩约 1/4",
      "items": [
        {
          "food": "鸡胸肉",
          "amount": "约 150g 可食",
          "kcal": 248,
          "protein_g": 46,
          "fat_g": 5,
          "carbs_g": 0
        },
        {
          "food": "米饭",
          "amount": "约 150g 熟重（已扣剩余）",
          "kcal": 174,
          "protein_g": 4,
          "fat_g": 0,
          "carbs_g": 39
        },
        {
          "food": "西兰花",
          "amount": "约 100g",
          "kcal": 35,
          "protein_g": 3,
          "fat_g": 0,
          "carbs_g": 7
        }
      ],
      "totals": {
        "kcal": 457,
        "protein_g": 53,
        "fat_g": 5,
        "carbs_g": 46
      }
    }
  ],
  "totals": {
    "kcal": 927,
    "protein_g": 73,
    "fat_g": 15,
    "carbs_g": 118
  },
  "leftover": {
    "kcal": 1673,
    "protein_g": 47,
    "fat_g": 45,
    "carbs_g": 272
  },
  "notes": "示例日，不是真实记录。"
}
```

上面只写了两餐，所以合计远低于目标；真实一天会继续加餐直到接近目标。
