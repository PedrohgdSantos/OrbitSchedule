import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from typing import List

from .rounded_frame import RoundedFrame
# Importa as classes e funções necessárias dos outros módulos do projeto.
from .data_handler import DataHandler
from .scheduler import Scheduler
from .professor_manager import ProfessorManager
from .turma_manager import TurmaManager
from .sala_manager import SalaManager
from .models import Aula # Importa Aula para tipagem da grade

# Define a classe principal da aplicação GUI.
class SchedulerApp:
    def __init__(self, root):
        """Inicializa a aplicação Tkinter."""
        self.root = root  # A janela principal da aplicação.
        self.root.title("Organizador de Horários")  # Define o título da janela.
        self.root.geometry("900x700")  # Define o tamanho inicial da janela.
        self.root.configure(bg="#050608")

        self.style = ttk.Style()
        self.configure_style()

        self.notebook = ttk.Notebook(self.root, style="App.TNotebook") # Cria um widget de notebook (abas).
        self.notebook.pack(expand=True, fill="both", padx=10, pady=(10, 5))

        self.grade_gerada: List[Aula] = [] # Armazena a última grade gerada.

        self.create_main_tab() # Cria a aba principal para geração de grade.
        self.create_professor_tab() # Cria a aba para gerenciamento de professores.
        self.create_sala_tab() # Cria a aba para gerenciamento de salas (precisa ser antes de turma para o combobox).
        self.create_turma_tab() # Cria a aba para gerenciamento de turmas.

        self.update_dashboard_summary()

        self.status_var = tk.StringVar(value="Pronto para gerar a grade.")
        self.status_separator = ttk.Separator(self.root, orient="horizontal")
        self.status_separator.pack(fill="x", padx=10, pady=(0, 0))
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, anchor="w", style="Status.TLabel")
        self.status_label.pack(fill="x", padx=10, pady=(4, 10))
        self.start_ui_animation()

    def configure_style(self):
        """Configura o tema e os estilos globais da aplicação."""
        self.style.theme_use("clam")
        self.style.configure(".", background="#0F172A", foreground="#E2E8F0", font=("Segoe UI", 10))
        self.style.configure("TFrame", background="#0F172A")
        self.style.configure("App.TFrame", background="#0F172A")
        self.style.configure("Rounded.TFrame", background="#111827", borderwidth=0, relief="flat")
        self.style.configure("Card.TFrame", background="#111827", borderwidth=1, relief="flat")
        self.style.configure("CardAccent.TFrame", background="#1D4ED8", borderwidth=0, relief="flat")
        self.style.configure("TLabelframe", background="#111827", borderwidth=0)
        self.style.configure("TLabelframe.Label", background="#111827", foreground="#E2E8F0")
        self.style.configure("CardHeader.TLabel", background="#111827", foreground="#94A3B8", font=("Segoe UI", 10, "bold"))
        self.style.configure("CardMetric.TLabel", background="#111827", foreground="#F8FAFC", font=("Segoe UI", 18, "bold"))
        self.style.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), background="#0F172A", foreground="#F8FAFC")
        self.style.configure("Subheader.TLabel", font=("Segoe UI", 10), background="#0F172A", foreground="#94A3B8")
        self.style.configure("Info.TLabel", background="#0F172A", foreground="#CBD5E1", font=("Segoe UI", 10))
        self.style.configure("Status.TLabel", background="#020617", foreground="#94A3B8", padding=(10, 6), font=("Segoe UI", 9))
        self.style.configure("Accent.TButton", background="#22C55E", foreground="#0F172A", font=("Segoe UI", 10, "bold"), padding=10, borderwidth=0)
        self.style.map("Accent.TButton", background=[("active", "#16A34A"), ("disabled", "#84CC16")], foreground=[("active", "#F8FAFC")])
        self.style.configure("Secondary.TButton", background="#2563EB", foreground="#FFFFFF", font=("Segoe UI", 10), padding=10, borderwidth=0)
        self.style.map("Secondary.TButton", background=[("active", "#1D4ED8")], foreground=[("active", "#FFFFFF")])
        self.style.configure("Danger.TButton", background="#EF4444", foreground="#FFFFFF", padding=10, borderwidth=0)
        self.style.map("Danger.TButton", background=[("active", "#DC2626")])
        self.style.configure("Card.TLabelframe", background="#111827", bordercolor="#1F2937", borderwidth=1, relief="flat")
        self.style.configure("Card.TLabelframe.Label", background="#111827", foreground="#E2E8F0", font=("Segoe UI", 11, "bold"))
        self.style.configure("Treeview", background="#111827", fieldbackground="#111827", foreground="#E2E8F0", rowheight=28, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", background="#1F2937", foreground="#E2E8F0", font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", background=[("selected", "#2563EB")], foreground=[("selected", "#FFFFFF")])
        self.style.configure("App.TNotebook", background="#0F172A", borderwidth=0)
        self.style.configure("TNotebook", background="#0F172A", borderwidth=0)
        self.style.configure("TNotebook.Tab", padding=[14, 12], font=("Segoe UI", 10, "bold"), background="#111827", foreground="#CBD5E1")
        self.style.map("TNotebook.Tab", background=[("selected", "#2563EB")], foreground=[("selected", "#FFFFFF")])
        self.style.configure("TButton", padding=8, relief="flat")
        self.style.configure("TLabel", background="#0F172A", foreground="#E2E8F0")
        self.style.configure("TEntry", fieldbackground="#111827", background="#111827", foreground="#E2E8F0", insertcolor="#F8FAFC", padding=8)
        self.style.configure("TCombobox", fieldbackground="#111827", background="#111827", foreground="#E2E8F0")
        self.style.configure("TCheckbutton", background="#0F172A", foreground="#E2E8F0")

    def create_main_tab(self):
        """Cria a aba principal para a geração e visualização da grade horária."""
        main_frame = ttk.Frame(self.notebook, style="App.TFrame")
        self.notebook.add(main_frame, text="Gerar Grade Horária")

        # Cabeçalho da aplicação.
        header = ttk.Label(main_frame, text="Gerador de Grade Horária Acadêmica", style="Header.TLabel")
        header.pack(pady=(16, 2), padx=10, anchor="w")
        subheader = ttk.Label(main_frame, text="Organize horários com visual moderno e intuitivo.", style="Subheader.TLabel")
        subheader.pack(padx=10, anchor="w")

        # Painel de métricas rápidas.
        stats_frame = ttk.Frame(main_frame, style="App.TFrame")
        stats_frame.pack(fill="x", padx=10, pady=(14, 10))

        self.dashboard_labels = {}
        self.stats_cards = []
        stats = [
            ("Professores", "0"),
            ("Turmas", "0"),
            ("Salas", "0"),
            ("Aulas geradas", "0"),
        ]
        for title, value in stats:
            card = RoundedFrame(stats_frame, bg_color="#111827", border_color="#4F46E5", corner_radius=18, padding=14)
            card.pack(side="left", expand=True, fill="both", padx=5)
            self.stats_cards.append(card)
            ttk.Label(card.inner_frame, text=title, style="CardHeader.TLabel").pack(anchor="w")
            label_value = ttk.Label(card.inner_frame, text=value, style="CardMetric.TLabel")
            label_value.pack(anchor="w", pady=(10, 0))
            self.dashboard_labels[title] = label_value

        # Frame para botões de ação da grade.
        self.action_frame = RoundedFrame(main_frame, bg_color="#111827", border_color="#1F2937", corner_radius=20, padding=14)
        self.action_frame.pack(padx=10, pady=10, fill="x")

        ttk.Button(self.action_frame.inner_frame, text="Gerar Grade", command=self.gerar_grade, style="Accent.TButton").pack(side="left", padx=6)
        ttk.Button(self.action_frame.inner_frame, text="Exportar Grade CSV", command=self.exportar_grade, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(self.action_frame.inner_frame, text="Zerar Aulas", command=self.clear_grade, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(self.action_frame.inner_frame, text="ℹ️ Como usar", command=self.show_info_main, style="Secondary.TButton").pack(side="left", padx=6)

        self.grade_summary_label = ttk.Label(main_frame, text="Nenhuma grade gerada ainda.", style="Info.TLabel")
        self.grade_summary_label.pack(padx=10, pady=(4, 0), anchor="w")

        # Área para exibir alertas e status.
        ttk.Label(main_frame, text="Alertas e Status", style="CardHeader.TLabel").pack(padx=10, pady=(14, 4), anchor="w")
        self.alert_container = RoundedFrame(main_frame, bg_color="#111827", border_color="#1F2937", corner_radius=18, padding=14)
        self.alert_container.pack(pady=0, padx=10, fill="x")
        self.alert_text = tk.Text(self.alert_container.inner_frame, height=5, font=("Consolas", 10), relief="flat", bg="#111827", fg="#E2E8F0", bd=0)
        self.alert_text.pack(fill="x", expand=True)
        self.alert_text.config(state=tk.DISABLED) # Torna o campo de texto somente leitura.

        # Treeview para exibir a grade horária gerada.
        ttk.Label(main_frame, text="Grade Horária Gerada", style="CardHeader.TLabel").pack(padx=10, pady=(16, 4), anchor="w")
        self.grade_container = RoundedFrame(main_frame, bg_color="#111827", border_color="#1F2937", corner_radius=18, padding=14)
        self.grade_container.pack(pady=0, padx=10, fill="both", expand=True)

        self.grade_tree = ttk.Treeview(self.grade_container.inner_frame, columns=("Dia", "Horário", "Bloco", "Turma", "Disciplina", "Professor", "Sala"), show="headings", selectmode="browse")
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

        self.grade_tree.tag_configure("oddrow", background="#111827")
        self.grade_tree.tag_configure("evenrow", background="#0F172A")
        self.grade_tree.pack(side="left", fill="both", expand=True)

        self.update_dashboard_summary()

        # Adiciona barra de rolagem à Treeview.
        scrollbar = ttk.Scrollbar(self.grade_container.inner_frame, orient="vertical", command=self.grade_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.grade_tree.config(yscrollcommand=scrollbar.set)

    def create_professor_tab(self):
        """Cria a aba para gerenciamento de professores."""
        professor_frame = ttk.Frame(self.notebook, style="App.TFrame")
        self.notebook.add(professor_frame, text="Gerenciar Professores")
        self.professor_manager = ProfessorManager(professor_frame, self) # Instancia o ProfessorManager.
        self.professor_manager.pack(expand=True, fill="both")

    def create_turma_tab(self):
        """Cria a aba para gerenciamento de turmas."""
        turma_frame = ttk.Frame(self.notebook, style="App.TFrame")
        self.notebook.add(turma_frame, text="Gerenciar Turmas")
        self.turma_manager = TurmaManager(turma_frame, self) # Instancia o TurmaManager.
        self.turma_manager.pack(expand=True, fill="both")

    def create_sala_tab(self):
        """Cria a aba para gerenciamento de salas."""
        sala_frame = ttk.Frame(self.notebook, style="App.TFrame")
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

    def start_ui_animation(self):
        """Inicia a animação contínua dos elementos visuais."""
        self.animation_phase = 0.0
        self.animate_ui()

    def animate_ui(self):
        """Executa um passo da animação de interface e agenda o próximo."""
        pulse = (math.sin(self.animation_phase) + 1) / 2
        border_base = (31, 41, 55)
        border_light = 18
        r = min(255, max(0, int(border_base[0] + border_light * pulse)))
        g = min(255, max(0, int(border_base[1] + border_light * pulse)))
        b = min(255, max(0, int(border_base[2] + border_light * pulse)))
        border_color = f"#{r:02x}{g:02x}{b:02x}"

        for frame in [self.action_frame, self.alert_container, self.grade_container] + self.stats_cards:
            if hasattr(frame, 'set_border_color'):
                frame.set_border_color(border_color)

        status_base = (8, 19, 43)
        status_light = 10
        sr = min(255, max(0, int(status_base[0] + status_light * pulse)))
        sg = min(255, max(0, int(status_base[1] + status_light * pulse)))
        sb = min(255, max(0, int(status_base[2] + status_light * pulse)))
        self.status_label.config(background=f"#{sr:02x}{sg:02x}{sb:02x}")

        self.animation_phase += 0.15
        self.root.after(80, self.animate_ui)

    def update_dashboard_summary(self):
        """Atualiza os cartões de métricas do painel principal."""
        professores = len(self.professor_manager.professores) if hasattr(self, 'professor_manager') else 0
        turmas = len(self.turma_manager.turmas) if hasattr(self, 'turma_manager') else 0
        salas = len(self.sala_manager.salas) if hasattr(self, 'sala_manager') else 0
        aulas = len(self.grade_gerada) if hasattr(self, 'grade_gerada') else 0

        self.dashboard_labels["Professores"].config(text=str(professores))
        self.dashboard_labels["Turmas"].config(text=str(turmas))
        self.dashboard_labels["Salas"].config(text=str(salas))
        self.dashboard_labels["Aulas geradas"].config(text=str(aulas))

    def set_status(self, message: str):
        """Atualiza a barra de status inferior."""
        self.status_var.set(message)

    def gerar_grade(self):
        """Carrega dados dos managers, gera a grade e exibe na Treeview."""
        self.set_status("Gerando grade horária...")
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
                for index, aula in enumerate(self.grade_gerada):
                    tag = "evenrow" if index % 2 == 0 else "oddrow"
                    self.grade_tree.insert("", "end", values=(
                        aula.dia, f"{aula.horario}º Horário", aula.bloco, 
                        aula.turma, aula.disciplina, aula.professor, aula.sala
                    ), tags=(tag,))
                self.update_alert_text("✅ SUCESSO: Grade horária gerada e exibida!\n", append=True)
                self.grade_summary_label.config(text=f"{len(self.grade_gerada)} aulas geradas.")
                self.set_status(f"Grade gerada com sucesso: {len(self.grade_gerada)} aulas alocadas.")
                self.update_dashboard_summary()
            else:
                self.update_alert_text("⚠️ ATENÇÃO: Nenhuma aula foi gerada. Verifique os dados de entrada.\n", append=True)
                self.grade_summary_label.config(text="Nenhuma aula gerada.")
                self.set_status("Não foi possível gerar a grade. Verifique os dados.")
                self.update_dashboard_summary()

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

    def clear_grade(self):
        """Limpa a grade gerada da interface e zera a lista de aulas."""
        self.grade_gerada = []
        for i in self.grade_tree.get_children():
            self.grade_tree.delete(i)
        self.grade_summary_label.config(text="Nenhuma aula gerada.")
        self.update_dashboard_summary()
        self.set_status("Aulas geradas zeradas.")
        self.update_alert_text("Grade horária limpa. Gere novamente se desejar.\n", append=False)

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
    app = SchedulerApp(root)  # Instancia a aplicação.
    root.mainloop()  # Inicia o loop de eventos do Tkinter, mantendo a janela aberta e responsiva.
