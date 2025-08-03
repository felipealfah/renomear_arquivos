# Projeto de Automação de Leitura e Renomeação de Arquivos

## Objetivo
Criar uma aplicação Python para ler arquivos recuperados do Windows com nomes genéricos e renomeá-los baseado no conteúdo identificado.

## Tipos de Arquivos Suportados
- **Documentos**: .doc, .docx, .pdf
- **Planilhas**: .xls, .xlsx, .csv
- **Apresentações**: .ppt, .pptx

## Bibliotecas Python Utilizadas
- `python-docx` - Para leitura de arquivos Word (.docx)
- `openpyxl` - Para leitura de arquivos Excel (.xlsx)
- `python-pptx` - Para leitura de apresentações PowerPoint (.pptx)
- `PyPDF2` e `pdfplumber` - Para leitura de documentos PDF
- `streamlit` - Para interface de usuário interativa
- `pandas` - Para manipulação de arquivos CSV
- `xlrd` - Para leitura de arquivos Excel legados (.xls)
- `python-docx2txt` ou similar - Para arquivos .doc (se necessário)

## Funcionalidades Principais
1. **Seleção de Diretório**: Interface para escolher pasta de arquivos a serem analisados
2. **Escaneamento de Diretório**: Identificar arquivos com nomes genéricos
3. **Leitura de Conteúdo**: Extrair texto/títulos dos arquivos para identificação
4. **Geração de Nomes**: Criar nomes significativos baseados no conteúdo
5. **Interface de Usuário**: Streamlit para interação e configuração
6. **Renomeação Segura**: Evitar conflitos de nomes e permitir preview das mudanças

## Gerenciamento de Dependências com UV
Este projeto utiliza `uv` para gerenciamento rápido e eficiente de dependências Python.

## Comandos de Desenvolvimento
```bash
# Inicializar projeto com uv
uv init

# Adicionar dependências
uv add streamlit python-docx openpyxl python-pptx pandas xlrd

# Instalar dependências
uv sync

# Executar aplicação
uv run streamlit run app.py

# Executar testes (quando implementados)
uv run pytest tests/

# Verificar código
uv run flake8 src/
uv run black src/

# Ativar ambiente virtual
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows
```

## Estrutura do Projeto
```
/
├── app.py                 # Aplicação principal Streamlit
├── ui/                    # Interface de usuário (Streamlit)
│   ├── __init__.py
│   ├── folder_selector.py # Componente para seleção de pastas
│   ├── file_preview.py    # Preview de arquivos e renomeação
│   └── progress_tracker.py # Barra de progresso e logs
├── functions/             # Funções de negócio
│   ├── __init__.py
│   ├── file_reader.py     # Classes para leitura de diferentes tipos de arquivo
│   ├── renamer.py         # Lógica de renomeação
│   ├── file_scanner.py    # Escaneamento de diretórios
│   └── utils.py           # Funções utilitárias
├── tests/                 # Testes automatizados
│   └── __init__.py
├── requirements.txt       # Dependências do projeto
├── pyproject.toml         # Configurações do projeto (se usando uv)
├── uv.lock               # Lock file das dependências (se usando uv)
├── .venv/                # Ambiente virtual
└── CLAUDE.md             # Este arquivo de regras
```

## Pipeline do Usuário - Fluxo da Aplicação

### 1. Seleção de Diretório
- Interface para escolher pasta com arquivos a serem analisados
- Validação se o diretório existe e tem permissões de leitura
- Botão "Navegar" ou campo de entrada manual do caminho

### 2. Análise Automática do Diretório
- Sistema escaneia todos os arquivos do diretório
- Identifica tipos de arquivo por extensão (.docx, .xlsx, .pptx, .pdf, etc.)
- Conta quantidade de arquivos por tipo
- Ignora arquivos não suportados

### 3. Exibição dos Tipos Encontrados
- Tabela/cards mostrando:
  - Tipo de arquivo (Word, Excel, PowerPoint, PDF)
  - Quantidade encontrada
  - Extensões detectadas (.docx, .doc, .xlsx, etc.)
- Status visual: tipos disponíveis vs não encontrados

### 4. Seleção de Tipos para Processamento
- Checkboxes/toggles para cada tipo de documento:
  - ☐ Documentos Word (.doc, .docx)
  - ☐ Planilhas Excel (.xls, .xlsx)
  - ☐ Apresentações PowerPoint (.ppt, .pptx)
  - ☐ Documentos PDF (.pdf)
  - ☐ Arquivos CSV (.csv)
- Botão "Processar Selecionados"

### 5. Processamento e Renomeação
- Barra de progresso por tipo de arquivo
- Para cada arquivo selecionado:
  - Lê conteúdo do documento
  - Extrai título/texto principal
  - Gera nome sugerido
  - Renomeia arquivo
- Log em tempo real das operações
- Relatório final com sucessos/erros

## Interface Streamlit - Componentes
- **Seletor de Pasta**: Campo de entrada + botão navegar
- **Análise de Diretório**: Exibição automática dos tipos encontrados
- **Seletores de Tipo**: Checkboxes para escolher tipos a processar
- **Preview de Operações**: Lista de arquivos que serão processados
- **Barra de Progresso**: Progresso por tipo e geral
- **Log de Operações**: Histórico em tempo real das operações

## Regras de Desenvolvimento
- Sempre verificar se o arquivo existe antes de tentar renomear
- Criar backup dos nomes originais antes de renomear
- Implementar preview das mudanças antes de aplicar
- Validar nomes de arquivo (caracteres especiais, tamanho)
- Tratar exceções de leitura de arquivos corrompidos
- Interface intuitiva e responsiva no Streamlit
- Usar `uv` para todas as operações de dependências
- Validar caminhos de pasta selecionados pelo usuário