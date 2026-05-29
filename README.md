# OrbitSchedule

Um projeto de gerenciamento escolar em Python com interface gráfica Tkinter. O objetivo é transformar cadastros de professores, turmas e salas em uma grade horária gerada automaticamente.

---

## 🚀 Por que usar o OrbitSchedule?

- Crie e ajuste a base de dados de professores, turmas e salas com facilidade.
- Gere uma grade horária automaticamente com regras de disponibilidade e conflitos.
- Exporte o resultado para CSV e compartilhe com a equipe.
- Interface moderna com animações suaves e navegação por abas.

---

## ✨ O que você encontra aqui

- Cadastro e edição de:
  - Professores
  - Turmas
  - Salas
- Geração de grade horária automática
- Visualização clara da grade no app
- Exportação da grade para CSV
- Botão de limpeza para resetar a geração atual
- Alertas de conflitos e inconsistências

---

## 📌 Como funciona

1. Abra o app com `python main.py`.
2. Preencha os dados em cada aba:
   - `Professores`
   - `Turmas`
   - `Salas`
3. Clique em `Gerar Grade` para montar a distribuição de aulas.
4. Confira os resultados na tabela e, se quiser, exporte o CSV.
5. Use `Zerar Aulas` para limpar a grade atual e gerar novamente.

---

## 🧩 Estrutura do projeto

- `main.py` — arquivo de entrada que inicia a aplicação
- `src/` — código-fonte do projeto
  - `src/app.py` — interface principal e orquestração da aplicação
  - `src/data_handler.py` — leitura e gravação de arquivos CSV
  - `src/scheduler.py` — algoritmo que monta a grade horária
  - `src/models.py` — definição das classes de dados
  - `src/professor_manager.py` — cadastro e edição de professores
  - `src/sala_manager.py` — cadastro e edição de salas
  - `src/turma_manager.py` — cadastro e edição de turmas
  - `src/rounded_frame.py` — componentes visuais com bordas arredondadas

---

## 📁 Estrutura de dados

Os dados ficam em `data/` nos arquivos:

- `professores.csv`
- `turmas.csv`
- `salas.csv`

Use `data/` para manter os registros persistentes entre execuções.

---

## ✅ Requisitos

- Python 3.10 ou superior
- Tkinter instalado (normalmente já vem com o Python)

---

## ▶️ Como rodar

No terminal, dentro da pasta do projeto:

```bash
python main.py
```
---

## 💡 O que o Scheduler faz

O algoritmo cria a grade considerando:

- disponibilidade dos professores
- disciplinas associadas à turma
- conflitos de horário entre professores
- preferência de sala para cada turma
- alertas quando não há solução ideal

---

## 🌱 Próximos passos sugeridos

- adicionar mais regras de alocação por carga horária
- permitir múltiplas salas por turma
- melhorar o algoritmo de balanceamento de professores
- incluir filtros e buscas na interface
- criar testes automatizados para validação

---

## 📬 Observações finais

OrbitSchedule é um ponto de partida para quem precisa criar grades escolares com rapidez e controle. O código já está estruturado para evoluir com novas regras e melhorias na interface.
