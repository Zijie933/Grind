#!/usr/bin/env python3
"""Aggregate Grind daily JSON logs for an ISO week (Monday–Sunday)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAYS_DIR = ROOT / "data" / "days"
MACROS = ("kcal", "protein_g", "fat_g", "carbs_g")
LABELS = {
    "kcal": "热量 kcal",
    "protein_g": "蛋白 g",
    "fat_g": "脂肪 g",
    "carbs_g": "碳水 g",
}


def parse_iso_week(value: str) -> date:
    return datetime.strptime(f"{value}-1", "%G-W%V-%u").date()


def week_monday(value: str | None) -> date:
    if not value:
        return date.today() - timedelta(days=date.today().weekday())
    if "W" in value.upper():
        return parse_iso_week(value.upper())
    day = date.fromisoformat(value)
    return day - timedelta(days=day.weekday())


def empty_macros() -> dict[str, float]:
    return {key: 0.0 for key in MACROS}


def add_macros(dst: dict[str, float], src: dict) -> None:
    for key in MACROS:
        dst[key] += float(src.get(key) or 0)


def meal_item_totals(day: dict) -> dict[str, float]:
    totals = empty_macros()
    for meal in day.get("meals") or []:
        items = meal.get("items")
        if items:
            for item in items:
                add_macros(totals, item)
        elif meal.get("totals"):
            add_macros(totals, meal["totals"])
    return totals


def load_day(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def format_macros(values: dict[str, float]) -> str:
    parts = []
    for key in MACROS:
        number = values[key]
        text = str(int(number)) if number == int(number) else f"{number:.1f}"
        parts.append(f"{LABELS[key]} {text}")
    return " · ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sum a week's Grind day JSON files.")
    parser.add_argument(
        "week",
        nargs="?",
        help="ISO week (2026-W42) or any date in that week (2026-10-18). Default: this week.",
    )
    args = parser.parse_args()

    monday = week_monday(args.week)
    days = [monday + timedelta(days=offset) for offset in range(7)]
    iso_week = f"{monday.isocalendar().year}-W{monday.isocalendar().week:02d}"

    logged: list[dict] = []
    missing: list[str] = []
    for day in days:
        path = DAYS_DIR / f"{day.isoformat()}.json"
        if path.exists():
            payload = load_day(path)
            payload["_path"] = str(path.relative_to(ROOT))
            logged.append(payload)
        else:
            missing.append(day.isoformat())

    consumed = empty_macros()
    leftover = empty_macros()
    targets = empty_macros()
    training_days = 0
    lifts: list[str] = []

    print(f"ISO 周 {iso_week}（{days[0].isoformat()} ～ {days[-1].isoformat()}）")
    print(f"已记录 {len(logged)} / 7 天")
    if missing:
        print("未记录：" + ", ".join(missing))
    print()

    for day in logged:
        recomputed = meal_item_totals(day)
        stored = day.get("totals") or empty_macros()
        add_macros(consumed, recomputed)
        add_macros(leftover, day.get("leftover") or empty_macros())
        add_macros(targets, day.get("targets") or empty_macros())
        trained = bool(day.get("trained") or day.get("workouts"))
        if trained:
            training_days += 1
        mismatch = [
            key
            for key in MACROS
            if round(float(stored.get(key) or 0) - recomputed[key], 1) != 0
        ]
        flag = " ⚠ totals 与餐次加总不一致" if mismatch else ""
        print(f"- {day.get('date')}: 训练={'是' if trained else '否'} · 已吃 {format_macros(recomputed)}{flag}")
        for session in day.get("workouts") or []:
            session_name = session.get("name") or "训练"
            for lift in session.get("lifts") or []:
                sets = lift.get("sets") or []
                set_bits = []
                for item in sets:
                    weight = item.get("weight_kg")
                    reps = item.get("reps")
                    bit = f"{weight}kg×{reps}" if weight is not None else f"{reps} reps"
                    set_bits.append(bit)
                line = f"  {day.get('date')} {session_name} / {lift.get('exercise')}: {len(sets)} 组 ({', '.join(set_bits)})"
                lifts.append(line)
                print(line)

    print()
    print(f"训练日：{training_days}")
    print("已吃合计：" + format_macros(consumed))
    print("目标合计（按已记录天）：" + format_macros(targets))
    print("剩余合计：" + format_macros(leftover))
    if not lifts:
        print("动作组数：无")
    return 0


if __name__ == "__main__":
    sys.exit(main())
