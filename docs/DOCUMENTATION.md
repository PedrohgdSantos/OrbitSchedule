# OrbitSchedule — Documentação Técnica

## Visão Geral

**OrbitSchedule** é uma aplicação desktop em Python (Tkinter) para gestão e geração automática de grades horárias escolares. Inclui módulo completo de controle de faltas com substituição automática de professores, gráficos de análise integrados via Matplotlib, animações de transição e exportação de relatórios em CSV compatível com Excel.

### Funcionalidades

- Cadastro de professores, turmas e salas com persistência em CSV
- Geração automática de grade horária com detecção de conflitos
- Módulo de faltas: registro, relatório visual, substituição automática, exportação
- Gráficos de análise (Faltas por Turma, Faltas por Matéria, Mapa de Presença)
- Animações: fade de página, hover na sidebar, count-up nos metric cards
- Alertas tipados com blocos coloridos por severidade
- Exportação CSV com UTF-8-BOM e separador `;` (compatível com Excel PT-BR)

---

## Estrutura do Projeto

```
OrbitSchedule/
├── main.py                  # Ponto de entrada
├── src/
│   ├── app.py               # Shell: sidebar, roteamento, dashboard
│   ├── models.py            # Dataclasses: Professor, Turma, Sala, Aula, Falta
│   ├── data_handler.py      # I/O de todos os arquivos CSV
│   ├── scheduler.py         # Algoritmo de geração da grade
│   ├── animations.py        # Utilitários de animação (fade, count-up, lerp)
│   ├── charts.py            # Widgets de gráficos (Matplotlib + Canvas)
│   ├── substitution.py      # Algoritmo de busca de professores substitutos
│   ├── professor_manager.py # Página CRUD de professores
│   ├── turma_manager.py     # Página CRUD de turmas
│   ├── sala_manager.py      # Página CRUD de salas
│   ├── absence_manager.py   # Página de gestão de faltas
│   └── rounded_frame.py     # Componente legado (não usado nas páginas atuais)
├── data/
│   ├── professores.csv
│   ├── turmas.csv
│   ├── salas.csv
│   └── faltas.csv           # Criado automaticamente no primeiro registro
└── docs/
    └── DOCUMENTATION.md
```

---

## Design System

Interface no padrão **Designo LMS Dashboard** — tema claro, sidebar branca, acento laranja.

### Paleta de cores

| Token        | Hex       | Uso                                         |
|--------------|-----------|---------------------------------------------|
| `BG_PAGE`    | `#F5F6FA` | Fundo geral das páginas                     |
| `BG_SIDEBAR` | `#FFFFFF` | Fundo da sidebar                            |
| `BG_CARD`    | `#FFFFFF` | Fundo dos cards e tabelas                   |
| `ORANGE`     | `#F97316` | Cor primária: botões, nav ativo, logo       |
| `ORANGE_DIM` | `#FFF7ED` | Hover de nav e ícones de métricas           |
| `TEXT_DARK`  | `#111827` | Texto principal                             |
| `TEXT_MID`   | `#6B7280` | Labels secundários e subtítulos             |
| `TEXT_LIGHT` | `#9CA3AF` | Textos de placeholder                       |
| `BORDER`     | `#E5E7EB` | Bordas de cards e separadores               |
| `GREEN`      | `#16A34A` | Status "presente" / sucesso                 |
| `GREEN_BG`   | `#DCFCE7` | Fundo de banner/linha "OK"                  |
| `RED`        | `#DC2626` | Faltas / erros / botão deletar              |
| `RED_BG`     | `#FEE2E2` | Fundo de linha/banner com falta             |
| `AMBER`      | `#D97706` | Avisos parciais / substituto atribuído      |
| `AMBER_BG`   | `#FEF3C7` | Fundo de linha coberta por substituto       |
| `BLUE`       | `#2563EB` | Ícone de Professores / bloco info           |
| `BLUE_BG`    | `#DBEAFE` | Fundo de bloco informativo                  |

### Layout

A janela é dividida em duas colunas:

- **Sidebar** (220 px, fixa): logo + itens de navegação animados
- **Área de conteúdo** (expansível): página ativa + barra de status no rodapé

Cards são `tk.Frame` com `highlightbackground=BORDER, highlightthickness=1`.

---

