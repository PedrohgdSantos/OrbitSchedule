# OrbitSchedule — Documentação Técnica

## Visão Geral

**OrbitSchedule** é uma aplicação desktop em Python (Tkinter) para gestão e geração automática de grades horárias escolares, com módulo integrado de controle de faltas de professores.

### Funcionalidades principais

- Cadastro de professores, turmas e salas com persistência em CSV
- Geração automática de grade horária com detecção de conflitos
- Exportação da grade para CSV compatível com Excel
- Registro e acompanhamento de faltas de professores
- Relatório de validação com destaque visual em vermelho para horários vagos
- Exportação de relatório de faltas para a Secretaria

---

## Estrutura do Projeto

```
OrbitSchedule/
├── main.py                  # Ponto de entrada da aplicação
├── src/
│   ├── app.py               # Shell principal: sidebar + roteamento de páginas
│   ├── models.py            # Dataclasses: Professor, Turma, Sala, Aula, Falta
│   ├── data_handler.py      # Leitura e escrita de todos os arquivos CSV
│   ├── scheduler.py         # Algoritmo de geração da grade horária
│   ├── professor_manager.py # Página de gerenciamento de professores
│   ├── turma_manager.py     # Página de gerenciamento de turmas
│   ├── sala_manager.py      # Página de gerenciamento de salas
│   ├── absence_manager.py   # Página de gestão de faltas e relatórios
│   └── rounded_frame.py     # Componente visual de card com bordas arredondadas
├── data/
│   ├── professores.csv
│   ├── turmas.csv
│   ├── salas.csv
│   └── faltas.csv           # Criado automaticamente ao registrar a primeira falta
└── docs/
    └── DOCUMENTATION.md
```

---

## Design System

A interface segue o padrão **Designo LMS Dashboard** (tema claro).

### Paleta de cores

| Token        | Hex       | Uso                                      |
|--------------|-----------|------------------------------------------|
| `BG_PAGE`    | `#F5F6FA` | Fundo geral das páginas                  |
| `BG_SIDEBAR` | `#FFFFFF` | Fundo da sidebar                         |
| `BG_CARD`    | `#FFFFFF` | Fundo dos cards e tabelas                |
| `ORANGE`     | `#F97316` | Cor primária: botões, nav ativo, logo    |
| `ORANGE_DIM` | `#FFF7ED` | Hover de nav e ícones de métricas        |
| `TEXT_DARK`  | `#111827` | Texto principal                          |
| `TEXT_MID`   | `#6B7280` | Labels secundários e subtítulos          |
| `BORDER`     | `#E5E7EB` | Bordas de cards e separadores            |
| `GREEN`      | `#16A34A` | Status "presente" / sucesso              |
| `GREEN_BG`   | `#DCFCE7` | Fundo do banner "está tudo certo"        |
| `RED`        | `#DC2626` | Faltas / erros / botão deletar           |
| `RED_BG`     | `#FEE2E2` | Highlight de linhas com falta            |
| `AMBER`      | `#D97706` | Indicador de alertas da semana           |

### Layout

A janela é dividida em duas colunas fixas:

- **Sidebar** (220 px, fixa): logo + itens de navegação
- **Área de conteúdo** (expansível): página ativa + barra de status no rodapé

A navegação é feita por clique nos itens da sidebar. O item ativo recebe fundo laranja sólido; os inativos respondem a hover com `ORANGE_DIM`.

---

## Módulos

### `main.py`

Ponto de entrada. Instancia `tk.Tk` e `SchedulerApp`, então inicia o loop de eventos.

```python
python main.py
```

---

### `src/app.py` — `SchedulerApp`

Shell da aplicação. Responsável por:

- Configurar todos os estilos TTK globais via `_configure_ttk_styles()`
- Montar o layout de duas colunas (`_build_shell()`)
- Construir a sidebar com navegação (`_build_sidebar()`)
- Instanciar e registrar todas as páginas (`_build_pages()`)
- Roteamento: `_navigate(page_key)` exibe a página selecionada e atualiza o estado visual da sidebar

**Páginas registradas:**

| `page_key`   | Classe              | Atributo             |
|--------------|---------------------|----------------------|
| `dashboard`  | *(interno)*         | —                    |
| `professores`| `ProfessorManager`  | `professor_manager`  |
| `turmas`     | `TurmaManager`      | `turma_manager`      |
| `salas`      | `SalaManager`       | `sala_manager`       |
| `faltas`     | `AbsenceManager`    | `absence_manager`    |

**Dashboard (página inicial):**

