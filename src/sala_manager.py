import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
from .models import Sala
from .data_handler import DataHandler
from .rounded_frame import RoundedFrame
import os

class SalaManager(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#050608")
        self.controller = controller
        self.salas: List[Sala] = []
        # Define o caminho do arquivo CSV de salas, relativo à raiz do projeto.
        self.file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "salas.csv"))
        self.create_widgets() # Primeiro, cria os widgets, incluindo self.tree
        self.load_salas() # Depois, carrega as salas e atualiza a treeview

    def load_salas(self):
        """Carrega as salas do arquivo CSV e atualiza a Treeview."""
        self.salas = DataHandler.load_salas(self.file_path)
        self.update_treeview()

    def save_salas(self):
        """Salva a lista atual de salas no arquivo CSV e notifica o TurmaManager."""
        DataHandler.save_salas(self.file_path, self.salas)
        # Notifica o TurmaManager para atualizar as opções de salas no dropdown.
        if hasattr(self.controller, "turma_manager"):
            self.controller.turma_manager.update_sala_options()

    def create_widgets(self):
        """Cria os widgets da interface para gerenciamento de salas."""
        # Cabeçalho do formulário
        ttk.Label(self, text="Dados da Sala", style="CardHeader.TLabel").pack(pady=(10, 0), padx=10, anchor="w")

        # Frame para entrada de dados da sala.
        input_frame = RoundedFrame(self, bg_color="#111827", border_color="#1F2937", corner_radius=18, padding=14)
        input_frame.pack(pady=10, padx=10, fill="x")

        # Campo para o número da sala.
        ttk.Label(input_frame.inner_frame, text="Número da Sala:").grid(row=0, column=0, sticky="w", pady=2)
        self.numero_sala_entry = ttk.Entry(input_frame.inner_frame, width=40)
        self.numero_sala_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # Checkbox para indicar se é um laboratório.
        ttk.Label(input_frame.inner_frame, text="É Laboratório?").grid(row=1, column=0, sticky="w", pady=2)
        self.is_laboratorio_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame.inner_frame, variable=self.is_laboratorio_var).grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Botões de ação (Adicionar, Atualizar, Deletar, Limpar Campos).
        btn_frame = RoundedFrame(input_frame.inner_frame, bg_color="#111827", border_color="#1F2937", corner_radius=16, padding=10)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        ttk.Button(btn_frame, text="Adicionar", command=self.add_sala, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Atualizar", command=self.update_sala, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Deletar", command=self.delete_sala, style="Danger.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpar Campos", command=self.clear_fields).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="ℹ️ Como adicionar", command=self.show_info, style="Accent.TButton").pack(side="left", padx=5)


        # Treeview para exibir a lista de salas.
        tree_container = RoundedFrame(self, bg_color="#111827", border_color="#1F2937", corner_radius=18, padding=12)
        tree_container.pack(pady=10, padx=10, fill="both", expand=True)
        self.tree = ttk.Treeview(tree_container.inner_frame, columns=("Número da Sala", "É Laboratório"), show="headings", selectmode="browse")
        self.tree.heading("Número da Sala", text="Número da Sala")
        self.tree.heading("É Laboratório", text="É Laboratório")
        self.tree.column("Número da Sala", width=150)
        self.tree.column("É Laboratório", width=150)
        self.tree.pack(fill="both", expand=True)
        # Associa a função load_selected_sala ao evento de seleção na Treeview.
        self.tree.bind("<<TreeviewSelect>>", self.load_selected_sala)

    def update_treeview(self):
        """Atualiza a exibição da Treeview com os dados atuais das salas."""
        # Limpa todos os itens existentes na Treeview.
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Insere cada sala da lista na Treeview.
        for sala in self.salas:
            lab_status = "Sim" if sala.is_laboratorio else "Não"
            self.tree.insert("", "end", values=(sala.numero, lab_status))

    def add_sala(self):
        """Adiciona uma nova sala à lista e salva no CSV."""
        numero = self.numero_sala_entry.get().strip()
        is_laboratorio = self.is_laboratorio_var.get()

        if not numero:
            messagebox.showwarning("Aviso", "O número da sala é obrigatório.")
            return

        # Verifica se já existe uma sala com o mesmo número.
        if any(s.numero == numero for s in self.salas):
            messagebox.showwarning("Aviso", f"Sala com o número \'{numero}\' já existe.")
            return

        new_sala = Sala(numero, is_laboratorio)
        self.salas.append(new_sala)
        self.save_salas()
        self.update_treeview()
        self.clear_fields()
        messagebox.showinfo("Sucesso", f"Sala \'{numero}\' adicionada com sucesso.")

    def update_sala(self):
        """Atualiza os dados de uma sala existente e salva no CSV."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma sala para atualizar.")
            return

        old_numero = self.tree.item(selected_item, "values")[0]
        numero = self.numero_sala_entry.get().strip()
        is_laboratorio = self.is_laboratorio_var.get()

        if not numero:
            messagebox.showwarning("Aviso", "O número da sala é obrigatório.")
            return

        for i, sala in enumerate(self.salas):
            if sala.numero == old_numero:
                # Verifica se o novo número já existe para outra sala.
                if numero != old_numero and any(s.numero == numero for s in self.salas if s.numero != old_numero):
                    messagebox.showwarning("Aviso", f"Sala com o número \'{numero}\' já existe.")
                    return
                
                self.salas[i].numero = numero
                self.salas[i].is_laboratorio = is_laboratorio
                break
        self.save_salas()
        self.update_treeview()
        self.clear_fields()
        messagebox.showinfo("Sucesso", f"Sala \'{numero}\' atualizada com sucesso.")

    def delete_sala(self):
        """Deleta uma sala da lista e salva no CSV."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma sala para deletar.")
            return

        numero_to_delete = self.tree.item(selected_item, "values")[0]
        if messagebox.askyesno("Confirmar Deleção", f"Tem certeza que deseja deletar a sala \'{numero_to_delete}\'?"):
            self.salas = [s for s in self.salas if s.numero != numero_to_delete]
            self.save_salas()
            self.update_treeview()
            self.clear_fields()
            messagebox.showinfo("Sucesso", f"Sala \'{numero_to_delete}\' deletada com sucesso.")

    def load_selected_sala(self, event):
        """Carrega os dados da sala selecionada na Treeview para os campos de entrada."""
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            self.numero_sala_entry.delete(0, tk.END)
            self.numero_sala_entry.insert(0, values[0])
            self.is_laboratorio_var.set(values[1] == "Sim")

    def clear_fields(self):
        """Limpa todos os campos de entrada de dados."""
        self.numero_sala_entry.delete(0, tk.END)
        self.is_laboratorio_var.set(False)

    def show_info(self):
        msg = (
            "Como adicionar uma Sala:\n\n"
            "• Número da Sala: Digite o identificador da sala (ex: 101, Lab A).\n"
            "• É Laboratório?: Marque esta opção caso a sala seja um laboratório de informática ou prática.\n"
            "O número da sala deve ser único."
        )
        messagebox.showinfo("Informação - Salas", msg)