## Módulos

### `src/animations.py`

Utilitários de animação baseados em `root.after()`. Sem dependências externas.

#### `lerp_color(src, dst, t) → str`

Interpolação linear entre duas cores hexadecimais. `t=0` retorna `src`, `t=1` retorna `dst`. Usada internamente pelo hover da sidebar.

#### `fade_page(root, callback, steps=10, delay_ms=14)`

Anima a opacidade da janela de `1.0 → 0.55 → 1.0`. A `callback` (troca de página) é executada no ponto mais escuro. Duração total ≈ 280 ms.

```
root.attributes("-alpha", ...)  ← API usada
```

Chamada em `SchedulerApp._navigate()` a cada troca de página.

#### `count_up(label, target, root, duration_ms=650)`

Anima o texto de um `tk.Label` do valor numérico atual até `target`. Calcula número de passos proporcional à diferença para que grandes saltos não sejam lentos. Usada nos metric cards do dashboard quando a grade é gerada ou limpa.

#### `bind_hover(root, widgets, normal_bg, hover_bg, steps, delay_ms, guard_fn)`

Vincula `<Enter>`/`<Leave>` a uma animação de interpolação de cor em todos os widgets da lista. O parâmetro `guard_fn` permite suprimir a animação quando o widget está em estado "ativo" (ex: item selecionado na sidebar).

---

### `src/charts.py`

Widgets de visualização embutidos em `tk.Frame`.

#### `FaltaBarChart(parent)`

Dois gráficos de barras lado a lado via **Matplotlib** (`FigureCanvasTkAgg`):

- **Esquerda** — Faltas por Turma: conta aulas da grade cujo professor está ausente, agrupadas por turma. Barras em vermelho.
- **Direita** — Faltas por Matéria: mesma lógica, agrupada por disciplina. Barras em laranja.

Exibe placeholder "Sem dados" quando não há faltas ou grade. Se `matplotlib` não estiver instalado, mostra label com instrução de instalação.

**API:** `chart.refresh(faltas: List[Falta], grade: List[Aula])` — pode ser chamado a qualquer momento para atualizar os dados.

#### `GradeHeatmap(parent)`

Grid de horários desenhado com `tk.Canvas` puro (sem dependência externa).

- Colunas = dias da semana (Seg–Sex)
- Linhas = horários (1°–6°)
- Célula vermelha (`#FEE2E2`) — professor ausente naquele slot
- Célula verde (`#F0FDF4`) — slot ocupado, professor presente
- Célula cinza (`#F9FAFB`) — nenhuma aula agendada

Redesenhado via `_redraw()` a cada `<Configure>` (redimensionamento) e a cada chamada de `refresh()`.

**API:** `heatmap.refresh(faltas, grade)` — reconstrói o grid interno e redesenha.

Ambos os widgets estão presentes no Dashboard (seções "Análise de Faltas" e "Mapa de Presença") e o `FaltaBarChart` também aparece na página de Faltas.

---

### `src/substitution.py`

Algoritmo de busca de professores substitutos. Sem UI — retorna dados estruturados.

#### `SubstituteOption` (dataclass)

| Campo           | Tipo            | Descrição                                        |
|-----------------|-----------------|--------------------------------------------------|
| `professor`     | `Professor`     | Candidato encontrado                             |
| `covers`        | `List[Aula]`    | Aulas que este professor consegue cobrir         |
| `covers_all`    | `bool`          | `True` se cobre todas as aulas do ausente        |
| `partial_count` | `int`           | Número de aulas que consegue cobrir              |
| `score`         | `float`         | Pontuação para ranking                           |

#### `affected_classes(falta, grade) → List[Aula]`

Retorna todas as aulas da grade que pertencem ao professor ausente no dia da falta. Converte a abreviação (`falta.dia_semana = "Seg"`) para o nome completo (`"Segunda"`) para comparar com `aula.dia`.

#### `find_substitutes(falta, grade, professores) → List[SubstituteOption]`

Busca candidatos usando as mesmas regras do `Scheduler`:

1. O candidato deve lecionar a mesma disciplina da aula afetada
2. Deve ter disponibilidade no formato `"Dia-Bloco"` correspondente (ex: `"Segunda-Manhã"`)
3. Não pode já estar ocupado naquele `(dia, horario)` na grade

