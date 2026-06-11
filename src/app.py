import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List

from .data_handler import DataHandler
from .scheduler import Scheduler
from .professor_manager import ProfessorManager
from .turma_manager import TurmaManager
from .sala_manager import SalaManager
from .absence_manager import AbsenceManager
from .models import Aula
from .animations import fade_page, count_up, lerp_color
from .charts import FaltaBarChart, GradeHeatmap

# ── Design tokens ──────────────────────────────────────────────────────────────
BG_PAGE     = "#F5F6FA"
BG_SIDEBAR  = "#FFFFFF"
BG_CARD     = "#FFFFFF"
ORANGE      = "#F97316"
ORANGE_DIM  = "#FFF7ED"
TEXT_DARK   = "#111827"
TEXT_MID    = "#6B7280"
TEXT_LIGHT  = "#9CA3AF"
BORDER      = "#E5E7EB"
GREEN       = "#16A34A"
GREEN_BG    = "#DCFCE7"
BLUE        = "#2563EB"
BLUE_BG     = "#DBEAFE"
RED         = "#DC2626"
RED_BG      = "#FEE2E2"
AMBER       = "#D97706"
AMBER_BG    = "#FEF3C7"
FONT        = "Segoe UI"


def _card(parent, **kwargs):
    f = tk.Frame(parent, bg=BG_CARD, **kwargs)
    f.config(highlightbackground=BORDER, highlightthickness=1, highlightcolor=BORDER)
    return f


def _btn(parent, text, cmd, primary=False, danger=False, small=False):
    if primary:
        bg, fg, abg, afg = ORANGE,   "#FFFFFF", "#EA6C0A", "#FFFFFF"
        hover_bg = "#EA6C0A"
    elif danger:
        bg, fg, abg, afg = RED,      "#FFFFFF", "#B91C1C", "#FFFFFF"
        hover_bg = "#B91C1C"
    else:
        bg, fg, abg, afg = BG_CARD,  TEXT_DARK, BG_PAGE,  TEXT_DARK
        hover_bg = BG_PAGE
    px = 12 if small else 18
    py = 5  if small else 8
    b = tk.Button(
        parent, text=text, command=cmd,
        bg=bg, fg=fg, activebackground=abg, activeforeground=afg,
        font=(FONT, 9 if small else 10), relief="flat", bd=0,
        padx=px, pady=py, cursor="hand2",
    )
    b.config(highlightbackground=BORDER, highlightthickness=1)
    # Instant hover color — smooth lerp would need root access here.
    b.bind("<Enter>", lambda _e: b.config(bg=hover_bg))
    b.bind("<Leave>", lambda _e: b.config(bg=bg))
    return b


