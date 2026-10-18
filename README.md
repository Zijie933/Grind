# Grind

每日权威数据：`data/days/YYYY-MM-DD.json`（当天训练 + 饮食 + 合计）。字段说明见 [docs/schema.md](docs/schema.md)。餐次照片不进 git。

## 如何同步这份仓库

档案、目标和每日日志在这个仓库里。餐次照片不提交（见 `.gitignore`）。

拉取最新：

```bash
git pull origin main
```

改完 `data/` 后推送：

```bash
git add data
git commit -m "Update grind log"
git push origin main
```
