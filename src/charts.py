"""
Chart widgets for OrbitSchedule.

FaltaBarChart  — two matplotlib bar charts (Faltas por Turma / por Matéria).
                 Falls back to a placeholder label if matplotlib is not installed.

GradeHeatmap   — tk.Canvas schedule grid showing slot presence/absence.
                 Pure Tkinter, no external dependencies.
"""
import tkinter as tk
from typing import List, Dict

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    _HAS_MPL = True
except ImportError:
    _HAS_MPL = False

from .models import Falta, Aula

# Maps abbreviated weekday (stored in Falta.dia_semana) to the full name used in Aula.dia.
_ABBR_TO_FULL: Dict[str, str] = {
    "Seg": "Segunda", "Ter": "Terça", "Qua": "Quarta",
    "Qui": "Quinta",  "Sex": "Sexta",
}

# ── Design tokens ──────────────────────────────────────────────────────────────
BG_CARD   = "#FFFFFF"
BG_PAGE   = "#F5F6FA"
BORDER    = "#E5E7EB"
ORANGE    = "#F97316"
RED       = "#DC2626"
RED_BG    = "#FEE2E2"
GREEN     = "#16A34A"
GREEN_BG  = "#DCFCE7"
TEXT_MID  = "#6B7280"
TEXT_DRK  = "#111827"
FONT      = "Segoe UI"


# ── Bar charts (matplotlib) ────────────────────────────────────────────────────