**Ranking:** candidatos que cobrem todas as aulas (`covers_all=True`) vêm primeiro. Entre empatados, menor carga de aulas atribuídas tem prioridade (score mais alto).

Retorna lista vazia se nenhum professor puder cobrir ao menos uma aula.

---

### `src/app.py` — `SchedulerApp`

Shell da aplicação. Gerencia layout, navegação, dashboard e orquestração entre módulos.

#### Construção

```
__init__
  └─ _configure_ttk_styles()   → estilos TTK globais
  └─ _build_shell()            → sidebar + área de conteúdo + barra de status
  └─ _build_sidebar()          → logo + nav items com hover animado
  └─ _build_pages()            → instancia managers e registra páginas
  └─ update_dashboard_summary()
  └─ _navigate("dashboard")
```

#### Navegação com fade

```python
def _navigate(self, page_key):
    def _switch():   # pack/pack_forget + atualiza cores da sidebar
        ...
    fade_page(self.root, _switch)   # ← animação via animations.py
```

#### Hover animado na sidebar

`_nav_hover(key, row, icon, text, entering)` usa `lerp_color` em 6 passos de 14 ms para interpolar `BG_SIDEBAR → ORANGE_DIM` (hover) ou o caminho inverso. Cancela a animação anterior do mesmo item antes de iniciar uma nova.

Itens ativos (fundo `ORANGE`) ignoram hover completamente.

#### Dashboard

| Seção                    | Descrição                                                               |
|--------------------------|-------------------------------------------------------------------------|
| Metric cards (×4)        | Professores, Turmas, Salas, Aulas — animados com `count_up()`           |
| Botões de ação           | Gerar Grade, Exportar CSV, Limpar Grade — com hover `<Enter>`/`<Leave>` |
| Alertas e Status         | Blocos individuais por severidade, borda dinâmica, badge de status       |
| Análise de Faltas        | `FaltaBarChart` atualizado via `refresh_charts()`                       |
| Mapa de Presença         | `GradeHeatmap` atualizado via `refresh_charts()`                        |
| Grade Horária Gerada     | Treeview com linhas alternadas                                          |

#### Alertas por bloco

`update_alert_text(message, append)` divide a mensagem em linhas e classifica cada uma:

| Prefixo / conteúdo     | Tipo      | Visual                            |
|------------------------|-----------|-----------------------------------|
| `✅` / "sucesso"       | `success` | Barra verde + fundo `GREEN_BG`    |
| `❌` / "erro"          | `error`   | Barra vermelha + fundo `RED_BG`   |
| `⚠️` / `•` / "falta"  | `warning` | Barra âmbar + fundo `AMBER_BG`    |
| Outros                 | `info`    | Barra azul + fundo `BLUE_BG`      |

Quando há qualquer erro ou aviso, a borda do card de alertas fica **vermelha (2 px)** e o badge mostra `● Há problemas`. Sem problemas, borda verde e badge `● OK`.

#### `refresh_charts()`

Método central que propaga os dados atuais (`absence_manager.faltas` + `grade_gerada`) para `_chart_faltas`, `_chart_heatmap` e `absence_manager.refresh_charts()`. Chamado após:
- `gerar_grade()` — quando a grade muda
- `clear_grade()` — quando a grade é limpa
- `AbsenceManager._registrar_falta()` / `_delete_falta()` — quando faltas mudam

#### Métodos públicos relevantes

| Método                       | Descrição                                               |
|------------------------------|---------------------------------------------------------|
| `gerar_grade()`              | Executa `Scheduler`, popula Treeview, atualiza charts   |
| `exportar_grade()`           | Abre diálogo, chama `DataHandler.save_grade()`          |
| `clear_grade()`              | Limpa grade da memória e da Treeview                    |
| `update_dashboard_summary()` | Atualiza metric cards com `count_up()`                  |
| `set_status(msg)`            | Atualiza barra de status inferior                       |
| `update_alert_text(msg)`     | Renderiza bloco de alerta tipado                        |
| `refresh_charts()`           | Sincroniza todos os widgets de gráfico                  |

---

### `src/models.py` — Modelos de dados

Todos os modelos são `@dataclass`.

