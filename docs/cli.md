# Interface CLI do OCR PDF

A CLI do OCR PDF é construída sobre a biblioteca `typer` com renderizações visuais robustas fornecidas pelo `rich`.

## Comandos Principais

### 1. `ocr-pdf --version`
Exibe a versão instalada da ferramenta.

```bash
ocr-pdf --version
```

---

### 2. `ocr-pdf info`
Mostra detalhes de diagnóstico do ambiente operacional, compatibilidade e disponibilidade dos mecanismos de OCR locais, além de exibir o mascote do projeto.

Opções:
* `--mascot` / `-m`: Define qual mascote exibir. Opções: `cat` (gato padrão), `cat_alt` (gato alternativo) ou `none` (oculta mascote).

```bash
ocr-pdf info --mascot cat_alt
```

---

### 3. `ocr-pdf engines`
Exibe de forma tabular os motores de OCR suportados pela ferramenta, identificando qual está configurado como padrão e se está atualmente instalado no sistema.

```bash
ocr-pdf engines
```

---

### 4. `ocr-pdf convert`
Realiza a conversão de um PDF de imagens em documento pesquisável ou arquivo de texto extraído.

**Argumentos:**
* `INPUT_FILE` (Obrigatório): O caminho para o PDF original escaneado.

**Opções:**
* `--output` / `-o`: Diretório onde o arquivo gerado será salvo (Padrão: `output/`).
* `--format` / `-f`: Formato de saída. Opções: `pdf` (PDF pesquisável), `txt` (texto plano) ou `markdown` (Markdown estruturado). (Padrão: `pdf`).
* `--engine` / `-e`: Engine OCR a ser utilizada. Opções: `tesseract`, `easyocr`, `paddleocr`. (Padrão: `tesseract`).
* `--lang` / `-l`: Código de idioma suportado pela engine. (Padrão: `por` - Português).
* `--dpi` / `-d`: Resolução para renderizar as páginas do PDF. (Padrão: `300`).
* `--preprocess` / `--no-preprocess`: Habilita ou desabilita conversão prévia da imagem para tons de cinza. (Padrão: Habilitado).
* `--binarize` / `--no-binarize`: Habilita ou desabilita binarização (preto e branco puro) antes do OCR. (Padrão: Desabilitado).
* `--verbose` / `-v`: Ativa logs detalhados de DEBUG.

#### Exemplos de Uso:

**Gerar PDF Pesquisável (Padrão):**
```bash
ocr-pdf convert document.pdf
```

**Extrair texto em formato TXT no idioma Inglês:**
```bash
ocr-pdf convert scans.pdf -f txt -l eng
```

**Extrair Markdown com binarização de imagem a 150 DPI:**
```bash
ocr-pdf convert scan.pdf -f markdown --binarize -d 150
```
