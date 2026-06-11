import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
import os

from .models import Turma, Sala
from .data_handler import DataHandler

BG_PAGE    = "#F5F6FA"
BG_CARD    = "#FFFFFF"
ORANGE     = "#F97316"
ORANGE_DIM = "#FFF7ED"
TEXT_DARK  = "#111827"
TEXT_MID   = "#6B7280"
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
    return tk.Entry(
        parent, font=(FONT, 10), bg=BG_PAGE, fg=TEXT_DARK,
        relief="flat", bd=0, width=width,
        highlightbackground=BORDER, highlightthickness=1,
        insertbackground=TEXT_DARK,
    )


class TurmaManager(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_PAGE)
        self.controller = controller
        self.turmas: List[Turma] = []
        self.file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "turmas.csv")
        )
        self._build_ui()
        self._load()

    def _load(self):
        self.turmas = DataHandler.load_turmas(self.file_path)
        self._refresh_tree()

    def _save(self):
        DataHandler.save_turmas(self.file_path, self.turmas)

    # ── UI ─────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        PAD = 28

        # Header
        hdr = tk.Frame(self, bg=BG_PAGE)
        hdr.pack(fill="x", padx=PAD, pady=(26, 0))
        tk.Label(hdr, text="Turmas", bg=BG_PAGE, fg=TEXT_DARK, font=(FONT, 22, "bold")).pack(anchor="w")
        tk.Label(hdr, text="Gerencie o cadastro de turmas.", bg=BG_PAGE, fg=TEXT_MID, font=(FONT, 10)).pack(anchor="w", pady=(3, 0))

        # Form card
        form = _card(self)
        form.pack(fill="x", padx=PAD, pady=(20, 0))

        grid = tk.Frame(form, bg=BG_CARD)
        grid.pack(fill="x", padx=20, pady=(18, 6))
        grid.columnconfigure(1, weight=1)

        # Text entry fields
        text_fields = [
            ("Nome:",                                "nome_entry"),
            ("Carga Horária (número inteiro):",      "carga_horaria_entry"),
            ("Disciplinas (separadas por vírgula):", "disciplinas_entry"),
        ]
        for row_idx, (lbl, attr) in enumerate(text_fields):
            tk.Label(grid, text=lbl, bg=BG_CARD, fg=TEXT_MID, font=(FONT, 9)).grid(
                row=row_idx, column=0, sticky="w", pady=(0, 4),
            )
            entry = _entry(grid)
            entry.grid(row=row_idx, column=1, sticky="ew", padx=(14, 0), pady=(0, 12), ipady=6)
            setattr(self, attr, entry)

        # Sala preferencial combobox
        tk.Label(grid, text="Sala Preferencial:", bg=BG_CARD, fg=TEXT_MID, font=(FONT, 9)).grid(
            row=3, column=0, sticky="w", pady=(0, 4),
        )
        self.sala_preferencial_combobox = ttk.Combobox(grid, width=48, state="readonly", font=(FONT, 10))
        self.sala_preferencial_combobox.grid(row=3, column=1, sticky="ew", padx=(14, 0), pady=(0, 12), ipady=4)
        self.update_sala_options()

        # Buttons
        btn_row = tk.Frame(form, bg=BG_CARD)
        btn_row.pack(fill="x", padx=20, pady=(0, 18))

        for txt, cmd, prim, dng in [
            ("Adicionar",         self.add_turma,    True,  False),
            ("Atualizar",         self.update_turma, True,  False),
            ("Deletar",           self.delete_turma, False, True),
            ("Limpar",            self.clear_fields, False, False),
            ("ℹ️ Como adicionar", self.show_info,    False, False),
        ]:
            _btn(btn_row, txt, cmd, primary=prim, danger=dng).pack(side="left", padx=(0, 8))

        # Table
        sec_row = tk.Frame(self, bg=BG_PAGE)
        sec_row.pack(fill="x", padx=PAD, pady=(22, 8))
        tk.Label(sec_row, text="Lista de Turmas", bg=BG_PAGE, fg=TEXT_DARK, font=(FONT, 11, "bold")).pack(side="left")

        tree_card = _card(self)
        tree_card.pack(fill="both", expand=True, padx=PAD, pady=(0, 24))

        self.tree = ttk.Treeview(
            tree_card,
            columns=("Nome", "Carga Horária", "Disciplinas", "Sala Preferencial"),
            show="headings", selectmode="browse",
        )
        for col, w in [("Nome", 120), ("Carga Horária", 100), ("Disciplinas", 220), ("Sala Preferencial", 120)]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)

        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        vsb = ttk.Scrollbar(tree_card, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=vsb.set)

    # ── Sala options ───────────────────────────────────────────────────────────

    def update_sala_options(self):
        salas: List[Sala] = self.controller.sala_manager.salas if hasattr(self.controller, "sala_manager") else []
        nums = [s.numero for s in salas]
        self.sala_preferencial_combobox["values"] = nums
        self.sala_preferencial_combobox.set(nums[0] if nums else "")

    # ── Treeview ───────────────────────────────────────────────────────────────

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for t in self.turmas:
            self.tree.insert("", "end", values=(
                t.nome, t.carga_horaria, ", ".join(t.disciplinas), t.sala_preferencial,
            ))

    def _on_select(self, _event):
        item = self.tree.focus()
        if not item:
            return
        v = self.tree.item(item, "values")
        for entry, val in zip(
            [self.nome_entry, self.carga_horaria_entry, self.disciplinas_entry], v[:3]
        ):
            entry.delete(0, tk.END)
            entry.insert(0, val)
        self.sala_preferencial_combobox.set(v[3])

    # ── CRUD ───────────────────────────────────────────────────────────────────

    def add_turma(self):
        nome      = self.nome_entry.get().strip()
        ch_str    = self.carga_horaria_entry.get().strip()
        disc_str  = self.disciplinas_entry.get().strip()
        sala_pref = self.sala_preferencial_combobox.get().strip()

        if not nome or not ch_str or not disc_str or not sala_pref:
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios.")
            return
        try:
            carga_horaria = int(ch_str)
        except ValueError:
            messagebox.showwarning("Aviso", "Carga Horária deve ser um número inteiro.")
            return
        if any(t.nome == nome for t in self.turmas):
            messagebox.showwarning("Aviso", f"Turma '{nome}' já existe.")
            return
        if sala_pref not in self.sala_preferencial_combobox["values"]:
            messagebox.showwarning("Aviso", f"Sala '{sala_pref}' não existe.")
            return

        disciplinas = sorted([d.strip() for d in disc_str.split(",") if d.strip()])
        turmas_na_sala = [t for t in self.turmas if t.sala_preferencial == sala_pref]
        if len(turmas_na_sala) >= 2:
            messagebox.showwarning("Aviso", "Sala já atingiu o limite de 2 turmas.")
            return
        if len(turmas_na_sala) == 1 and sorted(turmas_na_sala[0].disciplinas) != disciplinas:
            messagebox.showwarning("Aviso", "Sala ocupada por turma com disciplinas diferentes.")
            return

        self.turmas.append(Turma(nome, carga_horaria, disciplinas, sala_pref))
        self._save()
        self._refresh_tree()
        self.clear_fields()
        messagebox.showinfo("Sucesso", f"Turma '{nome}' adicionada.")

    def update_turma(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma turma para atualizar.")
            return
        old_nome  = self.tree.item(item, "values")[0]
        nome      = self.nome_entry.get().strip()
        ch_str    = self.carga_horaria_entry.get().strip()
        disc_str  = self.disciplinas_entry.get().strip()
        sala_pref = self.sala_preferencial_combobox.get().strip()

        if not nome or not ch_str or not disc_str or not sala_pref:
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios.")
            return
        try:
            carga_horaria = int(ch_str)
        except ValueError:
            messagebox.showwarning("Aviso", "Carga Horária deve ser um número inteiro.")
            return
        if nome != old_nome and any(t.nome == nome for t in self.turmas):
            messagebox.showwarning("Aviso", f"Turma '{nome}' já existe.")
            return
        if sala_pref not in self.sala_preferencial_combobox["values"]:
            messagebox.showwarning("Aviso", f"Sala '{sala_pref}' não existe.")
            return

        original = next((t for t in self.turmas if t.nome == old_nome), None)
        if not original:
            return

        disciplinas = sorted([d.strip() for d in disc_str.split(",") if d.strip()])
        sem_atual = [t for t in self.turmas if t.sala_preferencial == sala_pref and t.nome != old_nome]

        if sala_pref != original.sala_preferencial:
            if len(sem_atual) >= 2:
                messagebox.showwarning("Aviso", "Sala já atingiu o limite de 2 turmas.")
                return
            if len(sem_atual) == 1 and sorted(sem_atual[0].disciplinas) != disciplinas:
                messagebox.showwarning("Aviso", "Sala ocupada por turma com disciplinas diferentes.")
                return
        elif disciplinas != sorted(original.disciplinas) and sem_atual:
            if len(sem_atual) >= 2:
                messagebox.showwarning("Aviso", "Sala já atingiu o limite de 2 turmas.")
                return
            if sorted(sem_atual[0].disciplinas) != disciplinas:
                messagebox.showwarning("Aviso", "Sala ocupada por turma com disciplinas diferentes.")
                return

        original.nome            = nome
        original.carga_horaria   = carga_horaria
        original.disciplinas     = disciplinas
        original.sala_preferencial = sala_pref
        self._save()
        self._refresh_tree()
        self.clear_fields()
        messagebox.showinfo("Sucesso", f"Turma '{nome}' atualizada.")

    def delete_turma(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma turma para deletar.")
            return
        nome = self.tree.item(item, "values")[0]
        if messagebox.askyesno("Confirmar", f"Deletar turma '{nome}'?"):
            self.turmas = [t for t in self.turmas if t.nome != nome]
            self._save()
            self._refresh_tree()
            self.clear_fields()

    def clear_fields(self):
        for e in [self.nome_entry, self.carga_horaria_entry, self.disciplinas_entry]:
            e.delete(0, tk.END)
        self.sala_preferencial_combobox.set("")

    def show_info(self):
        messagebox.showinfo("Como adicionar Turmas", (
            "• Nome: nome da turma (ex: 1º Ano A).\n"
            "• Carga Horária: número inteiro de aulas totais.\n"
            "• Disciplinas: separadas por vírgula (ex: Matemática, Física).\n"
            "• Sala Preferencial: sala onde a turma terá a maioria das aulas.\n\n"
            "Uma sala suporta no máximo 2 turmas com as mesmas disciplinas."
        ))
