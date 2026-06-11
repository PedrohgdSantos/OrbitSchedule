import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
import os

from .models import Sala
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


class SalaManager(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_PAGE)
        self.controller = controller
        self.salas: List[Sala] = []
        self.file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "salas.csv")
        )
        self._build_ui()
        self._load()

    def _load(self):
        self.salas = DataHandler.load_salas(self.file_path)
        self._refresh_tree()

    def _save(self):
        DataHandler.save_salas(self.file_path, self.salas)
        if hasattr(self.controller, "turma_manager"):
            self.controller.turma_manager.update_sala_options()

    # ── UI ─────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        PAD = 28

        # Header
        hdr = tk.Frame(self, bg=BG_PAGE)
        hdr.pack(fill="x", padx=PAD, pady=(26, 0))
        tk.Label(hdr, text="Salas", bg=BG_PAGE, fg=TEXT_DARK, font=(FONT, 22, "bold")).pack(anchor="w")
        tk.Label(hdr, text="Gerencie o cadastro de salas.", bg=BG_PAGE, fg=TEXT_MID, font=(FONT, 10)).pack(anchor="w", pady=(3, 0))

        # Form card
        form = _card(self)
        form.pack(fill="x", padx=PAD, pady=(20, 0))

        grid = tk.Frame(form, bg=BG_CARD)
        grid.pack(fill="x", padx=20, pady=(18, 6))
        grid.columnconfigure(1, weight=1)

        # Número da sala
        tk.Label(grid, text="Número da Sala:", bg=BG_CARD, fg=TEXT_MID, font=(FONT, 9)).grid(
            row=0, column=0, sticky="w", pady=(0, 4),
        )
        self.numero_entry = tk.Entry(
            grid, font=(FONT, 10), bg=BG_PAGE, fg=TEXT_DARK,
            relief="flat", bd=0, width=50,
            highlightbackground=BORDER, highlightthickness=1,
            insertbackground=TEXT_DARK,
        )
        self.numero_entry.grid(row=0, column=1, sticky="ew", padx=(14, 0), pady=(0, 12), ipady=6)

        # Checkbox laboratório
        tk.Label(grid, text="É Laboratório?", bg=BG_CARD, fg=TEXT_MID, font=(FONT, 9)).grid(
            row=1, column=0, sticky="w", pady=(0, 4),
        )
        self.is_lab_var = tk.BooleanVar()
        chk = tk.Checkbutton(
            grid, variable=self.is_lab_var,
            bg=BG_CARD, activebackground=BG_CARD,
            selectcolor=ORANGE_DIM, relief="flat", bd=0, cursor="hand2",
        )
        chk.grid(row=1, column=1, sticky="w", padx=(14, 0), pady=(0, 12))

        # Buttons
        btn_row = tk.Frame(form, bg=BG_CARD)
        btn_row.pack(fill="x", padx=20, pady=(0, 18))

        for txt, cmd, prim, dng in [
            ("Adicionar",         self.add_sala,    True,  False),
            ("Atualizar",         self.update_sala, True,  False),
            ("Deletar",           self.delete_sala, False, True),
            ("Limpar",            self.clear_fields, False, False),
            ("ℹ️ Como adicionar", self.show_info,   False, False),
        ]:
            _btn(btn_row, txt, cmd, primary=prim, danger=dng).pack(side="left", padx=(0, 8))

        # Table
        sec_row = tk.Frame(self, bg=BG_PAGE)
        sec_row.pack(fill="x", padx=PAD, pady=(22, 8))
        tk.Label(sec_row, text="Lista de Salas", bg=BG_PAGE, fg=TEXT_DARK, font=(FONT, 11, "bold")).pack(side="left")

        tree_card = _card(self)
        tree_card.pack(fill="both", expand=True, padx=PAD, pady=(0, 24))

        self.tree = ttk.Treeview(
            tree_card,
            columns=("Número da Sala", "É Laboratório"),
            show="headings", selectmode="browse",
        )
        for col, w in [("Número da Sala", 200), ("É Laboratório", 160)]:
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
        for s in self.salas:
            self.tree.insert("", "end", values=(s.numero, "Sim" if s.is_laboratorio else "Não"))

    def _on_select(self, _event):
        item = self.tree.focus()
        if not item:
            return
        v = self.tree.item(item, "values")
        self.numero_entry.delete(0, tk.END)
        self.numero_entry.insert(0, v[0])
        self.is_lab_var.set(v[1] == "Sim")

    # ── CRUD ───────────────────────────────────────────────────────────────────

    def add_sala(self):
        numero = self.numero_entry.get().strip()
        if not numero:
            messagebox.showwarning("Aviso", "O número da sala é obrigatório.")
            return
        if any(s.numero == numero for s in self.salas):
            messagebox.showwarning("Aviso", f"Sala '{numero}' já existe.")
            return
        self.salas.append(Sala(numero, self.is_lab_var.get()))
        self._save()
        self._refresh_tree()
        self.clear_fields()
        messagebox.showinfo("Sucesso", f"Sala '{numero}' adicionada.")

    def update_sala(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma sala para atualizar.")
            return
        old_numero = self.tree.item(item, "values")[0]
        numero = self.numero_entry.get().strip()
        if not numero:
            messagebox.showwarning("Aviso", "O número da sala é obrigatório.")
            return
        if numero != old_numero and any(s.numero == numero for s in self.salas):
            messagebox.showwarning("Aviso", f"Sala '{numero}' já existe.")
            return
        for s in self.salas:
            if s.numero == old_numero:
                s.numero        = numero
                s.is_laboratorio = self.is_lab_var.get()
                break
        self._save()
        self._refresh_tree()
        self.clear_fields()
        messagebox.showinfo("Sucesso", f"Sala '{numero}' atualizada.")

    def delete_sala(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma sala para deletar.")
            return
        numero = self.tree.item(item, "values")[0]
        if messagebox.askyesno("Confirmar", f"Deletar sala '{numero}'?"):
            self.salas = [s for s in self.salas if s.numero != numero]
            self._save()
            self._refresh_tree()
            self.clear_fields()

    def clear_fields(self):
        self.numero_entry.delete(0, tk.END)
        self.is_lab_var.set(False)

    def show_info(self):
        messagebox.showinfo("Como adicionar Salas", (
            "• Número da Sala: identificador único (ex: 101, Lab A).\n"
            "• É Laboratório?: marque se for um laboratório de informática ou prática."
        ))
