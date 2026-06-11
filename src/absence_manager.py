import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
import os

from .models import Falta, Aula
from .data_handler import DataHandler

# ── Design tokens ──────────────────────────────────────────────────────────────
BG_PAGE    = "#F5F6FA"
BG_CARD    = "#FFFFFF"
ORANGE     = "#F97316"
ORANGE_DIM = "#FFF7ED"
TEXT_DARK  = "#111827"
TEXT_MID   = "#6B7280"
TEXT_LIGHT = "#9CA3AF"
BORDER     = "#E5E7EB"
GREEN      = "#16A34A"
GREEN_BG   = "#DCFCE7"
RED        = "#DC2626"
RED_BG     = "#FEE2E2"
AMBER      = "#D97706"
AMBER_BG   = "#FEF3C7"
FONT       = "Segoe UI"


def _card(parent, **kwargs):
    f = tk.Frame(parent, bg=BG_CARD, **kwargs)
    f.config(highlightbackground=BORDER, highlightthickness=1, highlightcolor=BORDER)
    return f


def _btn(parent, text, cmd, primary=False, danger=False, success=False):
    if primary:
        bg, fg, abg = ORANGE, "#FFFFFF", "#EA6C0A"
    elif danger:
        bg, fg, abg = RED, "#FFFFFF", "#B91C1C"
    elif success:
        bg, fg, abg = GREEN, "#FFFFFF", "#15803D"
    else:
        bg, fg, abg = BG_PAGE, TEXT_DARK, BORDER
    b = tk.Button(
        parent, text=text, command=cmd,
        bg=bg, fg=fg, activebackground=abg,
        activeforeground="#FFFFFF" if (primary or danger or success) else TEXT_DARK,
        font=(FONT, 10), relief="flat", bd=0,
        padx=14, pady=7, cursor="hand2",
    )
    if not primary and not danger and not success:
        b.config(highlightbackground=BORDER, highlightthickness=1)
    return b


def _sec(parent, text: str, pad: int, top_pad: int = 16):
    row = tk.Frame(parent, bg=BG_PAGE)
    row.pack(fill="x", padx=pad, pady=(top_pad, 8))
    tk.Label(row, text=text, bg=BG_PAGE, fg=TEXT_DARK, font=(FONT, 11, "bold")).pack(side="left")
    return row


