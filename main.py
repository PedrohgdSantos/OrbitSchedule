import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

# Importa as classes e funções necessárias dos outros módulos do projeto.
from data_handler import DataHandler
from scheduler import Scheduler
from professor_manager import ProfessorManager
from turma_manager import TurmaManager
from sala_manager import SalaManager
from models import Aula # Importa Aula para tipagem da grade

# Define a classe principal da aplicação GUI.
class SchedulerApp:
    def __init__(self, root):
        """Inicializa a aplicação Tkinter."""
        self.root = root  # A janela principal da aplicação.
        self.root.title("Organizador de Horários - White Label")  # Define o título da janela.
        self.root.geometry("900x700")  # Define o tamanho inicial da janela.
        
        self.notebook = ttk.Notebook(self.root) # Cria um widget de notebook (abas).
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.grade_gerada: List[Aula] = [] # Armazena a última grade gerada.

        self.create_main_tab() # Cria a aba principal para geração de grade.
        self.create_professor_tab() # Cria a aba para gerenciamento de professores.
        self.create_sala_tab() # Cria a aba para gerenciamento de salas (precisa ser antes de turma para o combobox).
        self.create_turma_tab() # Cria a aba para gerenciamento de turmas.

    def create_main_tab(self):
        """Cria a aba principal para a geração e visualização da grade horária."""
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="Gerar Grade Horária")

        # Cabeçalho da aplicação.
        header = ttk.Label(main_frame, text="Gerador de Grade Horária Acadêmica", font=("Arial", 18, "bold"))
        header.pack(pady=10)

        # Frame para botões de ação da grade.
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(pady=10)

        ttk.Button(action_frame, text="Gerar Grade", command=self.gerar_grade, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(action_frame, text="Exportar Grade CSV", command=self.exportar_grade).pack(side="left", padx=5)
        ttk.Button(action_frame, text="ℹ️ Como usar", command=self.show_info_main).pack(side="left", padx=5)

        # Área para exibir alertas e status.
        alert_frame = ttk.LabelFrame(main_frame, text="Alertas e Status", padding="10")
        alert_frame.pack(pady=10, padx=10, fill="x")
        self.alert_text = tk.Text(alert_frame, height=5, font=("Consolas", 10))
        self.alert_text.pack(fill="x", expand=True)
        self.alert_text.config(state=tk.DISABLED) # Torna o campo de texto somente leitura.

        # Treeview para exibir a grade horária gerada.
        grade_frame = ttk.LabelFrame(main_frame, text="Grade Horária Gerada", padding="10")
        grade_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.grade_tree = ttk.Treeview(grade_frame, columns=("Dia", "Horário", "Bloco", "Turma", "Disciplina", "Professor", "Sala"), show="headings")
        self.grade_tree.heading("Dia", text="Dia")
        self.grade_tree.heading("Horário", text="Horário")
        self.grade_tree.heading("Bloco", text="Bloco")
        self.grade_tree.heading("Turma", text="Turma")
        self.grade_tree.heading("Disciplina", text="Disciplina")
        self.grade_tree.heading("Professor", text="Professor")
        self.grade_tree.heading("Sala", text="Sala")

        # Ajusta a largura das colunas
        self.grade_tree.column("Dia", width=80, anchor="center")
        self.grade_tree.column("Horário", width=70, anchor="center")
        self.grade_tree.column("Bloco", width=70, anchor="center")
        self.grade_tree.column("Turma", width=100)
        self.grade_tree.column("Disciplina", width=150)
        self.grade_tree.column("Professor", width=150)
        self.grade_tree.column("Sala", width=70, anchor="center")

        self.grade_tree.pack(side="left", fill="both", expand=True)

        # Adiciona barra de rolagem à Treeview.
        scrollbar = ttk.Scrollbar(grade_frame, orient="vertical", command=self.grade_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.grade_tree.config(yscrollcommand=scrollbar.set)

    def create_professor_tab(self):
        """Cria a aba para gerenciamento de professores."""
        professor_frame = ttk.Frame(self.notebook)
        self.notebook.add(professor_frame, text="Gerenciar Professores")
        self.professor_manager = ProfessorManager(professor_frame, self) # Instancia o ProfessorManager.
        self.professor_manager.pack(expand=True, fill="both")

    def create_turma_tab(self):
        """Cria a aba para gerenciamento de turmas."""
        turma_frame = ttk.Frame(self.notebook)
        self.notebook.add(turma_frame, text="Gerenciar Turmas")
        self.turma_manager = TurmaManager(turma_frame, self) # Instancia o TurmaManager.
        self.turma_manager.pack(expand=True, fill="both")

    def create_sala_tab(self):
        """Cria a aba para gerenciamento de salas."""
        sala_frame = ttk.Frame(self.notebook)
        self.notebook.add(sala_frame, text="Gerenciar Salas")
        self.sala_manager = SalaManager(sala_frame, self) # Instancia o SalaManager.
        self.sala_manager.pack(expand=True, fill="both")

    def update_alert_text(self, message, append=False):
        """Atualiza a área de texto de alertas."""
        self.alert_text.config(state=tk.NORMAL) # Habilita edição temporariamente.
        if not append:
            self.alert_text.delete(1.0, tk.END)
        self.alert_text.insert(tk.END, message)
        self.alert_text.config(state=tk.DISABLED) # Desabilita edição novamente.
        self.alert_text.see(tk.END) # Rola para o final do texto.

    def gerar_grade(self):
        """Carrega dados dos managers, gera a grade e exibe na Treeview."""
        self.update_alert_text("Iniciando geração da grade horária...\n")
        try:
            # Carregar dados diretamente dos managers, que já carregam dos CSVs.
            professores = self.professor_manager.professores
            turmas = self.turma_manager.turmas
            salas = self.sala_manager.salas

            if not professores or not turmas or not salas:
                messagebox.showwarning("Aviso", "Certifique-se de ter Professores, Turmas e Salas cadastrados.")
                self.update_alert_text("⚠️ Erro: Dados insuficientes para gerar a grade.\n", append=True)
                return

            # Cria uma instância do Scheduler e gera a grade horária.
            scheduler = Scheduler(professores, turmas, salas)
            self.grade_gerada = scheduler.gerar_grade()
            alertas = scheduler.get_alertas()

            # Limpa a Treeview da grade.
            for i in self.grade_tree.get_children():
                self.grade_tree.delete(i)

            # Exibe a grade gerada na Treeview.
            if self.grade_gerada:
                for aula in self.grade_gerada:
                    self.grade_tree.insert("", "end", values=(
                        aula.dia, f"{aula.horario}º Horário", aula.bloco, 
                        aula.turma, aula.disciplina, aula.professor, aula.sala
                    ))
                self.update_alert_text("✅ SUCESSO: Grade horária gerada e exibida!\n", append=True)
            else:
                self.update_alert_text("⚠️ ATENÇÃO: Nenhuma aula foi gerada. Verifique os dados de entrada.\n", append=True)

            # Exibe os alertas gerados pelo Scheduler na área de texto.
            if alertas:
                self.update_alert_text("\n⚠️ ATENÇÃO: Foram encontrados problemas na alocação:\n\n", append=True)
                for alerta in alertas:
                    self.update_alert_text(f"• {alerta}\n", append=True)
            else:
                self.update_alert_text("\n✅ Nenhuma conflito de professor encontrado durante a geração.\n", append=True)

        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Ocorreu um erro ao gerar a grade:\n{str(e)}")
            self.update_alert_text(f"❌ Erro crítico: {str(e)}\n", append=True)

    def exportar_grade(self):
        """Permite ao usuário exportar a grade horária atualmente exibida para um arquivo CSV."""
        if not self.grade_gerada:
            messagebox.showwarning("Aviso", "Nenhuma grade horária foi gerada para exportar.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv", 
            filetypes=[("CSV files", "*.csv")], 
            title="Salvar Grade Horária Gerada",
            initialfile="grade_horaria_gerada.csv"
        )
        if save_path:
            try:
                DataHandler.save_grade(save_path, self.grade_gerada)
                messagebox.showinfo("Exportação Concluída", f"A grade horária foi salva com sucesso em:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Erro de Exportação", f"Ocorreu um erro ao salvar a grade:\n{str(e)}")

    def show_info_main(self):
        msg = (
            "Para gerar a grade horária corretamente, siga estes passos:\n\n"
            "1. Cadastre os Professores, Turmas e Salas nas abas correspondentes.\n"
            "2. Certifique-se de que as disciplinas dos professores correspondem às disciplinas das turmas.\n"
            "3. Clique em 'Gerar Grade' para criar o horário.\n"
            "4. Se houver alertas ou erros, verifique os dados cadastrados e tente novamente."
        )
        messagebox.showinfo("Como usar - Gerar Grade Horária", msg)

# Bloco principal de execução do script.
if __name__ == "__main__":
    root = tk.Tk()  # Cria a janela principal do Tkinter.
    # Configura um estilo para os botões, incluindo um estilo de destaque.
    style = ttk.Style()
    style.theme_use("clam") # Ou "default", "alt", "classic"
    style.configure("Accent.TButton", background="#28a745", foreground="white", font=("Arial", 11, "bold"))
    style.map("Accent.TButton", background=[("active", "#218838")])

    app = SchedulerApp(root)  # Instancia a aplicação.
    root.mainloop()  # Inicia o loop de eventos do Tkinter, mantendo a janela aberta e responsiva.
