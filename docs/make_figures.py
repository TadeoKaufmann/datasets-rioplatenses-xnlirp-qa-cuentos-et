"""Draw the README figures from the numbers reported in the thesis.

    python docs/make_figures.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent.parent / "figures"
BLUE, ORANGE, AQUA = "#257de0", "#f47230", "#00b894"
INK, MUTED, SURFACE = "#191919", "#666666", "#ffffff"

# Table 3.9: share of instances with a dialectal change, by MultiNLI genre (%)
DIALECTAL_BY_GENRE = {
    "Telephone": 60.8, "Fiction": 59.6, "Face-to-face": 51.2, "9/11": 40.7, "Letters": 36.8,
    "Travel": 30.3, "Slate": 22.9, "OUP": 20.9, "Verbatim": 20.4, "Government": 14.7,
}

# Table 5.4: macro F1 (mean, std over 3 seeds) at K = 200, 500, 1000, type D excluded
K = [200, 500, 1000]
NLI = {
    "BETO base": {"ES→ES": [(44.1, 1.3), (55.8, 1.8), (63.0, 1.5)],
                  "ES→RP": [(44.0, 0.6), (56.0, 1.9), (62.8, 1.6)],
                  "RP→RP": [(43.6, 3.0), (55.1, 0.8), (63.3, 1.4)]},
    "BETO aug.": {"ES→ES": [(43.1, 1.1), (56.1, 0.8), (63.4, 1.0)],
                  "ES→RP": [(43.1, 0.7), (56.4, 1.5), (63.1, 1.2)],
                  "RP→RP": [(43.4, 1.5), (55.9, 0.6), (63.6, 1.8)]},
    "BETO ET": {"ES→ES": [(42.9, 1.7), (55.9, 0.7), (62.6, 0.5)],
                "ES→RP": [(43.1, 1.8), (55.9, 1.1), (62.7, 0.3)],
                "RP→RP": [(42.6, 1.6), (55.2, 1.0), (63.4, 0.9)]},
}


def style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#d0d0d0")
    ax.tick_params(colors=MUTED, length=0)
    ax.set_axisbelow(True)


def save(fig, name):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / name, dpi=160, facecolor=SURFACE)
    plt.close(fig)


def genres():
    names, values = list(DIALECTAL_BY_GENRE), list(DIALECTAL_BY_GENRE.values())
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.barh(names, values, color=BLUE, height=0.68)
    ax.invert_yaxis()
    for y, v in enumerate(values):
        ax.text(v + 0.8, y, f"{v:.1f}%", va="center", color=INK, fontsize=9)
    style(ax)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([])
    ax.set_xlim(0, 70)
    ax.set_title("Instances that needed a dialectal change, by text genre", color=INK, loc="left")
    fig.tight_layout()
    save(fig, "dialectal_change_by_genre.png")


def nli_curves():
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8), sharey=True)
    series = [("ES→ES", BLUE, "o", -18), ("ES→RP", ORANGE, "s", 0), ("RP→RP", AQUA, "^", 18)]
    for ax, (model, conditions) in zip(axes, NLI.items()):
        for name, colour, marker, shift in series:
            mean, std = zip(*conditions[name])
            ax.errorbar([k + shift for k in K], mean, yerr=std, label=name, color=colour,
                        marker=marker, markersize=6, lw=2, capsize=3, elinewidth=1)
        style(ax)
        ax.grid(axis="y", color="#ececec")
        ax.set_title(model, color=INK)
        ax.set_xticks(K, ["200", "500", "1000"])
        ax.set_xlabel("training instances (K)", color=MUTED)
    axes[0].set_ylabel("macro F1 on test (%)", color=MUTED)
    axes[0].legend(title="train→test", frameon=False, loc="lower right")
    fig.suptitle("Training size moves the score; the variety of Spanish does not", color=INK,
                 x=0.01, ha="left")
    fig.tight_layout()
    save(fig, "nli_f1_by_training_size.png")


if __name__ == "__main__":
    genres()
    nli_curves()
