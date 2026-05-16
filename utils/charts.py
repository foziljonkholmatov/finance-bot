"""
utils/charts.py — Matplotlib grafiklar
"""
from __future__ import annotations
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from services.currency_service import fmt_uzs

COLOR_INCOME  = "#2ecc71"
COLOR_EXPENSE = "#e74c3c"
COLOR_BG      = "#1e1e2e"
COLOR_TEXT    = "#cdd6f4"
COLOR_GRID    = "#313244"

MONTHS_UZ = ["","Yanvar","Fevral","Mart","Aprel","May","Iyun",
              "Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]


def _dark(fig, ax):
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_BG)
    ax.tick_params(colors=COLOR_TEXT, labelsize=9)
    for spine in ["bottom","left"]:
        ax.spines[spine].set_color(COLOR_GRID)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color=COLOR_GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def _to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def monthly_bar(income: int, expense: int, year: int, month: int) -> bytes:
    fig, ax = plt.subplots(figsize=(6, 4))
    _dark(fig, ax)
    bars = ax.bar(["Daromad", "Harajat"],
                  [income/100, expense/100],
                  color=[COLOR_INCOME, COLOR_EXPENSE], width=0.45, zorder=3)
    for bar, val in zip(bars, [income, expense]):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*1.02,
                fmt_uzs(val), ha="center", va="bottom",
                color=COLOR_TEXT, fontsize=8.5, fontweight="bold")
    balance = income - expense
    sign = "+" if balance >= 0 else "-"
    ax.set_title(f"{MONTHS_UZ[month]} {year}  |  Balans: {sign}{fmt_uzs(abs(balance))}",
                 color=COLOR_TEXT, fontsize=10, pad=10)
    ax.set_ylabel("So'm", color=COLOR_TEXT, fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"{int(x):,}".replace(",", " ")))
    return _to_bytes(fig)


def category_pie(rows: list[dict], type_: str) -> bytes:
    if not rows:
        return b""
    labels = [r["category"] for r in rows]
    sizes  = [r["total"] for r in rows]
    cmap   = plt.cm.get_cmap("Set3", len(labels))
    fig, ax = plt.subplots(figsize=(6, 5))
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_BG)
    wedges, _, autotexts = ax.pie(
        sizes, colors=[cmap(i) for i in range(len(labels))],
        autopct="%1.1f%%", startangle=140, pctdistance=0.75,
        wedgeprops={"linewidth":0.8,"edgecolor":COLOR_BG}
    )
    for at in autotexts:
        at.set_color(COLOR_BG); at.set_fontsize(8)
    ax.legend(wedges, labels, loc="lower center", bbox_to_anchor=(0.5,-0.18),
              ncol=2, fontsize=8, framealpha=0, labelcolor=COLOR_TEXT)
    label = "Harajat" if type_ == "expense" else "Daromad"
    ax.set_title(f"{label} kategoriyalari", color=COLOR_TEXT, fontsize=10, pad=12)
    return _to_bytes(fig)


def weekly_trend(rows: list[dict]) -> bytes:
    if not rows:
        return b""
    days     = [r["day"].strftime("%d.%m") for r in rows]
    incomes  = [r["income"]/100 for r in rows]
    expenses = [r["expense"]/100 for r in rows]
    x = np.arange(len(days))
    fig, ax = plt.subplots(figsize=(7, 4))
    _dark(fig, ax)
    ax.plot(x, incomes,  marker="o", color=COLOR_INCOME,  linewidth=2, markersize=5, label="Daromad")
    ax.plot(x, expenses, marker="o", color=COLOR_EXPENSE, linewidth=2, markersize=5, label="Harajat")
    ax.fill_between(x, incomes,  alpha=0.12, color=COLOR_INCOME)
    ax.fill_between(x, expenses, alpha=0.12, color=COLOR_EXPENSE)
    ax.set_xticks(x); ax.set_xticklabels(days, color=COLOR_TEXT, fontsize=8)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"{int(v):,}".replace(",", " ")))
    ax.set_title("So'nggi 7 kun trendi", color=COLOR_TEXT, fontsize=10, pad=10)
    ax.legend(fontsize=8, framealpha=0, labelcolor=COLOR_TEXT)
    return _to_bytes(fig)