- 4 metric cards: Professores, Turmas, Salas, Aulas geradas
- Botões de ação: Gerar Grade, Exportar CSV, Limpar Grade
- Área de alertas do algoritmo
- Treeview com a grade gerada (linhas alternadas)

**Métodos públicos relevantes:**

| Método                    | Descrição                                              |
|---------------------------|--------------------------------------------------------|
| `gerar_grade()`           | Executa o `Scheduler` e popula a Treeview da grade     |
| `exportar_grade()`        | Abre diálogo e chama `DataHandler.save_grade()`        |
| `clear_grade()`           | Limpa grade da memória e da Treeview                   |
| `update_dashboard_summary()` | Sincroniza os metric cards com os dados atuais      |
| `set_status(message)`     | Atualiza o texto da barra de status inferior           |
| `update_alert_text(msg)`  | Escreve na área de alertas do dashboard                |

---

### `src/models.py` — Modelos de dados

Todos os modelos são `@dataclass`.

#### `Professor`
| Campo               | Tipo        | Descrição                                      |
|---------------------|-------------|------------------------------------------------|
| `nome`              | `str`       | Nome completo                                  |
| `disciplinas`       | `List[str]` | Disciplinas que pode lecionar                  |
| `disponibilidade`   | `List[str]` | Blocos disponíveis (ex: `Seg-Manhã`)           |
| `aulas_atribuidas`  | `int`       | Contador usado pelo scheduler para priorização |

#### `Turma`
| Campo               | Tipo        | Descrição                          |
|---------------------|-------------|------------------------------------|
| `nome`              | `str`       | Identificador da turma             |
| `carga_horaria`     | `int`       | Total de aulas semanais            |
| `disciplinas`       | `List[str]` | Disciplinas que a turma cursa      |
| `sala_preferencial` | `str`       | Sala onde a turma será alocada     |

#### `Sala`
| Campo           | Tipo   | Descrição                    |
|-----------------|--------|------------------------------|
| `numero`        | `str`  | Identificador único da sala  |
| `is_laboratorio`| `bool` | `True` se for laboratório    |

#### `Aula`
| Campo       | Tipo  | Descrição                            |
|-------------|-------|--------------------------------------|
| `dia`       | `str` | Dia da semana (ex: `Segunda`)        |
| `horario`   | `int` | Número do horário no dia (1–4)       |
| `bloco`     | `str` | `Manhã` ou `Noite`                   |
| `turma`     | `str` | Nome da turma                        |
| `disciplina`| `str` | Nome da disciplina                   |
| `professor` | `str` | Nome do professor                    |
| `sala`      | `str` | Número da sala                       |

#### `Falta`
| Campo          | Tipo  | Descrição                                      |
|----------------|-------|------------------------------------------------|
| `data`         | `str` | Data no formato `DD/MM/AAAA`                   |
| `professor`    | `str` | Nome do professor ausente                      |
| `dia_semana`   | `str` | Abreviação do dia (ex: `Seg`)                  |
| `bloco`        | `str` | Bloco inferido da grade (`Manhã`, `Noite`, `—`)|
| `horario`      | `str` | Horário inferido da grade ou `—`               |
| `motivo`       | `str` | Motivo informado ou `Não informado`            |
| `registrado_em`| `str` | Timestamp do registro (`DD/MM/AAAA HH:MM`)     |

---

### `src/data_handler.py` — `DataHandler`

Todos os métodos são estáticos. Responsável por toda I/O de CSV.

**Encoding:** todos os arquivos são lidos e gravados com `utf-8-sig` (UTF-8 com BOM), garantindo compatibilidade com Excel em qualquer sistema operacional.

**Separador de exportação:** os arquivos exportados ao usuário (`save_grade` e os exports de `AbsenceManager`) usam `;` como delimitador, padrão do Excel em locale português.

| Método                              | Arquivo alvo          | Descrição                                    |
|-------------------------------------|-----------------------|----------------------------------------------|
| `_read_csv(path)`                   | qualquer              | Lê CSV, retorna `List[dict]`                 |
| `_write_csv(path, data, fields)`    | qualquer              | Grava CSV interno (separador `,`)            |
| `load_professores(path)`            | `professores.csv`     | Retorna `List[Professor]`                    |
| `save_professores(path, lista)`     | `professores.csv`     | Persiste lista de professores                |
| `load_turmas(path)`                 | `turmas.csv`          | Retorna `List[Turma]`                        |
| `save_turmas(path, lista)`          | `turmas.csv`          | Persiste lista de turmas                     |
| `load_salas(path)`                  | `salas.csv`           | Retorna `List[Sala]`                         |
| `save_salas(path, lista)`           | `salas.csv`           | Persiste lista de salas                      |
| `load_faltas(path)`                 | `faltas.csv`          | Retorna `List[Falta]`                        |
| `save_faltas(path, lista)`          | `faltas.csv`          | Persiste lista de faltas                     |
| `save_grade(path, grade)`           | arquivo escolhido     | Exporta grade com separador `;`, UTF-8-BOM   |

