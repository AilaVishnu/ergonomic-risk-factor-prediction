"""
Build outputs/figures/methodology_flowchart.png — a clean
pipeline diagram (Raw data -> Cleaning -> Feature engineering ->
Stage 1 -> Stage 2 -> Web app).

Run:
    python src/build_pipeline_flowchart.py
"""

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT  = ROOT / "outputs" / "figures" / "methodology_flowchart.png"

NAVY    = "#1F3B73"
ACCENT  = "#2E86AB"
GREY    = "#8C8C8C"
WHITE   = "#FFFFFF"
LIGHT   = "#F2F2F2"


def box(ax, x, y, w, h, title, subtitle="", fill=NAVY, text_color=WHITE,
        subtitle_color="#EAEAEA"):
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=0, facecolor=fill,
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h * 0.62, title,
            ha="center", va="center",
            fontsize=11, fontweight="bold", color=text_color)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.28, subtitle,
                ha="center", va="center",
                fontsize=8, color=subtitle_color)


def arrow(ax, x1, y1, x2, y2, color=GREY):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6,
                        shrinkA=2, shrinkB=2),
    )


def build():
    fig, ax = plt.subplots(figsize=(13, 4.8), dpi=150)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 5)
    ax.axis("off")

    # Title strip
    ax.text(6.5, 4.6, "Project pipeline (raw inputs to interactive prediction)",
            ha="center", va="center",
            fontsize=13, fontweight="bold", color=NAVY)

    bw, bh = 1.9, 1.2

    # ----- Inputs row (top) -----
    box(ax, 0.4, 2.8, bw, bh, "Rider survey",
        "delivery_rider_survey.csv\n182 rows × 48 cols", fill=ACCENT)
    box(ax, 0.4, 1.0, bw, bh, "Posture observations",
        "posture_data.xlsx\n182 obs (RULA + QEC)", fill=ACCENT)

    # ----- Cleaning + Feature engineering -----
    box(ax, 2.7, 2.8, bw, bh, "Phase 1 — Clean",
        "normalise CSV\nvalidate")
    box(ax, 2.7, 1.0, bw, bh, "Phase 2 — Engineer",
        "encode, derive,\nseverity-rank merge")

    # ----- Stage 1 + Stage 2 -----
    box(ax, 5.0, 1.9, bw, bh, "Phase 3 — Stage 1",
        "deterministic\nLow/Med/High labels")
    box(ax, 7.3, 1.9, bw, bh, "Phase 6 — Stage 2",
        "SMOTE + GridSearchCV\n7 algos × 6 targets")

    # ----- Evaluation + Output -----
    box(ax, 9.6, 1.9, bw, bh, "Phase 7 — Evaluate",
        "CM / ROC AUC /\nfeature importance")

    # ----- Web app (rightmost) -----
    box(ax, 11.9, 1.9, 0.95, bh, "Web app",
        "Streamlit\ndemo", fill=NAVY)

    # ----- Arrows -----
    arrow(ax, 2.3, 3.4, 2.7, 3.4)        # survey -> clean
    arrow(ax, 2.3, 1.6, 2.7, 1.6)        # posture -> engineer
    arrow(ax, 4.6, 3.4, 5.0, 2.7)        # clean -> stage 1
    arrow(ax, 4.6, 1.6, 5.0, 2.3)        # engineer -> stage 1
    arrow(ax, 6.9, 2.5, 7.3, 2.5)        # stage 1 -> stage 2
    arrow(ax, 9.2, 2.5, 9.6, 2.5)        # stage 2 -> evaluate
    arrow(ax, 11.5, 2.5, 11.9, 2.5)      # evaluate -> web app

    # ----- Bottom legend strip -----
    ax.text(6.5, 0.3, "Stage 1 produces auditable risk labels using "
                      "Borg / RULA / NASA-TLX / Borg CR10 / tercile thresholds. "
                      "Stage 2 learns to recover those labels from the "
                      "remaining rider profile.",
            ha="center", va="center",
            fontsize=8.5, style="italic", color=GREY)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(OUT, dpi=200, bbox_inches="tight",
                facecolor=WHITE, edgecolor="none")
    plt.close(fig)
    return OUT


if __name__ == "__main__":
    p = build()
    print(f"saved {p.relative_to(ROOT)}")
