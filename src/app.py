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
FONT        = "Segoe UI"


def _card(parent, **kwargs):
    f = tk.Frame(parent, bg=BG_CARD, **kwargs)
    f.config(highlightbackground=BORDER, highlightthickness=1, highlightcolor=BORDER)
    return f


def _btn(parent, text, cmd, primary=False, danger=False, small=False):
    if primary:
        bg, fg, abg, afg = ORANGE, "#FFFFFF", "#EA6C0A", "#FFFFFF"
    elif danger:
        bg, fg, abg, afg = RED, "#FFFFFF", "#B91C1C", "#FFFFFF"
    else:
        bg, fg, abg, afg = BG_CARD, TEXT_DARK, BG_PAGE, TEXT_DARK
    px = 12 if small else 18
    py = 5 if small else 8
    b = tk.Button(
        parent, text=text, command=cmd,
        bg=bg, fg=fg, activebackground=abg, activeforeground=afg,
        font=(FONT, 9 if small else 10), relief="flat", bd=0,
        padx=px, pady=py, cursor="hand2",
    )
    b.config(highlightbackground=BORDER, highlightthickness=1)
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

        self._nav_btns: dict = {}
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
                w.bind("<Enter>",    lambda e, r=row, i=icon_lbl, t=text_lbl: self._nav_hover(r, i, t, True))
                w.bind("<Leave>",    lambda e, r=row, i=icon_lbl, t=text_lbl: self._nav_hover(r, i, t, False))

            self._nav_btns[key] = (row, icon_lbl, text_lbl)

    def _nav_hover(self, row, icon, text, entering):
        if row.cget("bg") == ORANGE:
            return
        col = ORANGE_DIM if entering else BG_SIDEBAR
        row.config(bg=col)
        icon.config(bg=col)
        text.config(bg=col)

    def _navigate(self, page_key: str):
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
        sec_hdr(inner, "Alertas e Status", PAD, top_pad=22)
        alert_card = _card(inner)
        alert_card.pack(fill="x", padx=PAD)
        self.alert_text = tk.Text(
            alert_card, height=5,
            font=("Consolas", 9), relief="flat",
            bg=BG_CARD, fg=TEXT_DARK, bd=0,
            padx=14, pady=12, insertbackground=TEXT_DARK,
        )
        self.alert_text.pack(fill="both", expand=True)
        self.alert_text.config(state=tk.DISABLED)

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
        self.alert_text.config(state=tk.NORMAL)
        if not append:
            self.alert_text.delete(1.0, tk.END)
        self.alert_text.insert(tk.END, message)
        self.alert_text.config(state=tk.DISABLED)
        self.alert_text.see(tk.END)

    def update_dashboard_summary(self):
        if not hasattr(self, "dashboard_labels"):
            return
        self.dashboard_labels["Professores"].config(
            text=str(len(self.professor_manager.professores) if hasattr(self, "professor_manager") else 0)
        )
        self.dashboard_labels["Turmas"].config(
            text=str(len(self.turma_manager.turmas) if hasattr(self, "turma_manager") else 0)
        )
        self.dashboard_labels["Salas"].config(
            text=str(len(self.sala_manager.salas) if hasattr(self, "sala_manager") else 0)
        )
        self.dashboard_labels["Aulas"].config(
            text=str(len(self.grade_gerada))
        )

    def set_status(self, message: str):
        self.status_var.set(message)

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