---

### `src/scheduler.py` — `Scheduler`

Implementa o algoritmo de geração da grade.

**Constantes:**
- `DIAS`: `["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]`
- `HORARIOS`: `[1, 2, 3, 4]`
- `BLOCOS`: `["Manhã", "Noite"]`

**Lógica de `gerar_grade()`:**

1. Para cada turma, determina o bloco (`Manhã`/`Noite`) pelo nome
2. Para cada disciplina da turma, tenta alocar 4 aulas distribuídas nos 5 dias
3. Busca professor disponível via `_get_professores_disponiveis()`
4. Prioriza o professor com menor `aulas_atribuidas`
5. Registra alerta se nenhum professor puder ser alocado

**Regras de alocação:**
- O professor deve lecionar a disciplina solicitada
- O professor deve ter disponibilidade no `dia-bloco` correspondente
- O professor não pode estar ocupado no mesmo `dia + horário` (verificado por `_professor_ocupado()`)

---

### `src/professor_manager.py` — `ProfessorManager`

Página de CRUD de professores. Herda `tk.Frame`.

**Campos do formulário:**
- Nome
- Disciplinas (separadas por vírgula)
- Disponibilidade (ex: `Seg-Manhã, Ter-Noite`)

**Validações:**
- Todos os campos obrigatórios
- Nome único (sem duplicatas)

**Operações:** Adicionar, Atualizar, Deletar, Limpar campos. Seleção na Treeview preenche o formulário automaticamente.

---

### `src/turma_manager.py` — `TurmaManager`

Página de CRUD de turmas. Herda `tk.Frame`.

**Campos do formulário:**
- Nome
- Carga Horária (inteiro)
- Disciplinas (separadas por vírgula)
- Sala Preferencial (Combobox populado pelo `SalaManager`)

**Regra de sala compartilhada:**
- Máximo de 2 turmas por sala
- Se já houver 1 turma na sala, a nova deve ter exatamente as mesmas disciplinas

**Método público:** `update_sala_options()` — chamado automaticamente pelo `SalaManager` ao salvar alterações de salas.

---

### `src/sala_manager.py` — `SalaManager`

Página de CRUD de salas. Herda `tk.Frame`.

**Campos:** Número da sala + checkbox "É Laboratório?"

Ao salvar qualquer alteração, chama `TurmaManager.update_sala_options()` para manter o Combobox de salas sincronizado.

---

### `src/absence_manager.py` — `AbsenceManager`

Módulo completo de gestão de faltas. Herda `tk.Frame`.

#### Seções da página

**1. Dashboard de métricas**

Quatro cards atualizados em tempo real:

| Card              | Cálculo                                              |
|-------------------|------------------------------------------------------|
| Faltas Hoje       | Total de registros com `data == hoje`                |
| Faltas na Semana  | Registros dentro da semana corrente (seg–dom)        |
| Prof. Ausentes    | Número de professores distintos ausentes hoje        |
| Aulas Afetadas    | Aulas da grade cujo professor está ausente hoje      |

**2. Banner de status**

- Verde + "✅ Está tudo certo" — nenhuma falta hoje
- Vermelho + "⚠️ X falta(s)..." — com contagem de ausentes e aulas afetadas

**3. Formulário de registro**

- Data (DD/MM/AAAA, padrão: hoje)
- Professor (Combobox com professores cadastrados)
- Motivo (opcional)
- Impede registro duplicado para o mesmo professor/data

**4. Relatório de Validação**

Treeview com a grade completa filtrada por data:

| Tag TTK     | Visual                         | Condição                        |
|-------------|--------------------------------|---------------------------------|
| `absent`    | fundo `#FEE2E2`, texto vermelho | Professor marcado como ausente  |
| `present`   | fundo `#DCFCE7`, texto verde    | Professor presente              |
| `unknown`   | fundo padrão, texto cinza       | Sem filtro de data aplicado     |

**5. Lista de faltas registradas**

Treeview com todas as faltas em vermelho, ordenadas por data decrescente. Permite remover registro selecionado.

