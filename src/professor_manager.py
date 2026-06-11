import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
import os

from .models import Professor
from .data_handler import DataHandler

BG_PAGE    = "#F5F6FA"
BG_CARD    = "#FFFFFF"
ORANGE     = "#F97316"
ORANGE_DIM = "#FFF7ED"
TEXT_DARK  = "#111827"
TEXT_MID   = "#6B7280"
TEXT_LIGHT = "#9CA3AF"
BORDER     = "#E5E7EB"
RED        = "#DC2626"
FONT       = "Segoe UI"


def _card(parent, **kwargs):
    f = tk.Frame(parent, bg=BG_CARD, **kwargs)
    f.config(highlightbackground=BORDER, highlightthickness=1, highlightcolor=BORDER)
    return f


def _btn(parent, text, cmd, primary=False, danger=False):
    if primary:
        bg, fg, abg = ORANGE, "#FFFFFF", "#EA6C0A"
    elif danger:
        bg, fg, abg = RED, "#FFFFFF", "#B91C1C"
    else:
        bg, fg, abg = BG_PAGE, TEXT_DARK, BORDER
    b = tk.Button(
        parent, text=text, command=cmd,
        bg=bg, fg=fg, activebackground=abg,
        activeforeground="#FFFFFF" if (primary or danger) else TEXT_DARK,
        font=(FONT, 10), relief="flat", bd=0,
        padx=14, pady=7, cursor="hand2",
    )
    if not primary and not danger:
        b.config(highlightbackground=BORDER, highlightthickness=1)
    return b


def _entry(parent, width=50):
    e = tk.Entry(
        parent, font=(FONT, 10), bg=BG_PAGE, fg=TEXT_DARK,
        relief="flat", bd=0, width=width,
        highlightbackground=BORDER, highlightthickness=1,
        insertbackground=TEXT_DARK,
    )
    return e