class FaltaBarChart(tk.Frame):
    """
    Two side-by-side bar charts embedded in a Tkinter frame via FigureCanvasTkAgg.
      Left  — Faltas por Turma   (aulas sem cobertura agrupadas por turma)
      Right — Faltas por Matéria (agrupadas por disciplina)

    Call .refresh(faltas, grade) to update with new data.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=BG_CARD)

        if not _HAS_MPL:
            tk.Label(
                self,
                text="Instale matplotlib para exibir os gráficos:  pip install matplotlib",
                bg=BG_CARD, fg=TEXT_MID, font=(FONT, 10),
            ).pack(expand=True, pady=30)
            return

        self._fig = Figure(figsize=(8.5, 3.0), dpi=96, facecolor=BG_CARD)
        self._fig.subplots_adjust(
            left=0.06, right=0.98, top=0.82, bottom=0.22, wspace=0.38
        )
        self._ax_t = self._fig.add_subplot(1, 2, 1)  # Turma
        self._ax_m = self._fig.add_subplot(1, 2, 2)  # Matéria

        self._mpl = FigureCanvasTkAgg(self._fig, master=self)
        self._mpl.get_tk_widget().pack(fill="both", expand=True)

        self._draw_empty()

    # ── internal helpers ───────────────────────────────────────────────────────

    def _style(self, ax, title: str):
        ax.set_facecolor(BG_CARD)
        ax.set_title(title, fontsize=9, color=TEXT_MID, pad=6, loc="left")
        ax.tick_params(axis="both", colors=TEXT_MID, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER)
        ax.yaxis.grid(True, color=BORDER, linewidth=0.6, zorder=0)
        ax.set_axisbelow(True)

    def _update_fig_bg(self):
        """Sync matplotlib figure/canvas background with the current BG_CARD token."""
        self._fig.set_facecolor(BG_CARD)
        self._mpl.get_tk_widget().config(bg=BG_CARD)

    def _draw_empty(self):
        self._update_fig_bg()
        for ax, title in [
            (self._ax_t, "Faltas por Turma"),
            (self._ax_m, "Faltas por Matéria"),
        ]:
            ax.clear()
            self._style(ax, title)
            ax.text(
                0.5, 0.5, "Sem dados — registre faltas para visualizar.",
                ha="center", va="center",
                transform=ax.transAxes, color=TEXT_MID, fontsize=9,
            )
        self._mpl.draw()

    def _bar(self, ax, data: dict, title: str, color: str):
        ax.clear()
        self._style(ax, title)
        if not data:
            ax.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                    transform=ax.transAxes, color=TEXT_MID, fontsize=9)
            return
        labels = list(data.keys())
        values = list(data.values())
        bars = ax.bar(labels, values, color=color, zorder=3, width=0.52,
                      edgecolor="none")
        ax.bar_label(bars, fmt="%d", label_type="edge", fontsize=8,
                     color=TEXT_MID, padding=3)
        ax.set_ylim(0, max(values) * 1.42)
        if len(labels) > 4:
            ax.set_xticklabels(labels, rotation=28, ha="right")

    # ── public API ─────────────────────────────────────────────────────────────

    def refresh(self, faltas: List[Falta], grade: List[Aula]):
        """Recompute bar charts from the given absence list and generated grade."""
        if not _HAS_MPL:
            return
        if not faltas or not grade:
            self._draw_empty()
            return

        # CORREÇÃO BUG 1: usa (professor, dia_completo) em vez de apenas professor.
        # Assim só contamos as aulas do dia exato da falta, não todas as aulas do
        # professor na semana, o que gerava contagens infladas e "aleatórias".
        absent_slots: set = set()
        for f in faltas:
            full_day = _ABBR_TO_FULL.get(f.dia_semana, f.dia_semana)
            absent_slots.add((f.professor, full_day))

        turma_cnt:   Dict[str, int] = {}
        materia_cnt: Dict[str, int] = {}
        for aula in grade:
            if (aula.professor, aula.dia) in absent_slots:
                turma_cnt[aula.turma]        = turma_cnt.get(aula.turma, 0) + 1
                materia_cnt[aula.disciplina] = materia_cnt.get(aula.disciplina, 0) + 1

        self._update_fig_bg()
        self._bar(self._ax_t, turma_cnt,   "Faltas por Turma",    RED)
        self._bar(self._ax_m, materia_cnt, "Faltas por Matéria",  ORANGE)
        self._mpl.draw()


# ── Schedule heatmap (pure Tkinter Canvas) ─────────────────────────────────────

class GradeHeatmap(tk.Frame):
    """
    Canvas-drawn schedule grid: columns = weekdays, rows = class periods.

    Cell color legend:
      Red   (#FEE2E2) — slot has a class but professor is absent
      Green (#F0FDF4) — slot occupied, professor present
      Grey  (#F9FAFB) — no class scheduled for that slot

    Call .refresh(faltas, grade) to update.
    """

    DAYS    = ["Seg", "Ter", "Qua", "Qui", "Sex"]
    PERIODS = [1, 2, 3, 4, 5, 6]
    _DAY_MAP = {
        "Segunda": "Seg", "Terça": "Ter", "Quarta": "Qua",
        "Quinta":  "Qui", "Sexta": "Sex",
    }

    def __init__(self, parent):
        super().__init__(parent, bg=BG_CARD)
        self._canvas = tk.Canvas(
            self, bg=BG_CARD, highlightthickness=0, height=185,
        )
        self._canvas.pack(fill="both", expand=True, padx=16, pady=(8, 14))
        self._canvas.bind("<Configure>", lambda _e: self._redraw())
        self._grid: Dict[str, Dict[int, str]] = {}

    # ── public API ─────────────────────────────────────────────────────────────

    def refresh(self, faltas: List[Falta], grade: List[Aula]):
        """Rebuild grid data and redraw."""
        # CORREÇÃO BUG 1 (heatmap): mesma lógica do FaltaBarChart — filtra por
        # (professor, dia_completo) para só colorir a célula do dia real da falta.
        absent_slots: set = set()
        for f in faltas:
            full_day = _ABBR_TO_FULL.get(f.dia_semana, f.dia_semana)
            absent_slots.add((f.professor, full_day))

        self._grid = {d: {} for d in self.DAYS}
        for aula in grade:
            day = self._DAY_MAP.get(aula.dia, aula.dia[:3])
            if day not in self._grid:
                continue
            if (aula.professor, aula.dia) in absent_slots:
                self._grid[day][aula.horario] = "absent"
            elif self._grid[day].get(aula.horario) != "absent":
                self._grid[day][aula.horario] = "ok"

        self._redraw()

    # ── drawing ────────────────────────────────────────────────────────────────

    def _redraw(self):
        self._canvas.delete("all")
        self._canvas.config(bg=BG_CARD)
        w = self._canvas.winfo_width()
        h = self._canvas.winfo_height()
        if w < 20 or h < 20:
            return

        cols = len(self.DAYS) + 1      # +1 for row-header column
        rows = len(self.PERIODS) + 1   # +1 for column-header row
        cw   = w / cols
        rh   = h / rows

        # Lê módulo globals a cada redraw — assim picks up dark/light após o toggle.
        header_bg = BG_PAGE
        absent_bg, absent_fg = RED_BG,   RED
        ok_bg,     ok_fg     = GREEN_BG, GREEN
        free_bg,   free_fg   = BG_CARD,  TEXT_MID

        # Column headers (days)
        for ci, day in enumerate(self.DAYS, 1):
            x0 = ci * cw
            self._canvas.create_rectangle(x0, 0, x0 + cw, rh, fill=header_bg, outline=BORDER)
            self._canvas.create_text(
                x0 + cw / 2, rh / 2,
                text=day, font=("Segoe UI", 8, "bold"), fill=TEXT_MID,
            )

        # Row headers (periods)
        for ri, period in enumerate(self.PERIODS, 1):
            y0 = ri * rh
            self._canvas.create_rectangle(0, y0, cw, y0 + rh, fill=header_bg, outline=BORDER)
            self._canvas.create_text(
                cw / 2, y0 + rh / 2,
                text=f"{period}°", font=("Segoe UI", 8), fill=TEXT_MID,
            )

        # Top-left corner cell
        self._canvas.create_rectangle(0, 0, cw, rh, fill=header_bg, outline=BORDER)
        self._canvas.create_text(
            cw / 2, rh / 2, text="H \\ Dia",
            font=("Segoe UI", 7), fill=TEXT_MID,
        )

        # Data cells
        for ci, day in enumerate(self.DAYS, 1):
            for ri, period in enumerate(self.PERIODS, 1):
                status = self._grid.get(day, {}).get(period, "free")
                if status == "absent":
                    fill, label, fg = absent_bg, "FALTA", absent_fg
                elif status == "ok":
                    fill, label, fg = ok_bg, "✓", ok_fg
                else:
                    fill, label, fg = free_bg, "—", free_fg

                x0, y0 = ci * cw, ri * rh
                self._canvas.create_rectangle(
                    x0, y0, x0 + cw, y0 + rh,
                    fill=fill, outline=BORDER,
                )
                self._canvas.create_text(
                    x0 + cw / 2, y0 + rh / 2,
                    text=label, font=("Segoe UI", 8), fill=fg,
                )
