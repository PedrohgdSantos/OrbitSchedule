import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
from .models import Turma, Sala # Importa Sala também para obter a lista de salas
from .data_handler import DataHandler
from .rounded_frame import RoundedFrame
import os

class TurmaManager(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#050608")
        self.controller = controller # O controller é a instância de SchedulerApp
        self.turmas: List[Turma] = []
        self.file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "turmas.csv"))
        self.create_widgets() # Primeiro, cria os widgets, incluindo self.tree e o Combobox
        self.load_turmas() # Depois, carrega as turmas e atualiza a treeview

    def load_turmas(self):
        """Carrega as turmas do arquivo CSV."""
        self.turmas = DataHandler.load_turmas(self.file_path)
        self.update_treeview()

    def save_turmas(self):
        """Salva as turmas no arquivo CSV."""
        DataHandler.save_turmas(self.file_path, self.turmas)

    def create_widgets(self):
        """Cria os widgets da interface para gerenciamento de turmas."""
        # Cabeçalho do formulário
        ttk.Label(self, text="Dados da Turma", style="CardHeader.TLabel").pack(pady=(10, 0), padx=10, anchor="w")

        # Frame de entrada de dados
        input_frame = RoundedFrame(self, bg_color="#111827", border_color="#1F2937", corner_radius=18, padding=14)
        input_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(input_frame.inner_frame, text="Nome:").grid(row=0, column=0, sticky="w", pady=2)
        self.nome_entry = ttk.Entry(input_frame.inner_frame, width=40)
        self.nome_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(input_frame.inner_frame, text="Carga Horária:").grid(row=1, column=0, sticky="w", pady=2)
        self.carga_horaria_entry = ttk.Entry(input_frame.inner_frame, width=40)
        self.carga_horaria_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(input_frame.inner_frame, text="Disciplinas (separadas por vírgula):").grid(row=2, column=0, sticky="w", pady=2)
        self.disciplinas_entry = ttk.Entry(input_frame.inner_frame, width=40)
        self.disciplinas_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(input_frame.inner_frame, text="Sala Preferencial:").grid(row=3, column=0, sticky="w", pady=2)
        # Combobox para seleção da sala preferencial
        self.sala_preferencial_combobox = ttk.Combobox(input_frame.inner_frame, width=38, state="readonly")
        self.sala_preferencial_combobox.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        self.update_sala_options() # Carrega as opções de salas no Combobox

        # Botões de ação
        btn_frame = RoundedFrame(input_frame.inner_frame, bg_color="#111827", border_color="#1F2937", corner_radius=16, padding=10)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        ttk.Button(btn_frame, text="Adicionar", command=self.add_turma, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Atualizar", command=self.update_turma, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Deletar", command=self.delete_turma, style="Danger.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpar Campos", command=self.clear_fields).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="ℹ️ Como adicionar", command=self.show_info, style="Accent.TButton").pack(side="left", padx=5)


        # Treeview para exibir turmas
        tree_container = RoundedFrame(self, bg_color="#111827", border_color="#1F2937", corner_radius=18, padding=12)
        tree_container.pack(pady=10, padx=10, fill="both", expand=True)
        self.tree = ttk.Treeview(tree_container.inner_frame, columns=("Nome", "Carga Horária", "Disciplinas", "Sala Preferencial"), show="headings", selectmode="browse")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Carga Horária", text="Carga Horária")
        self.tree.heading("Disciplinas", text="Disciplinas")
        self.tree.heading("Sala Preferencial", text="Sala Preferencial")
        self.tree.column("Nome", width=100)
        self.tree.column("Carga Horária", width=100)
        self.tree.column("Disciplinas", width=200)
        self.tree.column("Sala Preferencial", width=100)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected_turma)

    def update_sala_options(self):
        """Atualiza as opções do Combobox de salas com as salas atualmente cadastradas."""
        # Acessa o SalaManager através do controller para obter a lista de salas.
        salas: List[Sala] = self.controller.sala_manager.salas
        sala_numeros = [s.numero for s in salas]
        self.sala_preferencial_combobox["values"] = sala_numeros
        if sala_numeros: # Seleciona a primeira sala por padrão se houver.
            self.sala_preferencial_combobox.set(sala_numeros[0])
        else:
            self.sala_preferencial_combobox.set("") # Limpa se não houver salas.

    def update_treeview(self):
        """Atualiza a exibição da Treeview com os dados atuais das turmas."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        for turma in self.turmas:
            self.tree.insert("", "end", values=(turma.nome, turma.carga_horaria, ", ".join(turma.disciplinas), turma.sala_preferencial))

    def add_turma(self):
        """Adiciona uma nova turma à lista e salva no CSV."""
        nome = self.nome_entry.get().strip()
        carga_horaria_str = self.carga_horaria_entry.get().strip()
        disciplinas_str = self.disciplinas_entry.get().strip()
        sala_preferencial = self.sala_preferencial_combobox.get().strip() # Pega o valor do Combobox

        if not nome or not carga_horaria_str or not disciplinas_str or not sala_preferencial:
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios para adicionar uma turma.")
            return

        try:
            carga_horaria = int(carga_horaria_str)
        except ValueError:
            messagebox.showwarning("Aviso", "Carga Horária deve ser um número inteiro.")
            return

        # Normaliza as disciplinas para comparação (ordenadas e sem espaços extras)
        disciplinas = sorted([d.strip() for d in disciplinas_str.split(",") if d.strip()])

        if any(t.nome == nome for t in self.turmas):
            messagebox.showwarning("Aviso", f"Turma com o nome \'{nome}\' já existe.")
            return
        
        # Validação da sala preferencial
        if sala_preferencial not in self.sala_preferencial_combobox["values"]:
            messagebox.showwarning("Aviso", f"A sala preferencial \'{sala_preferencial}\' não existe. Por favor, selecione uma sala válida.")
            return

        # NOVA VALIDAÇÃO: Regra de compartilhamento de sala
        # Permite até 2 turmas por sala, desde que tenham as mesmas disciplinas.
        turmas_na_sala = [t for t in self.turmas if t.sala_preferencial == sala_preferencial]
        
        if len(turmas_na_sala) >= 2:
            messagebox.showwarning("Aviso", "Sala já atingiu o limite de 2 turmas. Por gentileza escolha uma sala diferente.")
            return
        
        if len(turmas_na_sala) == 1:
            # Compara a lista de disciplinas da turma que já está na sala com a nova turma
            if sorted(turmas_na_sala[0].disciplinas) != disciplinas:
                messagebox.showwarning("Aviso", "Sala já ocupada por turma com disciplinas diferentes. Por gentileza escolha uma sala diferente ou ajuste as disciplinas.")
                return

        new_turma = Turma(nome, carga_horaria, disciplinas, sala_preferencial)
        self.turmas.append(new_turma)
        self.save_turmas()
        self.update_treeview()
        self.clear_fields()
        messagebox.showinfo("Sucesso", f"Turma \'{nome}\' adicionada com sucesso.")

    def update_turma(self):
        """Atualiza os dados de uma turma existente e salva no CSV."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma turma para atualizar.")
            return

        old_nome = self.tree.item(selected_item, "values")[0]
        nome = self.nome_entry.get().strip()
        carga_horaria_str = self.carga_horaria_entry.get().strip()
        disciplinas_str = self.disciplinas_entry.get().strip()
        sala_preferencial = self.sala_preferencial_combobox.get().strip()

        if not nome or not carga_horaria_str or not disciplinas_str or not sala_preferencial:
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios para atualizar uma turma.")
            return

        try:
            carga_horaria = int(carga_horaria_str)
        except ValueError:
            messagebox.showwarning("Aviso", "Carga Horária deve ser um número inteiro.")
            return

        disciplines = sorted([d.strip() for d in disciplinas_str.split(",") if d.strip()])

        # Encontra a turma original que está sendo atualizada
        original_turma = next((t for t in self.turmas if t.nome == old_nome), None)
        if not original_turma:
            messagebox.showwarning("Erro", "Turma original não encontrada para atualização.")
            return

        # Validação de nome duplicado (se o nome for alterado)
        if nome != old_nome and any(t.nome == nome for t in self.turmas if t.nome != old_nome):
            messagebox.showwarning("Aviso", f"Turma com o nome \'{nome}\' já existe.")
            return
        
        # Validação da sala preferencial
        if sala_preferencial not in self.sala_preferencial_combobox["values"]:
            messagebox.showwarning("Aviso", f"A sala preferencial \'{sala_preferencial}\' não existe. Por favor, selecione uma sala válida.")
            return

        # Regra de compartilhamento de sala (ao atualizar)
        # Exclui a turma que está sendo atualizada da lista de turmas na sala para evitar auto-conflito
        turmas_na_sala_sem_atual = [t for t in self.turmas if t.sala_preferencial == sala_preferencial and t.nome != old_nome]
        
        # A validação de ocupação da sala só deve ser aplicada se:
        # 1. A sala preferencial mudou
        # OU
        # 2. A sala preferencial não mudou, mas as disciplinas mudaram E a sala já tem outras turmas.
        
        # Cenário 1: A sala preferencial mudou
        if sala_preferencial != original_turma.sala_preferencial:
            if len(turmas_na_sala_sem_atual) >= 2:
                messagebox.showwarning("Aviso", "Sala já atingiu o limite de 2 turmas. Por gentileza escolha uma sala diferente.")
                return
            
            if len(turmas_na_sala_sem_atual) == 1:
                if sorted(turmas_na_sala_sem_atual[0].disciplinas) != disciplines:
                    messagebox.showwarning("Aviso", "Sala já ocupada por turma com disciplinas diferentes. Por gentileza escolha uma sala diferente ou ajuste as disciplinas.")
                    return
        # Cenário 2: A sala preferencial não mudou, mas as disciplinas mudaram E há outras turmas na sala
        elif disciplines != sorted(original_turma.disciplinas) and len(turmas_na_sala_sem_atual) > 0:
            if len(turmas_na_sala_sem_atual) >= 2:
                messagebox.showwarning("Aviso", "Sala já atingiu o limite de 2 turmas. Por gentileza escolha uma sala diferente.")
                return
            
            if len(turmas_na_sala_sem_atual) == 1:
                if sorted(turmas_na_sala_sem_atual[0].disciplinas) != disciplines:
                    messagebox.showwarning("Aviso", "Sala já ocupada por turma com disciplinas diferentes. Por gentileza escolha uma sala diferente ou ajuste as disciplinas.")
                    return

        # Se passou pelas validações, atualiza a turma
        for i, turma in enumerate(self.turmas):
            if turma.nome == old_nome:
                self.turmas[i].nome = nome
                self.turmas[i].carga_horaria = carga_horaria
                self.turmas[i].disciplinas = disciplines
                self.turmas[i].sala_preferencial = sala_preferencial
                break
        self.save_turmas()
        self.update_treeview()
        self.clear_fields()
        messagebox.showinfo("Sucesso", f"Turma \'{nome}\' atualizada com sucesso.")

    def delete_turma(self):
        """Deleta uma turma da lista e salva no CSV."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma turma para deletar.")
            return

        nome_to_delete = self.tree.item(selected_item, "values")[0]
        if messagebox.askyesno("Confirmar Deleção", f"Tem certeza que deseja deletar a turma \'{nome_to_delete}\'?"):
            self.turmas = [t for t in self.turmas if t.nome != nome_to_delete]
            self.save_turmas()
            self.update_treeview()
            self.clear_fields()
            messagebox.showinfo("Sucesso", f"Turma \'{nome_to_delete}\' deletada com sucesso.")

    def load_selected_turma(self, event):
        """Carrega os dados da turma selecionada na Treeview para os campos de entrada."""
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            self.nome_entry.delete(0, tk.END)
            self.nome_entry.insert(0, values[0])
            self.carga_horaria_entry.delete(0, tk.END)
            self.carga_horaria_entry.insert(0, values[1])
            self.disciplinas_entry.delete(0, tk.END)
            self.disciplinas_entry.insert(0, values[2])
            self.sala_preferencial_combobox.set(values[3]) # Define o valor do Combobox

    def clear_fields(self):
        """Limpa todos os campos de entrada de dados."""
        self.nome_entry.delete(0, tk.END)
        self.carga_horaria_entry.delete(0, tk.END)
        self.disciplinas_entry.delete(0, tk.END)
        self.sala_preferencial_combobox.set("") # Limpa o Combobox

    def show_info(self):
        msg = (
            "Como adicionar uma Turma:\n\n"
            "• Nome: Digite o nome da turma (ex: 1º Ano A).\n"
            "• Carga Horária: Informe um número inteiro representando o total de aulas.\n"
            "• Disciplinas: Informe as disciplinas separadas por vírgula (ex: Matemática, Física).\n"
            "• Sala Preferencial: Selecione a sala onde a turma terá a maioria das aulas.\n\n"
            "Nota: Uma sala suporta no máximo 2 turmas desde que tenham as mesmas disciplinas."
        )
        messagebox.showinfo("Informação - Turmas", msg)