**6. Exportação**

| Botão                           | Arquivo gerado              | Conteúdo                                                        |
|---------------------------------|-----------------------------|-----------------------------------------------------------------|
| Relatório de Faltas (CSV)       | `relatorio_faltas_YYYYMMDD` | Data, Professor, Motivo, Turmas/Disciplinas/Salas afetadas, coluna "Substituto" vazia |
| Grade Validada com Status (CSV) | `grade_validada_YYYYMMDD`   | Grade completa com coluna Status: `Presente` ou `FALTA - SEM COBERTURA` |

Ambos os arquivos usam separador `;` e encoding `utf-8-sig`.

---

### `src/rounded_frame.py` — `RoundedFrame`

Componente `tk.Canvas` que renderiza um retângulo com cantos arredondados via polígono suavizado (`smooth=True`).

Parâmetros do construtor:

| Parâmetro       | Padrão    | Descrição                     |
|-----------------|-----------|-------------------------------|
| `bg_color`      | `#111827` | Cor de preenchimento interna  |
| `border_color`  | `#1F2937` | Cor da borda                  |
| `corner_radius` | `16`      | Raio dos cantos em pixels     |
| `padding`       | `12`      | Espaço interno                |

Método `set_border_color(color)` permite atualizar a cor da borda dinamicamente (usado anteriormente para animações).

> **Nota:** o componente ainda está disponível no código porém não é mais utilizado nas páginas após a migração para o tema claro. Os cards agora são `tk.Frame` com `highlightbackground`.

---

## Estrutura dos arquivos CSV

Todos os arquivos internos usam `,` como separador e encoding `utf-8-sig`.

### `professores.csv`
```
nome,disciplina,disponibilidade
Prof. Silva,Matematica,Seg-Manha,Ter-Noite
```

### `turmas.csv`
```
nome,carga_horaria,disciplinas,sala
Turma A,20,Matematica,Fisica,101
```

### `salas.csv`
```
numero_sala,laboratorio
101,Nao
Lab A,Sim
```

### `faltas.csv`
```
data,professor,dia_semana,bloco,horario,motivo,registrado_em
11/06/2024,Prof. Silva,Seg,Manha,1,Doenca,11/06/2024 08:30
```

---

## Fluxo de uso típico

1. Execute `python main.py`
2. Acesse **Salas** na sidebar → cadastre as salas disponíveis
3. Acesse **Professores** → cadastre professores com disciplinas e disponibilidade
4. Acesse **Turmas** → cadastre turmas, associando disciplinas e sala preferencial
5. Acesse **Dashboard** → clique em **Gerar Grade** e verifique alertas
6. Exporte a grade com **Exportar CSV** (arquivo pronto para Excel)
7. Acesse **Faltas** → registre ausências diárias dos professores
8. Use **Visualizar** no relatório para ver a grade com faltas destacadas em vermelho
9. Exporte o relatório de faltas para envio à Secretaria

---

## Comportamento do algoritmo de grade

- 5 dias × 4 horários × blocos (Manhã/Noite) = estrutura base
- Cada turma recebe até 5 disciplinas × 4 aulas = 20 slots por semana
- O bloco da turma é inferido pelo nome (ex: turmas com `Noite` no nome → bloco Noite)
- Professores são priorizados pelo menor número de aulas já atribuídas
- Conflitos de horário são detectados e registrados como alertas
- A `carga_horaria` da turma está registrada para uso futuro; o algoritmo atual usa sempre 20 slots

---

## Compatibilidade dos arquivos exportados

| Configuração      | Valor        | Motivo                                              |
|-------------------|--------------|-----------------------------------------------------|
| Encoding          | `utf-8-sig`  | BOM sinaliza UTF-8 para o Excel abrir sem configuração |
| Separador         | `;`          | Padrão do Excel em locale português (PT-BR/PT-PT)   |
| Quebra de linha   | `\r\n`       | Padrão CSV/Windows, sem linhas em branco extras     |

---

## Extensões sugeridas

- Adicionar campo `bloco` diretamente em `turmas.csv` para eliminar inferência pelo nome
- Respeitar `carga_horaria` real no algoritmo do `Scheduler`
- Implementar filtro/pesquisa nas Treeviews
- Adicionar campo de substituto diretamente no módulo de faltas
- Histórico de grades geradas com data/hora
- Testes automatizados para `Scheduler` e `DataHandler`

---

## Execução

```bash
python main.py
```

Verificação de sintaxe sem abrir a janela:

```bash
python -m py_compile src/app.py
```