#### `Professor`
| Campo              | Tipo        | Descrição                                               |
|--------------------|-------------|---------------------------------------------------------|
| `nome`             | `str`       | Nome completo                                           |
| `disciplinas`      | `List[str]` | Disciplinas que pode lecionar                           |
| `disponibilidade`  | `List[str]` | Blocos disponíveis no formato `"Dia-Bloco"` (ex: `"Segunda-Manhã"`) |
| `aulas_atribuidas` | `int`       | Contador de aulas na grade; usado para priorização      |

#### `Turma`
| Campo              | Tipo        | Descrição                          |
|--------------------|-------------|------------------------------------|
| `nome`             | `str`       | Identificador da turma             |
| `carga_horaria`    | `int`       | Total de aulas semanais            |
| `disciplinas`      | `List[str]` | Disciplinas que a turma cursa      |
| `sala_preferencial`| `str`       | Sala onde a turma será alocada     |

#### `Sala`
| Campo            | Tipo   | Descrição                    |
|------------------|--------|------------------------------|
| `numero`         | `str`  | Identificador único da sala  |
| `is_laboratorio` | `bool` | `True` se for laboratório    |

#### `Aula`
| Campo       | Tipo  | Descrição                          |
|-------------|-------|------------------------------------|
| `dia`       | `str` | Dia completo (ex: `"Segunda"`)     |
| `horario`   | `int` | Número do horário no dia (1–4)     |
| `bloco`     | `str` | `"Manhã"` ou `"Noite"`            |
| `turma`     | `str` | Nome da turma                      |
| `disciplina`| `str` | Nome da disciplina                 |
| `professor` | `str` | Nome do professor                  |
| `sala`      | `str` | Número da sala                     |

#### `Falta`
| Campo          | Tipo  | Descrição                                          |
|----------------|-------|----------------------------------------------------|
| `data`         | `str` | Data no formato `DD/MM/AAAA`                       |
| `professor`    | `str` | Nome do professor ausente                          |
| `dia_semana`   | `str` | Abreviação (ex: `"Seg"`)                           |
| `bloco`        | `str` | Bloco inferido da grade (`"Manhã"`, `"Noite"`, `"—"`) |
| `horario`      | `str` | Horário inferido da grade ou `"—"`                 |
| `motivo`       | `str` | Motivo informado ou `"Não informado"`              |
| `registrado_em`| `str` | Timestamp do registro (`DD/MM/AAAA HH:MM`)         |
| `substituto`   | `str` | Nome do professor substituto atribuído; `""` = sem cobertura |

O campo `substituto` tem default `""` e é opcional — faltas antigas sem o campo são carregadas normalmente pelo `DataHandler`.

---

### `src/data_handler.py` — `DataHandler`

Todos os métodos são estáticos. Responsável por toda I/O de CSV.

**Encoding:** `utf-8-sig` (UTF-8 com BOM) em leitura e escrita, garantindo compatibilidade com Excel em qualquer sistema operacional.

**Separador:** arquivos internos usam `,`; exportações ao usuário usam `;` (padrão Excel PT-BR).

| Método                           | Arquivo alvo      | Descrição                                  |
|----------------------------------|-------------------|--------------------------------------------|
| `_read_csv(path)`                | qualquer          | Lê CSV, retorna `List[dict]`               |
| `_write_csv(path, data, fields)` | qualquer          | Grava CSV interno (separador `,`)          |
| `load_professores(path)`         | `professores.csv` | Retorna `List[Professor]`                  |
| `save_professores(path, lista)`  | `professores.csv` | Persiste lista de professores              |
| `load_turmas(path)`              | `turmas.csv`      | Retorna `List[Turma]`                      |
| `save_turmas(path, lista)`       | `turmas.csv`      | Persiste lista de turmas                   |
| `load_salas(path)`               | `salas.csv`       | Retorna `List[Sala]`                       |
| `save_salas(path, lista)`        | `salas.csv`       | Persiste lista de salas                    |
| `load_faltas(path)`              | `faltas.csv`      | Retorna `List[Falta]` com campo `substituto` |
| `save_faltas(path, lista)`       | `faltas.csv`      | Persiste lista de faltas com `substituto`  |
| `save_grade(path, grade)`        | arquivo escolhido | Exporta grade com separador `;`, UTF-8-BOM |

---

### `src/scheduler.py` — `Scheduler`