class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OrbitSchedule")
        self.root.geometry("1180x720")
        self.root.configure(bg=BG_PAGE)
        self.root.minsize(960, 600)

        self._configure_ttk_styles()
        self.grade_gerada: List[Aula] = []

        self._build_shell()
        self._build_sidebar()
        self._build_pages()
        self.update_dashboard_summary()
        self._navigate("dashboard")

    # ── TTK global styles ──────────────────────────────────────────────────────

    def _configure_ttk_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure(".", background=BG_PAGE, foreground=TEXT_DARK, font=(FONT, 10))
        s.configure("TFrame", background=BG_PAGE)
        s.configure("TLabel", background=BG_PAGE, foreground=TEXT_DARK)
        s.configure("TEntry",
            fieldbackground=BG_CARD, background=BG_CARD,
            foreground=TEXT_DARK, insertcolor=TEXT_DARK,
            padding=8, relief="flat", borderwidth=1,
        )
        s.configure("TCombobox",
            fieldbackground=BG_CARD, background=BG_CARD,
            foreground=TEXT_DARK, padding=8,
        )
        s.configure("Treeview",
            background=BG_CARD, fieldbackground=BG_CARD,
            foreground=TEXT_DARK, rowheight=36,
            font=(FONT, 10), borderwidth=0,
        )
        s.configure("Treeview.Heading",
            background=BG_PAGE, foreground=TEXT_MID,
            font=(FONT, 9, "bold"), relief="flat", borderwidth=0,
        )
        s.map("Treeview",
            background=[("selected", ORANGE_DIM)],
            foreground=[("selected", ORANGE)],
        )
        s.configure("TSeparator", background=BORDER)
        s.configure("TScrollbar",
            background=BORDER, troughcolor=BG_PAGE,
            borderwidth=0, arrowsize=12,
        )
        s.configure("TCheckbutton", background=BG_CARD, foreground=TEXT_DARK)

    # ── Shell layout ───────────────────────────────────────────────────────────

    def _build_shell(self):
        self.sidebar_frame = tk.Frame(self.root, bg=BG_SIDEBAR, width=220)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        tk.Frame(self.root, bg=BORDER, width=1).pack(side="left", fill="y")

        right = tk.Frame(self.root, bg=BG_PAGE)
        right.pack(side="left", fill="both", expand=True)

        # Status bar at bottom of right panel
        self.status_var = tk.StringVar(value="Pronto.")
        status_bar = tk.Frame(right, bg=BG_SIDEBAR)
        status_bar.pack(side="bottom", fill="x")
        tk.Frame(status_bar, bg=BORDER, height=1).pack(fill="x")
        tk.Label(
            status_bar, textvariable=self.status_var,
            bg=BG_SIDEBAR, fg=TEXT_LIGHT,
            font=(FONT, 9), anchor="w", padx=20,
        ).pack(fill="x", pady=6)

        self.content_area = right

    # ── Sidebar ────────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        # Logo
        logo_row = tk.Frame(self.sidebar_frame, bg=BG_SIDEBAR, height=68)
        logo_row.pack(fill="x")
        logo_row.pack_propagate(False)

        logo_box = tk.Frame(logo_row, bg=ORANGE, width=34, height=34)
        logo_box.place(x=18, y=17)
        tk.Label(logo_box, text="O", bg=ORANGE, fg="#FFFFFF", font=(FONT, 13, "bold")).place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(logo_row, text="OrbitSchedule", bg=BG_SIDEBAR, fg=TEXT_DARK, font=(FONT, 11, "bold")).place(x=60, y=24)

        tk.Frame(self.sidebar_frame, bg=BORDER, height=1).pack(fill="x")

        # Nav items: (key, icon, label)
        nav_items = [
            ("dashboard",   "⊞",  "Dashboard"),
            ("professores", "👤", "Professores"),
            ("turmas",      "🎓", "Turmas"),
            ("salas",       "🏫", "Salas"),
            ("faltas",      "📋", "Faltas"),
        ]

        self._nav_btns: dict  = {}
        self._hover_jobs: dict = {}
        nav_wrap = tk.Frame(self.sidebar_frame, bg=BG_SIDEBAR)
        nav_wrap.pack(fill="x", pady=(10, 0))

        for key, icon, label in nav_items:
            row = tk.Frame(nav_wrap, bg=BG_SIDEBAR, cursor="hand2")
            row.pack(fill="x", padx=10, pady=2)

            icon_lbl = tk.Label(row, text=icon, bg=BG_SIDEBAR, fg=TEXT_MID, font=(FONT, 13), width=3)
            icon_lbl.pack(side="left", padx=(6, 0), pady=10)

            text_lbl = tk.Label(row, text=label, bg=BG_SIDEBAR, fg=TEXT_MID, font=(FONT, 10), anchor="w")
            text_lbl.pack(side="left", padx=4, pady=10, fill="x", expand=True)

            for w in (row, icon_lbl, text_lbl):
                w.bind("<Button-1>", lambda e, k=key: self._navigate(k))
                w.bind("<Enter>",    lambda e, k=key, r=row, i=icon_lbl, t=text_lbl: self._nav_hover(k, r, i, t, True))
                w.bind("<Leave>",    lambda e, k=key, r=row, i=icon_lbl, t=text_lbl: self._nav_hover(k, r, i, t, False))

            self._nav_btns[key] = (row, icon_lbl, text_lbl)

    def _nav_hover(self, key: str, row, icon, text, entering: bool):
        # Never re-style the currently active nav item.
        if row.cget("bg") == ORANGE:
            return
        target = ORANGE_DIM if entering else BG_SIDEBAR

        # Cancel any in-progress animation for this key.
        if key in self._hover_jobs:
            try:
                self.root.after_cancel(self._hover_jobs[key])
            except Exception:
                pass

        from_col  = row.cget("bg")
        MAX_STEPS = 6
        widgets   = [row, icon, text]

        def _step(step: int):
            if row.cget("bg") == ORANGE:   # became active during animation
                return
            color = lerp_color(from_col, target, step / MAX_STEPS)
            for w in widgets:
                try:
                    w.config(bg=color)
                except tk.TclError:
                    pass
            if step < MAX_STEPS:
                self._hover_jobs[key] = self.root.after(14, lambda: _step(step + 1))

        _step(1)

    def _navigate(self, page_key: str):
        def _switch():
            for key, (row, icon, text) in self._nav_btns.items():
                if key == page_key:
                    row.config(bg=ORANGE)
                    icon.config(bg=ORANGE, fg="#FFFFFF")
                    text.config(bg=ORANGE, fg="#FFFFFF")
                else:
                    row.config(bg=BG_SIDEBAR)
                    icon.config(bg=BG_SIDEBAR, fg=TEXT_MID)
                    text.config(bg=BG_SIDEBAR, fg=TEXT_MID)

            for key, page in self._pages.items():
                if key == page_key:
                    page.pack(fill="both", expand=True)
                else:
                    page.pack_forget()

        # Fade window → switch → fade back  (~280 ms total)
        fade_page(self.root, _switch)

    # ── Pages ──────────────────────────────────────────────────────────────────

    def _build_pages(self):
        self._pages: dict = {}
        self._pages["dashboard"] = self._build_dashboard()

        for key, ManagerCls, attr in [
            ("professores", ProfessorManager, "professor_manager"),
            ("turmas",      TurmaManager,     "turma_manager"),
            ("salas",       SalaManager,      "sala_manager"),
            ("faltas",      AbsenceManager,   "absence_manager"),
        ]:
            frame = tk.Frame(self.content_area, bg=BG_PAGE)
            manager = ManagerCls(frame, self)
            manager.pack(fill="both", expand=True)
            setattr(self, attr, manager)
            self._pages[key] = frame

    # ── Dashboard page ─────────────────────────────────────────────────────────

    def _build_dashboard(self) -> tk.Frame:
        page = tk.Frame(self.content_area, bg=BG_PAGE)

        canvas = tk.Canvas(page, bg=BG_PAGE, highlightthickness=0)
        vsb = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG_PAGE)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))  # noqa
        inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))

        PAD = 28

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(inner, bg=BG_PAGE)
        hdr.pack(fill="x", padx=PAD, pady=(26, 0))
        tk.Label(hdr, text="Dashboard", bg=BG_PAGE, fg=TEXT_DARK, font=(FONT, 22, "bold")).pack(anchor="w")
        tk.Label(hdr, text="Gerencie horários e visualize métricas em tempo real.", bg=BG_PAGE, fg=TEXT_MID, font=(FONT, 10)).pack(anchor="w", pady=(3, 0))

        # ── Metric cards ──────────────────────────────────────────────────────
        cards_row = tk.Frame(inner, bg=BG_PAGE)
        cards_row.pack(fill="x", padx=PAD, pady=(22, 0))

        metrics = [
            ("Professores", "0", "👤", BLUE,  BLUE_BG),
            ("Turmas",      "0", "🎓", ORANGE, ORANGE_DIM),
            ("Salas",       "0", "🏫", GREEN,  GREEN_BG),
            ("Aulas",       "0", "📋", TEXT_MID, BG_PAGE),
        ]
        self.dashboard_labels: dict = {}
        for title, val, icon, _accent, icon_bg in metrics:
            c = _card(cards_row)
            c.pack(side="left", fill="both", expand=True, padx=(0, 14))

            top = tk.Frame(c, bg=BG_CARD)
            top.pack(fill="x", padx=16, pady=(16, 6))
            tk.Label(top, text=title, bg=BG_CARD, fg=TEXT_MID, font=(FONT, 9)).pack(side="left")

            icon_box = tk.Frame(top, bg=icon_bg, width=32, height=32)
            icon_box.pack(side="right")
            icon_box.pack_propagate(False)
            tk.Label(icon_box, text=icon, bg=icon_bg, font=(FONT, 13)).place(relx=0.5, rely=0.5, anchor="center")

            val_lbl = tk.Label(c, text=val, bg=BG_CARD, fg=TEXT_DARK, font=(FONT, 26, "bold"))
            val_lbl.pack(anchor="w", padx=16, pady=(0, 18))
            self.dashboard_labels[title] = val_lbl

        # ── Action buttons ────────────────────────────────────────────────────
        actions = tk.Frame(inner, bg=BG_PAGE)
        actions.pack(fill="x", padx=PAD, pady=(22, 0))

        btns = [
            ("  Gerar Grade",    self.gerar_grade,    True,  False),
            ("  Exportar CSV",   self.exportar_grade, False, False),
            ("  Limpar Grade",   self.clear_grade,    False, False),
            ("ℹ️  Como usar",    self.show_info_main, False, False),
        ]
        for txt, cmd, prim, dng in btns:
            b = _btn(actions, txt, cmd, primary=prim, danger=dng)
            b.pack(side="left", padx=(0, 10))

        self.grade_summary_label = tk.Label(
            inner, text="Nenhuma grade gerada ainda.",
            bg=BG_PAGE, fg=TEXT_LIGHT, font=(FONT, 9),
        )
        self.grade_summary_label.pack(anchor="w", padx=PAD, pady=(8, 0))

        # ── Alerts ────────────────────────────────────────────────────────────
        alert_hdr_row = sec_hdr(inner, "Alertas e Status", PAD, top_pad=22)
        self._alert_status_lbl = tk.Label(
            alert_hdr_row, text="", bg=BG_PAGE,
            font=(FONT, 9, "bold"),
        )
        self._alert_status_lbl.pack(side="right")

        self.alert_card = _card(inner)
        self.alert_card.pack(fill="x", padx=PAD)

        # Scrollable inner frame for individual alert blocks
        _ac = tk.Canvas(self.alert_card, bg=BG_CARD, highlightthickness=0, height=170)
        _ac_vsb = ttk.Scrollbar(self.alert_card, orient="vertical", command=_ac.yview)
        _ac.configure(yscrollcommand=_ac_vsb.set)
        _ac_vsb.pack(side="right", fill="y")
        _ac.pack(fill="both", expand=True)
        self._alert_inner = tk.Frame(_ac, bg=BG_CARD)
        _aid = _ac.create_window((0, 0), window=self._alert_inner, anchor="nw")
        _ac.bind("<Configure>", lambda e: _ac.itemconfig(_aid, width=e.width))
        self._alert_inner.bind("<Configure>", lambda _e: _ac.configure(scrollregion=_ac.bbox("all")))
        self._alert_canvas = _ac
        self._alert_has_error = False

        # ── Faltas analysis charts ────────────────────────────────────────────
        sec_hdr(inner, "Análise de Faltas", PAD, top_pad=26)
        chart_card = _card(inner)
        chart_card.pack(fill="x", padx=PAD)
        self._chart_faltas = FaltaBarChart(chart_card)
        self._chart_faltas.pack(fill="both", expand=True)

        # ── Schedule presence heatmap ─────────────────────────────────────────
        sec_hdr(inner, "Grade Horária — Mapa de Presença", PAD, top_pad=20)
        heatmap_card = _card(inner)
        heatmap_card.pack(fill="x", padx=PAD)
        tk.Label(
            heatmap_card,
            text="Verde = aula com professor presente  •  Vermelho = professor ausente  •  Cinza = sem aula",
            bg=BG_CARD, fg=TEXT_LIGHT, font=(FONT, 8),
        ).pack(anchor="w", padx=16, pady=(10, 0))
        self._chart_heatmap = GradeHeatmap(heatmap_card)
        self._chart_heatmap.pack(fill="both", expand=True)

        # ── Grade table ───────────────────────────────────────────────────────
        sec_hdr(inner, "Grade Horária Gerada", PAD, top_pad=26)
        grade_card = _card(inner)
        grade_card.pack(fill="x", padx=PAD, pady=(0, 30))

        cols = [
            ("Dia", 80), ("Horário", 90), ("Bloco", 80),
            ("Turma", 110), ("Disciplina", 160), ("Professor", 160), ("Sala", 70),
        ]
        self.grade_tree = ttk.Treeview(
            grade_card,
            columns=[c for c, _ in cols],
            show="headings", selectmode="browse",
        )
        for col, w in cols:
            self.grade_tree.heading(col, text=col)
            self.grade_tree.column(col, width=w, anchor="center" if w <= 90 else "w")

        self.grade_tree.tag_configure("odd",  background=BG_CARD)
        self.grade_tree.tag_configure("even", background="#FAFAFA")
        self.grade_tree.pack(side="left", fill="both", expand=True)

        tree_vsb = ttk.Scrollbar(grade_card, orient="vertical", command=self.grade_tree.yview)
        tree_vsb.pack(side="right", fill="y")
        self.grade_tree.config(yscrollcommand=tree_vsb.set)

        return page

    # ── Helpers ────────────────────────────────────────────────────────────────

    def update_alert_text(self, message: str, append: bool = False):
        if not append:
            for w in self._alert_inner.winfo_children():
                w.destroy()
            self._alert_has_error = False
            self.alert_card.config(highlightbackground=BORDER, highlightthickness=1)
            self._alert_status_lbl.config(text="")

        for raw in message.split("\n"):
            line = raw.strip()
            if not line:
                continue
            if line.startswith("✅") or "sucesso" in line.lower() or "concluído" in line.lower():
                kind = "success"
            elif line.startswith("❌") or line.lower().startswith("erro"):
                kind = "error"
            elif line.startswith("⚠️") or line.startswith("•") or "falta" in line.lower():
                kind = "warning"
            else:
                kind = "info"

            if kind in ("error", "warning"):
                self._alert_has_error = True

            self._render_alert_block(line, kind)

        # Update card border and status badge
        if self._alert_has_error:
            self.alert_card.config(highlightbackground=RED, highlightthickness=2)
            self._alert_status_lbl.config(text="● Há problemas", fg=RED)
        else:
            self.alert_card.config(highlightbackground=GREEN, highlightthickness=1)
            if self._alert_inner.winfo_children():
                self._alert_status_lbl.config(text="● OK", fg=GREEN)

        self._alert_canvas.yview_moveto(1.0)

    def _render_alert_block(self, text: str, kind: str):
        """Render one alert line as a styled block with a left accent bar."""
        palette = {
            "success": (GREEN,    GREEN_BG),
            "error":   (RED,      RED_BG),
            "warning": (AMBER,    AMBER_BG),
            "info":    (BLUE,     BLUE_BG),
        }
        fg, bg = palette.get(kind, palette["info"])

        row = tk.Frame(self._alert_inner, bg=bg)
        row.pack(fill="x", pady=1, padx=0)

        tk.Frame(row, bg=fg, width=4).pack(side="left", fill="y")
        tk.Label(
            row, text=text,
            bg=bg, fg=TEXT_DARK if kind == "info" else fg,
            font=(FONT, 9), anchor="w",
            padx=12, pady=5, justify="left",
        ).pack(side="left", fill="x", expand=True)

    def update_dashboard_summary(self):
        if not hasattr(self, "dashboard_labels"):
            return
        counts = {
            "Professores": len(self.professor_manager.professores) if hasattr(self, "professor_manager") else 0,
            "Turmas":      len(self.turma_manager.turmas)          if hasattr(self, "turma_manager")     else 0,
            "Salas":       len(self.sala_manager.salas)            if hasattr(self, "sala_manager")      else 0,
            "Aulas":       len(self.grade_gerada),
        }
        for title, value in counts.items():
            # count_up animates from the label's current number to the new value
            count_up(self.dashboard_labels[title], value, self.root)

    def set_status(self, message: str):
        self.status_var.set(message)

    def refresh_charts(self):
        """Push updated faltas + grade data to all chart widgets."""
        faltas = getattr(self.absence_manager, "faltas", []) if hasattr(self, "absence_manager") else []
        grade  = self.grade_gerada
        if hasattr(self, "_chart_faltas"):
            self._chart_faltas.refresh(faltas, grade)
        if hasattr(self, "_chart_heatmap"):
            self._chart_heatmap.refresh(faltas, grade)
        # Also refresh the absence manager's inline chart if present.
        if hasattr(self, "absence_manager") and hasattr(self.absence_manager, "refresh_charts"):
            self.absence_manager.refresh_charts()

    # ── Actions ────────────────────────────────────────────────────────────────

    def gerar_grade(self):
        self.set_status("Gerando grade horária…")
        self.update_alert_text("Iniciando geração da grade horária…\n")
        try:
            professores = self.professor_manager.professores
            turmas      = self.turma_manager.turmas
            salas       = self.sala_manager.salas

            if not professores or not turmas or not salas:
                messagebox.showwarning("Aviso", "Certifique-se de ter Professores, Turmas e Salas cadastrados.")
                self.update_alert_text("⚠️  Dados insuficientes para gerar a grade.\n", append=True)
                return

            scheduler = Scheduler(professores, turmas, salas)
            self.grade_gerada = scheduler.gerar_grade()
            alertas = scheduler.get_alertas()

            for i in self.grade_tree.get_children():
                self.grade_tree.delete(i)

            if self.grade_gerada:
                for idx, aula in enumerate(self.grade_gerada):
                    tag = "even" if idx % 2 == 0 else "odd"
                    self.grade_tree.insert("", "end", values=(
                        aula.dia, f"{aula.horario}º Horário", aula.bloco,
                        aula.turma, aula.disciplina, aula.professor, aula.sala,
                    ), tags=(tag,))
                self.update_alert_text("✅  Grade gerada com sucesso!\n", append=True)
                self.grade_summary_label.config(text=f"{len(self.grade_gerada)} aulas geradas.")
                self.set_status(f"Grade gerada: {len(self.grade_gerada)} aulas alocadas.")
            else:
                self.update_alert_text("⚠️  Nenhuma aula gerada. Verifique os dados.\n", append=True)
                self.grade_summary_label.config(text="Nenhuma aula gerada.")
                self.set_status("Não foi possível gerar a grade.")

            self.update_dashboard_summary()
            self.refresh_charts()

            if alertas:
                self.update_alert_text("\n⚠️  Problemas encontrados:\n\n", append=True)
                for a in alertas:
                    self.update_alert_text(f"  • {a}\n", append=True)
            else:
                self.update_alert_text("\n✅  Nenhum conflito de alocação encontrado.\n", append=True)

        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Erro ao gerar a grade:\n{e}")
            self.update_alert_text(f"❌  Erro: {e}\n", append=True)

    def exportar_grade(self):
        if not self.grade_gerada:
            messagebox.showwarning("Aviso", "Nenhuma grade foi gerada para exportar.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Salvar Grade Horária",
            initialfile="grade_horaria.csv",
        )
        if path:
            try:
                DataHandler.save_grade(path, self.grade_gerada)
                messagebox.showinfo("Exportação concluída", f"Grade salva em:\n{path}")
            except Exception as e:
                messagebox.showerror("Erro de exportação", f"Erro ao salvar:\n{e}")

    def clear_grade(self):
        self.grade_gerada = []
        for i in self.grade_tree.get_children():
            self.grade_tree.delete(i)
        self.grade_summary_label.config(text="Nenhuma aula gerada.")
        self.update_dashboard_summary()
        self.refresh_charts()
        self.set_status("Grade limpa.")
        self.update_alert_text("Grade limpa.\n")

    def show_info_main(self):
        messagebox.showinfo("Como usar", (
            "1. Cadastre Professores, Turmas e Salas nas páginas laterais.\n"
            "2. Confirme que as disciplinas dos professores batem com as das turmas.\n"
            "3. Clique em 'Gerar Grade'.\n"
            "4. Verifique alertas e exporte em CSV se necessário."
        ))


# ── Utility ────────────────────────────────────────────────────────────────────

def sec_hdr(parent, text: str, pad: int, top_pad: int = 16):
    row = tk.Frame(parent, bg=BG_PAGE)
    row.pack(fill="x", padx=pad, pady=(top_pad, 8))
    tk.Label(row, text=text, bg=BG_PAGE, fg=TEXT_DARK, font=(FONT, 11, "bold")).pack(side="left")
    return row


if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()
