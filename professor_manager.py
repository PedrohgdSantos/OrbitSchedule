import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
from models import Professor
from data_handler import DataHandler
from rounded_frame import RoundedFrame
import os

class ProfessorManager(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#050608")
        self.controller = controller
        self.professores: List[Professor] = []
        self.file_path = os.path.join(os.path.dirname(__file__), "data", "professores.csv")
        self.create_widgets() # Primeiro, cria os widgets, incluindo self.tree
        self.load_professores() # Depois, carrega os professores e atualiza a treeview

    def load_professores(self):
        """Carrega os professores do arquivo CSV."""
        self.professores = DataHandler.load_professores(self.file_path)
        self.update_treeview()

    def save_professores(self):
        """Salva os professores no arquivo CSV."""
        DataHandler.save_professores(self.file_path, self.professores)

    def create_widgets(self):
        # Cabeçalho do formulário
        ttk.Label(self, text="Dados do Professor", style="CardHeader.TLabel").pack(pady=(10, 0), padx=10, anchor="w")

        # Frame de entrada de dados
        input_frame = RoundedFrame(self, bg_color="#111827", border_color="#1F2937", corner_radius=18, padding=14)
        input_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(input_frame.inner_frame, text="Nome:").grid(row=0, column=0, sticky="w", pady=2)
        self.nome_entry = ttk.Entry(input_frame.inner_frame, width=40)
        self.nome_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(input_frame.inner_frame, text="Disciplinas (separadas por vírgula):").grid(row=1, column=0, sticky="w", pady=2)
        self.disciplinas_entry = ttk.Entry(input_frame.inner_frame, width=40)
        self.disciplinas_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(input_frame.inner_frame, text="Disponibilidade (Dia-Bloco, ex: Seg-Manhã):").grid(row=2, column=0, sticky="w", pady=2)
        self.disponibilidade_entry = ttk.Entry(input_frame.inner_frame, width=40)
        self.disponibilidade_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        # Botões de ação
        btn_frame = RoundedFrame(input_frame.inner_frame, bg_color="#111827", border_color="#1F2937", corner_radius=16, padding=10)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        ttk.Button(btn_frame, text="Adicionar", command=self.add_professor, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Atualizar", command=self.update_professor, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Deletar", command=self.delete_professor, style="Danger.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpar Campos", command=self.clear_fields).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="ℹ️ Como adicionar", command=self.show_info, style="Accent.TButton").pack(side="left", padx=5)


        # Treeview para exibir professores
        tree_container = RoundedFrame(self, bg_color="#111827", border_color="#1F2937", corner_radius=18, padding=12)
        tree_container.pack(pady=10, padx=10, fill="both", expand=True)
        self.tree = ttk.Treeview(tree_container.inner_frame, columns=("Nome", "Disciplinas", "Disponibilidade"), show="headings", selectmode="browse")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Disciplinas", text="Disciplinas")
        self.tree.heading("Disponibilidade", text="Disponibilidade")
        self.tree.column("Nome", width=150)
        self.tree.column("Disciplinas", width=200)
        self.tree.column("Disponibilidade", width=250)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected_professor)

        # A chamada para update_treeview() agora é feita dentro de load_professores(), que é chamado após create_widgets().

    def update_treeview(self):
        """Atualiza a exibição da Treeview com os dados atuais dos professores."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        for prof in self.professores:
            self.tree.insert("", "end", values=(prof.nome, ", ".join(prof.disciplinas), ", ".join(prof.disponibilidade)))

    def add_professor(self):
        """Adiciona um novo professor à lista e salva no CSV."""
        nome = self.nome_entry.get().strip()
        disciplinas_str = self.disciplinas_entry.get().strip()
        disponibilidade_str = self.disponibilidade_entry.get().strip()

        if not nome or not disciplinas_str or not disponibilidade_str:
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios para adicionar um professor.")
            return

        disciplinas = [d.strip() for d in disciplinas_str.split(",") if d.strip()]
        disponibilidade = [d.strip() for d in disponibilidade_str.split(",") if d.strip()]

        if any(p.nome == nome for p in self.professores):
            messagebox.showwarning("Aviso", f"Professor com o nome \'{nome}\' já existe.")
            return

        new_prof = Professor(nome, disciplinas, disponibilidade)
        self.professores.append(new_prof)
        self.save_professores()
        self.update_treeview()
        self.clear_fields()
        messagebox.showinfo("Sucesso", f"Professor \'{nome}\' adicionado com sucesso.")

    def update_professor(self):
        """Atualiza os dados de um professor existente e salva no CSV."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um professor para atualizar.")
            return

        old_nome = self.tree.item(selected_item, "values")[0]
        nome = self.nome_entry.get().strip()
        disciplinas_str = self.disciplinas_entry.get().strip()
        disponibilidade_str = self.disponibilidade_entry.get().strip()

        if not nome or not disciplinas_str or not disponibilidade_str:
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios para atualizar um professor.")
            return

        disciplinas = [d.strip() for d in disciplinas_str.split(",") if d.strip()]
        disponibilidade = [d.strip() for d in disponibilidade_str.split(",") if d.strip()]

        for i, prof in enumerate(self.professores):
            if prof.nome == old_nome:
                # Verifica se o novo nome já existe para outro professor
                if nome != old_nome and any(p.nome == nome for p in self.professores if p.nome != old_nome):
                    messagebox.showwarning("Aviso", f"Professor com o nome \'{nome}\' já existe.")
                    return
                
                self.professores[i].nome = nome
                self.professores[i].disciplinas = disciplinas
                self.professores[i].disponibilidade = disponibilidade
                break
        self.save_professores()
        self.update_treeview()
        self.clear_fields()
        messagebox.showinfo("Sucesso", f"Professor \'{nome}\' atualizado com sucesso.")

    def delete_professor(self):
        """Deleta um professor da lista e salva no CSV."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um professor para deletar.")
            return

        nome_to_delete = self.tree.item(selected_item, "values")[0]
        if messagebox.askyesno("Confirmar Deleção", f"Tem certeza que deseja deletar o professor \'{nome_to_delete}\'?"):
            self.professores = [p for p in self.professores if p.nome != nome_to_delete]
            self.save_professores()
            self.update_treeview()
            self.clear_fields()
            messagebox.showinfo("Sucesso", f"Professor \'{nome_to_delete}\' deletado com sucesso.")

    def load_selected_professor(self, event):
        """Carrega os dados do professor selecionado na Treeview para os campos de entrada."""
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            self.nome_entry.delete(0, tk.END)
            self.nome_entry.insert(0, values[0])
            self.disciplinas_entry.delete(0, tk.END)
            self.disciplinas_entry.insert(0, values[1])
            self.disponibilidade_entry.delete(0, tk.END)
            self.disponibilidade_entry.insert(0, values[2])

    def clear_fields(self):
        """Limpa todos os campos de entrada de dados."""
        self.nome_entry.delete(0, tk.END)
        self.disciplinas_entry.delete(0, tk.END)
        self.disponibilidade_entry.delete(0, tk.END)

    def show_info(self):
        msg = (
            "Como adicionar um Professor:\n\n"
            "• Nome: Digite o nome completo do professor.\n"
            "• Disciplinas: Informe as disciplinas separadas por vírgula (ex: Matemática, Física).\n"
            "• Disponibilidade: Informe os dias e blocos separados por vírgula (ex: Seg-Manhã, Ter-Noite, Qua-Tarde).\n"
            "Certifique-se de não deixar espaços extras desnecessários nas listas."
        )
        messagebox.showinfo("Informação - Professores", msg)