Algoritmo de geração da grade horária.

**Constantes:**
- `DIAS`: `["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]`
- `HORARIOS`: `[1, 2, 3, 4]`
- `BLOCOS`: `["Manhã", "Noite"]`

**Lógica de `gerar_grade()`:**

1. Para cada turma, determina o bloco (`Manhã`/`Noite`) pelo nome
2. Para cada disciplina da turma, tenta alocar 4 aulas distribuídas nos 5 dias
3. Busca professor via `_get_professores_disponiveis(disciplina, dia, bloco, horario)`
4. Prioriza professor com menor `aulas_atribuidas`
5. Registra alerta se nenhum professor puder ser alocado no slot

**Regras de alocação (idênticas às do módulo de substituição):**
- Professor deve lecionar a disciplina solicitada
- Professor deve ter `"Dia-Bloco"` em `disponibilidade` (ex: `"Segunda-Manhã"`)
- Professor não pode estar em outro slot com mesmo `(dia, horario)` na grade atual

---

### `src/absence_manager.py` — `AbsenceManager`

Módulo completo de gestão de faltas. Herda `tk.Frame`.

#### Seções da página

**1. Dashboard de métricas (4 cards)**

| Card              | Cálculo                                              |
|-------------------|------------------------------------------------------|
| Faltas Hoje       | Total de registros com `data == hoje`                |
| Faltas na Semana  | Registros dentro da semana corrente (seg–dom)        |
| Prof. Ausentes    | Professores distintos ausentes hoje                  |
| Aulas Afetadas    | Aulas da grade cujo professor está ausente hoje      |

**2. Gráficos de análise**

`FaltaBarChart` embutido — Faltas por Turma e por Matéria. Atualizado a cada registro ou remoção de falta.

**3. Banner de status**

| Situação              | Cor    | Mensagem                                         |
|-----------------------|--------|--------------------------------------------------|
| Nenhuma falta hoje    | Verde  | ✅ Está tudo certo                               |
| Faltas sem cobertura  | Vermelho | ⚠️ X falta(s) — Y sem cobertura               |
| Todas com substituto  | Âmbar  | 🔄 X aula(s) com substituto atribuído           |

**4. Formulário de registro**

- Data (DD/MM/AAAA, padrão: hoje), Professor (Combobox), Motivo (opcional)
- Impede duplicata para o mesmo professor/data
- Ao confirmar, abre automaticamente o **dialog de substituição**

**5. Dialog de substituição automática**

Modal que abre logo após o registro da falta (e pode ser reaberto via botão "👤 Atribuir Substituto"):

1. Lista as aulas afetadas pelo professor ausente naquele dia
2. Executa `find_substitutes()` e exibe os candidatos rankeados:
   - `★` = cobre todas as aulas
   - `◎` = cobertura parcial, mostra contagem
3. Combobox pré-selecionado com o melhor candidato
4. **Confirmar** → salva o nome em `falta.substituto` e persiste
5. **Registrar sem substituto** → mantém `falta.substituto = ""`

Se nenhum candidato for encontrado, exibe mensagem explicando os critérios necessários (disciplina, disponibilidade, sem conflito).

**6. Relatório de Validação da Grade**

Treeview da grade completa filtrada por data:

| Tag TTK   | Visual                           | Condição                               |
|-----------|----------------------------------|----------------------------------------|
| `present` | fundo verde, texto verde         | Professor presente                     |
| `absent`  | fundo vermelho, texto vermelho   | Ausente sem substituto atribuído       |
| `covered` | fundo âmbar, texto âmbar         | Ausente mas com substituto — `🔄 Nome` |
| `unknown` | fundo padrão, texto cinza        | Sem filtro de data aplicado            |

**7. Lista de faltas registradas**

| Tag TTK   | Visual        | Condição                          |
|-----------|---------------|-----------------------------------|
| `falta`   | fundo vermelho | Sem substituto                   |
| `coberta` | fundo âmbar   | Com substituto atribuído — `✅ Nome` |

Botões: "Remover Falta Selecionada" + "👤 Atribuir Substituto" (reabre dialog para a falta selecionada).

**8. Exportação**