class ProfessorManager(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_PAGE)
        self.controller = controller
        self.professores: List[Professor] = []
        self.file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "professores.csv")
        )
        self._build_ui()
        self._load()

    def _load(self):
        self.professores = DataHandler.load_professores(self.file_path)
        self._refresh_tree()

    def _save(self):
        DataHandler.save_professores(self.file_path, self.professores)

    # ── UI ─────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        PAD = 28

        # Header
        hdr = tk.Frame(self, bg=BG_PAGE)
        hdr.pack(fill="x", padx=PAD, pady=(26, 0))
        tk.Label(hdr, text="Professores", bg=BG_PAGE, fg=TEXT_DARK, font=(FONT, 22, "bold")).pack(anchor="w")
        tk.Label(hdr, text="Gerencie o cadastro de professores.", bg=BG_PAGE, fg=TEXT_MID, font=(FONT, 10)).pack(anchor="w", pady=(3, 0))

        # Form card
        form = _card(self)
        form.pack(fill="x", padx=PAD, pady=(20, 0))

        grid = tk.Frame(form, bg=BG_CARD)
        grid.pack(fill="x", padx=20, pady=(18, 6))
        grid.columnconfigure(1, weight=1)

        fields = [
            ("Nome:",                                  "nome_entry"),
            ("Disciplinas (separadas por vírgula):",   "disciplinas_entry"),
            ("Disponibilidade (ex: Seg-Manhã,Ter-Noite):", "disponibilidade_entry"),
        ]
        for row_idx, (lbl_text, attr) in enumerate(fields):
            tk.Label(grid, text=lbl_text, bg=BG_CARD, fg=TEXT_MID, font=(FONT, 9)).grid(
                row=row_idx, column=0, sticky="w", pady=(0, 4),
            )
            entry = _entry(grid)
            entry.grid(row=row_idx, column=1, sticky="ew", padx=(14, 0), pady=(0, 12), ipady=6)
            setattr(self, attr, entry)

        # Buttons
        btn_row = tk.Frame(form, bg=BG_CARD)
        btn_row.pack(fill="x", padx=20, pady=(0, 18))

        for txt, cmd, prim, dng in [
            ("Adicionar",         self.add_professor,    True,  False),
            ("Atualizar",         self.update_professor, True,  False),
            ("Deletar",           self.delete_professor, False, True),
            ("Limpar",            self.clear_fields,     False, False),
            ("ℹ️ Como adicionar", self.show_info,        False, False),
        ]:
            _btn(btn_row, txt, cmd, primary=prim, danger=dng).pack(side="left", padx=(0, 8))

        # Table
        sec_row = tk.Frame(self, bg=BG_PAGE)
        sec_row.pack(fill="x", padx=PAD, pady=(22, 8))
        tk.Label(sec_row, text="Lista de Professores", bg=BG_PAGE, fg=TEXT_DARK, font=(FONT, 11, "bold")).pack(side="left")

        tree_card = _card(self)
        tree_card.pack(fill="both", expand=True, padx=PAD, pady=(0, 24))

        self.tree = ttk.Treeview(
            tree_card,
            columns=("Nome", "Disciplinas", "Disponibilidade"),
            show="headings", selectmode="browse",
        )
        for col, w in [("Nome", 160), ("Disciplinas", 220), ("Disponibilidade", 300)]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)

        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        vsb = ttk.Scrollbar(tree_card, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=vsb.set)

    # ── Treeview ───────────────────────────────────────────────────────────────

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for p in self.professores:
            self.tree.insert("", "end", values=(p.nome, ", ".join(p.disciplinas), ", ".join(p.disponibilidade)))

    def _on_select(self, _event):
        item = self.tree.focus()
        if not item:
            return
        v = self.tree.item(item, "values")
        for entry, val in zip(
            [self.nome_entry, self.disciplinas_entry, self.disponibilidade_entry], v
        ):
            entry.delete(0, tk.END)
            entry.insert(0, val)

    # ── CRUD ───────────────────────────────────────────────────────────────────

    def add_professor(self):
        nome  = self.nome_entry.get().strip()
        disc  = self.disciplinas_entry.get().strip()
        disp  = self.disponibilidade_entry.get().strip()
        if not nome or not disc or not disp:
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios.")
            return
        if any(p.nome == nome for p in self.professores):
            messagebox.showwarning("Aviso", f"Professor '{nome}' já existe.")
            return
        disciplinas    = [d.strip() for d in disc.split(",") if d.strip()]
        disponibilidade = [d.strip() for d in disp.split(",") if d.strip()]
        self.professores.append(Professor(nome, disciplinas, disponibilidade))
        self._save()
        self._refresh_tree()
        self.clear_fields()
        messagebox.showinfo("Sucesso", f"Professor '{nome}' adicionado.")

    def update_professor(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um professor para atualizar.")
            return
        old_nome = self.tree.item(item, "values")[0]
        nome  = self.nome_entry.get().strip()
        disc  = self.disciplinas_entry.get().strip()
        disp  = self.disponibilidade_entry.get().strip()
        if not nome or not disc or not disp:
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios.")
            return
        if nome != old_nome and any(p.nome == nome for p in self.professores):
            messagebox.showwarning("Aviso", f"Professor '{nome}' já existe.")
            return
        disciplinas    = [d.strip() for d in disc.split(",") if d.strip()]
        disponibilidade = [d.strip() for d in disp.split(",") if d.strip()]
        for p in self.professores:
            if p.nome == old_nome:
                p.nome           = nome
                p.disciplinas    = disciplinas
                p.disponibilidade = disponibilidade
                break
        self._save()
        self._refresh_tree()
        self.clear_fields()
        messagebox.showinfo("Sucesso", f"Professor '{nome}' atualizado.")

    def delete_professor(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um professor para deletar.")
            return
        nome = self.tree.item(item, "values")[0]
        if messagebox.askyesno("Confirmar", f"Deletar professor '{nome}'?"):
            self.professores = [p for p in self.professores if p.nome != nome]
            self._save()
            self._refresh_tree()
            self.clear_fields()

    def clear_fields(self):
        for e in [self.nome_entry, self.disciplinas_entry, self.disponibilidade_entry]:
            e.delete(0, tk.END)

    def show_info(self):
        messagebox.showinfo("Como adicionar Professores", (
            "• Nome: nome completo do professor.\n"
            "• Disciplinas: separadas por vírgula (ex: Matemática, Física).\n"
            "• Disponibilidade: Dia-Bloco separados por vírgula\n"
            "  (ex: Seg-Manhã, Ter-Noite, Qua-Tarde)."
        ))