class AbsenceManager(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_PAGE)
        self.controller = controller
        self.faltas: List[Falta] = []
        self.file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "faltas.csv")
        )
        self._build_ui()
        self._load()

    # ── Persistence ────────────────────────────────────────────────────────────

    def _load(self):
        self.faltas = DataHandler.load_faltas(self.file_path)
        self._refresh_faltas_tree()
        self._update_dashboard()

    def _save(self):
        DataHandler.save_faltas(self.file_path, self.faltas)

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        PAD = 28

        # Scrollable container
        canvas = tk.Canvas(self, bg=BG_PAGE, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG_PAGE)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))  # noqa
        inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))

        # ── Page header ───────────────────────────────────────────────────────
        hdr = tk.Frame(inner, bg=BG_PAGE)
        hdr.pack(fill="x", padx=PAD, pady=(26, 0))
        tk.Label(hdr, text="Gestão de Faltas", bg=BG_PAGE, fg=TEXT_DARK, font=(FONT, 22, "bold")).pack(anchor="w")
        tk.Label(
            hdr,
            text="Registre ausências, valide a grade e exporte relatórios para a Secretaria.",
            bg=BG_PAGE, fg=TEXT_MID, font=(FONT, 10),
        ).pack(anchor="w", pady=(3, 0))

        # ── Dashboard cards ───────────────────────────────────────────────────
        cards_row = tk.Frame(inner, bg=BG_PAGE)
        cards_row.pack(fill="x", padx=PAD, pady=(22, 0))

        self._dash: Dict[str, tk.Label] = {}
        dash_defs = [
            ("Faltas Hoje",      "0", "📅", RED_BG),
            ("Faltas na Semana", "0", "📊", AMBER_BG),
            ("Prof. Ausentes",   "0", "👤", RED_BG),
            ("Aulas Afetadas",   "0", "📋", ORANGE_DIM),
        ]
        for title, val, icon, icon_bg in dash_defs:
            c = _card(cards_row)
            c.pack(side="left", fill="both", expand=True, padx=(0, 14))
            top_row = tk.Frame(c, bg=BG_CARD)
            top_row.pack(fill="x", padx=16, pady=(16, 6))
            tk.Label(top_row, text=title, bg=BG_CARD, fg=TEXT_MID, font=(FONT, 9)).pack(side="left")
            ib = tk.Frame(top_row, bg=icon_bg, width=32, height=32)
            ib.pack(side="right")
            ib.pack_propagate(False)
            tk.Label(ib, text=icon, bg=icon_bg, font=(FONT, 13)).place(relx=0.5, rely=0.5, anchor="center")
            vl = tk.Label(c, text=val, bg=BG_CARD, fg=TEXT_DARK, font=(FONT, 26, "bold"))
            vl.pack(anchor="w", padx=16, pady=(0, 18))
            self._dash[title] = vl

        # ── Status banner ─────────────────────────────────────────────────────
        self._banner_frame = tk.Frame(inner, bg=GREEN_BG)
        self._banner_frame.config(highlightbackground=GREEN, highlightthickness=1)
        self._banner_frame.pack(fill="x", padx=PAD, pady=(18, 0))
        self._banner_lbl = tk.Label(
            self._banner_frame,
            text="✅  Está tudo certo — nenhuma falta registrada hoje.",
            bg=GREEN_BG, fg=GREEN, font=(FONT, 10, "bold"),
            padx=16, pady=12, anchor="w",
        )
        self._banner_lbl.pack(fill="x")

        # ── Register absence form ─────────────────────────────────────────────
        _sec(inner, "Registrar Falta", PAD, top_pad=26)
        form = _card(inner)
        form.pack(fill="x", padx=PAD)

        grid = tk.Frame(form, bg=BG_CARD)
        grid.pack(fill="x", padx=20, pady=(18, 8))
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(3, weight=1)

        # Row 0: date + professor
        tk.Label(grid, text="Data (DD/MM/AAAA):", bg=BG_CARD, fg=TEXT_MID, font=(FONT, 9)).grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        self.data_entry = tk.Entry(
            grid, font=(FONT, 10), bg=BG_PAGE, fg=TEXT_DARK,
            relief="flat", bd=0, width=16,
            highlightbackground=BORDER, highlightthickness=1,
            insertbackground=TEXT_DARK,
        )
        self.data_entry.insert(0, date.today().strftime("%d/%m/%Y"))
        self.data_entry.grid(row=0, column=1, sticky="w", padx=(12, 30), pady=(0, 10), ipady=6)

        tk.Label(grid, text="Professor:", bg=BG_CARD, fg=TEXT_MID, font=(FONT, 9)).grid(
            row=0, column=2, sticky="w", pady=(0, 10))
        self.professor_cb = ttk.Combobox(grid, width=32, state="readonly", font=(FONT, 10))
        self.professor_cb.grid(row=0, column=3, sticky="ew", padx=(12, 0), pady=(0, 10), ipady=4)

        # Row 1: motivo
        tk.Label(grid, text="Motivo (opcional):", bg=BG_CARD, fg=TEXT_MID, font=(FONT, 9)).grid(
            row=1, column=0, sticky="w", pady=(0, 4))
        self.motivo_entry = tk.Entry(
            grid, font=(FONT, 10), bg=BG_PAGE, fg=TEXT_DARK,
            relief="flat", bd=0, width=70,
            highlightbackground=BORDER, highlightthickness=1,
            insertbackground=TEXT_DARK,
        )
        self.motivo_entry.grid(row=1, column=1, columnspan=3, sticky="ew", padx=(12, 0), pady=(0, 4), ipady=6)

        btn_row = tk.Frame(form, bg=BG_CARD)
        btn_row.pack(fill="x", padx=20, pady=(8, 18))
        _btn(btn_row, "Registrar Falta", self._registrar_falta, danger=True).pack(side="left", padx=(0, 10))
        _btn(btn_row, "↺  Atualizar professores", self._refresh_professor_list).pack(side="left")

        # ── Validation report ─────────────────────────────────────────────────
        rep_hdr_row = tk.Frame(inner, bg=BG_PAGE)
        rep_hdr_row.pack(fill="x", padx=PAD, pady=(28, 0))
        lft = tk.Frame(rep_hdr_row, bg=BG_PAGE)
        lft.pack(side="left", fill="x", expand=True)
        tk.Label(lft, text="Relatório de Validação da Grade", bg=BG_PAGE, fg=TEXT_DARK, font=(FONT, 11, "bold")).pack(anchor="w")
        tk.Label(
            lft,
            text="Aulas com professor ausente aparecem destacadas em vermelho.",
            bg=BG_PAGE, fg=TEXT_MID, font=(FONT, 9),
        ).pack(anchor="w", pady=(2, 0))

        rgt = tk.Frame(rep_hdr_row, bg=BG_PAGE)
        rgt.pack(side="right")
        tk.Label(rgt, text="Data:", bg=BG_PAGE, fg=TEXT_MID, font=(FONT, 9)).pack(side="left", padx=(0, 8))
        self.filter_entry = tk.Entry(
            rgt, font=(FONT, 10), bg=BG_CARD, fg=TEXT_DARK,
            relief="flat", bd=0, width=13,
            highlightbackground=BORDER, highlightthickness=1,
            insertbackground=TEXT_DARK,
        )
        self.filter_entry.insert(0, date.today().strftime("%d/%m/%Y"))
        self.filter_entry.pack(side="left", ipady=5)
        _btn(rgt, "Visualizar", self._refresh_report, primary=True).pack(side="left", padx=(8, 0))

        rep_card = _card(inner)
        rep_card.pack(fill="x", padx=PAD, pady=(10, 0))

        rep_cols = [
            ("Dia", 58), ("Horário", 75), ("Bloco", 68), ("Turma", 90),
            ("Disciplina", 145), ("Professor", 145), ("Sala", 58), ("Status", 110),
        ]
        self.report_tree = ttk.Treeview(
            rep_card,
            columns=[c for c, _ in rep_cols],
            show="headings", selectmode="browse", height=10,
        )
        for col, w in rep_cols:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=w, anchor="center" if w <= 80 else "w")

        self.report_tree.tag_configure("present", background=GREEN_BG, foreground=GREEN)
        self.report_tree.tag_configure("absent",  background=RED_BG,   foreground=RED)
        self.report_tree.tag_configure("unknown", background=BG_CARD,  foreground=TEXT_MID)

        self.report_tree.pack(side="left", fill="both", expand=True)
        rep_vsb = ttk.Scrollbar(rep_card, orient="vertical", command=self.report_tree.yview)
        rep_vsb.pack(side="right", fill="y")
        self.report_tree.config(yscrollcommand=rep_vsb.set)

        # ── Registered absences ───────────────────────────────────────────────
        _sec(inner, "Faltas Registradas", PAD, top_pad=28)

        falta_card = _card(inner)
        falta_card.pack(fill="x", padx=PAD)

        falta_cols = [
            ("Data", 90), ("Professor", 150), ("Dia", 55),
            ("Bloco", 68), ("Motivo", 200), ("Registrado em", 140),
        ]
        self.faltas_tree = ttk.Treeview(
            falta_card,
            columns=[c for c, _ in falta_cols],
            show="headings", selectmode="browse", height=7,
        )
        for col, w in falta_cols:
            self.faltas_tree.heading(col, text=col)
            self.faltas_tree.column(col, width=w)

        self.faltas_tree.tag_configure("falta", background=RED_BG, foreground=RED)

        self.faltas_tree.pack(side="left", fill="both", expand=True)
        f_vsb = ttk.Scrollbar(falta_card, orient="vertical", command=self.faltas_tree.yview)
        f_vsb.pack(side="right", fill="y")
        self.faltas_tree.config(yscrollcommand=f_vsb.set)

        del_row = tk.Frame(inner, bg=BG_PAGE)
        del_row.pack(fill="x", padx=PAD, pady=(10, 0))
        _btn(del_row, "Remover Falta Selecionada", self._delete_falta, danger=True).pack(side="left")

        # ── Export ────────────────────────────────────────────────────────────
        _sec(inner, "Exportar para Secretaria", PAD, top_pad=28)
        exp_card = _card(inner)
        exp_card.pack(fill="x", padx=PAD, pady=(0, 30))

        exp_inner = tk.Frame(exp_card, bg=BG_CARD)
        exp_inner.pack(fill="x", padx=20, pady=20)

        tk.Label(
            exp_inner,
            text="Gere arquivos CSV estruturados e prontos para envio à Secretaria.",
            bg=BG_CARD, fg=TEXT_MID, font=(FONT, 10),
        ).pack(anchor="w", pady=(0, 14))

        exp_btns = tk.Frame(exp_inner, bg=BG_CARD)
        exp_btns.pack(anchor="w")

        _btn(exp_btns, "📥  Relatório de Faltas (CSV)",
             self._export_faltas_csv, success=True).pack(side="left", padx=(0, 12))
        _btn(exp_btns, "📥  Grade Validada com Status (CSV)",
             self._export_grade_csv).pack(side="left")

        # Init
        self._refresh_professor_list()
        self._refresh_report()

    # ── Professor list ─────────────────────────────────────────────────────────

    def _refresh_professor_list(self):
        profs = (
            [p.nome for p in self.controller.professor_manager.professores]
            if hasattr(self.controller, "professor_manager")
            else []
        )
        self.professor_cb["values"] = profs
        if profs:
            self.professor_cb.current(0)

    # ── Date helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _parse_date(s: str) -> Optional[date]:
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None

    def _week_range(self):
        today = date.today()
        start = today - timedelta(days=today.weekday())
        return start, start + timedelta(days=6)

    # ── Dashboard ──────────────────────────────────────────────────────────────

    def _update_dashboard(self):
        today_str = date.today().strftime("%d/%m/%Y")
        wstart, wend = self._week_range()

        today_faltas  = [f for f in self.faltas if f.data == today_str]
        week_faltas   = [
            f for f in self.faltas
            if (d := self._parse_date(f.data)) and wstart <= d <= wend
        ]
        absent_today  = {f.professor for f in today_faltas}

        grade: List[Aula] = getattr(self.controller, "grade_gerada", [])
        affected = sum(1 for a in grade if a.professor in absent_today)

        self._dash["Faltas Hoje"].config(text=str(len(today_faltas)))
        self._dash["Faltas na Semana"].config(text=str(len(week_faltas)))
        self._dash["Prof. Ausentes"].config(text=str(len(absent_today)))
        self._dash["Aulas Afetadas"].config(text=str(affected))

        if today_faltas:
            self._banner_frame.config(bg=RED_BG, highlightbackground=RED)
            self._banner_lbl.config(
                bg=RED_BG, fg=RED,
                text=(
                    f"⚠️  {len(today_faltas)} falta(s) hoje — "
                    f"{len(absent_today)} professor(es) ausente(s), "
                    f"{affected} aula(s) sem cobertura."
                ),
            )
        else:
            self._banner_frame.config(bg=GREEN_BG, highlightbackground=GREEN)
            self._banner_lbl.config(
                bg=GREEN_BG, fg=GREEN,
                text="✅  Está tudo certo — nenhuma falta registrada hoje.",
            )

    # ── Validation report ──────────────────────────────────────────────────────

    def _refresh_report(self):
        self.report_tree.delete(*self.report_tree.get_children())
        grade: List[Aula] = getattr(self.controller, "grade_gerada", [])

        if not grade:
            self.report_tree.insert("", "end", values=(
                "—", "—", "—", "—", "—",
                "Gere a grade na aba Dashboard primeiro.", "—", "—",
            ), tags=("unknown",))
            return

        filter_str  = self.filter_entry.get().strip()
        filter_date = self._parse_date(filter_str)
        absent_profs = (
            {f.professor for f in self.faltas if f.data == filter_date.strftime("%d/%m/%Y")}
            if filter_date else set()
        )

        gap_count = 0
        for aula in grade:
            if aula.professor in absent_profs:
                tag    = "absent"
                status = "⚠️ FALTA"
                gap_count += 1
            elif filter_date:
                tag    = "present"
                status = "✅ Presente"
            else:
                tag    = "unknown"
                status = "—"

            self.report_tree.insert("", "end", values=(
                aula.dia, f"{aula.horario}º", aula.bloco,
                aula.turma, aula.disciplina, aula.professor, aula.sala, status,
            ), tags=(tag,))

        # Update banner text to reflect report filter
        if filter_date and gap_count == 0:
            self._banner_frame.config(bg=GREEN_BG, highlightbackground=GREEN)
            self._banner_lbl.config(
                bg=GREEN_BG, fg=GREEN,
                text=f"✅  Está tudo certo — nenhuma falta em {filter_str}.",
            )
        elif filter_date and gap_count > 0:
            self._banner_frame.config(bg=RED_BG, highlightbackground=RED)
            self._banner_lbl.config(
                bg=RED_BG, fg=RED,
                text=(
                    f"⚠️  {gap_count} aula(s) sem cobertura em {filter_str} "
                    f"— linhas em vermelho indicam os horários vagos."
                ),
            )

    # ── Faltas treeview ────────────────────────────────────────────────────────

    def _refresh_faltas_tree(self):
        self.faltas_tree.delete(*self.faltas_tree.get_children())
        for f in sorted(self.faltas, key=lambda x: x.data, reverse=True):
            self.faltas_tree.insert("", "end", values=(
                f.data, f.professor, f.dia_semana,
                f.bloco, f.motivo, f.registrado_em,
            ), tags=("falta",))

    # ── CRUD ───────────────────────────────────────────────────────────────────

    def _registrar_falta(self):
        data_str  = self.data_entry.get().strip()
        professor = self.professor_cb.get().strip()
        motivo    = self.motivo_entry.get().strip()

        if not data_str or not professor:
            messagebox.showwarning("Aviso", "Data e Professor são obrigatórios.")
            return
        parsed = self._parse_date(data_str)
        if not parsed:
            messagebox.showwarning("Aviso", "Data inválida. Use o formato DD/MM/AAAA.")
            return
        if any(f.data == data_str and f.professor == professor for f in self.faltas):
            messagebox.showwarning("Aviso", f"Falta de '{professor}' em {data_str} já registrada.")
            return

        weekday_abbr = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        dia_semana = weekday_abbr[parsed.weekday()]

        grade: List[Aula] = getattr(self.controller, "grade_gerada", [])
        aulas_prof = [a for a in grade if a.professor == professor]
        bloco   = aulas_prof[0].bloco    if aulas_prof else "—"
        horario = str(aulas_prof[0].horario) if aulas_prof else "—"

        self.faltas.append(Falta(
            data=data_str,
            professor=professor,
            dia_semana=dia_semana,
            bloco=bloco,
            horario=horario,
            motivo=motivo or "Não informado",
            registrado_em=datetime.now().strftime("%d/%m/%Y %H:%M"),
        ))
        self._save()
        self._refresh_faltas_tree()
        self._refresh_report()
        self._update_dashboard()
        self.motivo_entry.delete(0, tk.END)
        messagebox.showinfo("Registrado", f"Falta de '{professor}' em {data_str} registrada.")

    def _delete_falta(self):
        item = self.faltas_tree.focus()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma falta para remover.")
            return
        v = self.faltas_tree.item(item, "values")
        data_v, prof_v = v[0], v[1]
        if messagebox.askyesno("Confirmar", f"Remover falta de '{prof_v}' em {data_v}?"):
            self.faltas = [f for f in self.faltas if not (f.data == data_v and f.professor == prof_v)]
            self._save()
            self._refresh_faltas_tree()
            self._refresh_report()
            self._update_dashboard()

    # ── CSV Export ─────────────────────────────────────────────────────────────

    def _export_faltas_csv(self):
        if not self.faltas:
            messagebox.showwarning("Aviso", "Nenhuma falta registrada para exportar.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Exportar Relatório de Faltas",
            initialfile=f"relatorio_faltas_{date.today().strftime('%Y%m%d')}.csv",
        )
        if not path:
            return

        grade: List[Aula] = getattr(self.controller, "grade_gerada", [])

        try:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "Data", "Dia da Semana", "Bloco", "Horário",
                    "Professor Ausente", "Motivo",
                    "Turma(s) Afetada(s)", "Disciplina(s)", "Sala(s)",
                    "Substituto (preencher)", "Observações",
                ])
                for falta in sorted(self.faltas, key=lambda x: x.data):
                    aulas = [a for a in grade if a.professor == falta.professor]
                    turmas = " | ".join(sorted({a.turma for a in aulas})) or "—"
                    discs  = " | ".join(sorted({a.disciplina for a in aulas})) or "—"
                    salas  = " | ".join(sorted({a.sala for a in aulas})) or "—"
                    writer.writerow([
                        falta.data, falta.dia_semana, falta.bloco, falta.horario,
                        falta.professor, falta.motivo,
                        turmas, discs, salas,
                        "", "",
                    ])
            messagebox.showinfo("Exportado", f"Relatório exportado:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar:\n{e}")

    def _export_grade_csv(self):
        grade: List[Aula] = getattr(self.controller, "grade_gerada", [])
        if not grade:
            messagebox.showwarning("Aviso", "Gere a grade no Dashboard antes de exportar.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Exportar Grade Validada",
            initialfile=f"grade_validada_{date.today().strftime('%Y%m%d')}.csv",
        )
        if not path:
            return

        today_str    = date.today().strftime("%d/%m/%Y")
        absent_profs = {f.professor for f in self.faltas if f.data == today_str}

        try:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "Dia", "Horário", "Bloco", "Turma",
                    "Disciplina", "Professor", "Sala", "Status",
                ])
                for aula in grade:
                    status = "FALTA - SEM COBERTURA" if aula.professor in absent_profs else "Presente"
                    writer.writerow([
                        aula.dia, f"{aula.horario}º Horário", aula.bloco,
                        aula.turma, aula.disciplina, aula.professor, aula.sala, status,
                    ])
            messagebox.showinfo("Exportado", f"Grade validada exportada:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar:\n{e}")