| Botão                           | Conteúdo da coluna "Substituto"                    |
|---------------------------------|----------------------------------------------------|
| Relatório de Faltas (CSV)       | Nome do substituto ou `"A preencher"` se vazio     |
| Grade Validada com Status (CSV) | Status: `Presente`, `COBERTO — Nome` ou `FALTA - SEM COBERTURA` + coluna "Substituto" separada |

Ambos usam separador `;` e encoding `utf-8-sig`.

---

### `src/professor_manager.py`, `turma_manager.py`, `sala_manager.py`

Páginas de CRUD padrão. Herdam `tk.Frame`. Mesma estrutura:
- Formulário superior (card branco)
- Treeview inferior com scroll

**Regra de sala compartilhada** (`TurmaManager`): máximo de 2 turmas por sala; se já houver 1, a nova deve ter as mesmas disciplinas. `update_sala_options()` é chamado pelo `SalaManager` ao salvar para manter o Combobox de salas sincronizado.

---

## Estrutura dos arquivos CSV

Arquivos internos: separador `,`, encoding `utf-8-sig`.

### `professores.csv`
```
nome,disciplina,disponibilidade
João Silva,Matemática,Segunda-Manhã,Terça-Noite
```

### `turmas.csv`
```
nome,carga_horaria,disciplinas,sala
Turma A,20,Matemática;Física,101
```

### `salas.csv`
```
numero_sala,laboratorio
101,Nao
Lab A,Sim
```

### `faltas.csv`
```
data,professor,dia_semana,bloco,horario,motivo,registrado_em,substituto
11/06/2026,João Silva,Seg,Manhã,1,Doença,11/06/2026 08:30,Maria Souza
```

---

## Fluxo de uso típico

1. Execute `python main.py`
2. **Salas** → cadastre as salas disponíveis
3. **Professores** → cadastre com disciplinas e disponibilidade no formato `"Dia-Bloco"` (ex: `Segunda-Manhã`)
4. **Turmas** → associe disciplinas e sala preferencial
5. **Dashboard** → clique **Gerar Grade** → verifique alertas tipados e o Mapa de Presença
6. Exporte a grade com **Exportar CSV**
7. **Faltas** → registre ausências; o dialog de substituição abre automaticamente
8. Confirme ou troque o substituto sugerido
9. O Relatório de Validação mostra verde (presente), vermelho (sem cobertura) ou âmbar (coberto)
10. Exporte o relatório para envio à Secretaria — coluna Substituto já preenchida

---

## Algoritmo de substituição

```
falta registrada
       │
       ▼
affected_classes(falta, grade)
  → aulas do dia cujo professor == ausente
       │
       ▼
find_substitutes(falta, grade, professores)
  para cada professor (≠ ausente):
    para cada aula afetada:
      ✓ mesma disciplina?
      ✓ "Dia-Bloco" em disponibilidade?
      ✓ sem conflito (dia, horario) na grade?
    → calcula score e covers_all
  → ordena: covers_all primeiro, depois score desc
       │
       ▼
Dialog exibe candidatos → usuário confirma
       │
       ▼
falta.substituto = nome_escolhido
DataHandler.save_faltas(...)
```

---

## Compatibilidade dos arquivos exportados

| Configuração    | Valor       | Motivo                                                     |
|-----------------|-------------|------------------------------------------------------------|
| Encoding        | `utf-8-sig` | BOM sinaliza UTF-8 para o Excel abrir sem configuração     |
| Separador       | `;`         | Padrão do Excel em locale português (PT-BR/PT-PT)          |
| Quebra de linha | `\r\n`      | Padrão CSV/Windows, sem linhas em branco extras            |

---

## Dependências

| Pacote       | Uso                                           | Obrigatório |
|--------------|-----------------------------------------------|-------------|
| `tkinter`    | Interface gráfica (incluso no Python)         | Sim         |
| `matplotlib` | Gráficos de barras no dashboard e na página de faltas | Recomendado |

Para instalar matplotlib:
```bash
pip install matplotlib
```

Sem matplotlib, os gráficos de barra exibem um placeholder de texto. O Mapa de Presença (`GradeHeatmap`) é Canvas puro e funciona sem dependências externas.

---

## Execução

```bash
python main.py
```

Verificação de sintaxe sem abrir a janela:

```bash
python -m py_compile src/app.py src/absence_manager.py src/charts.py src/animations.py src/substitution.py
```
