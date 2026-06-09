# OCR PDF CLI

> Converta PDFs escaneados em documentos pesquisáveis utilizando OCR local, offline e multiplataforma.

OCR PDF CLI é uma ferramenta de linha de comando desenvolvida em Python para transformar PDFs compostos por imagens em documentos pesquisáveis através de OCR (Reconhecimento Óptico de Caracteres).

O projeto foi desenvolvido com foco em:

* Linux
* Windows
* macOS
* Termux (Android)

Todo o processamento ocorre localmente na máquina do usuário.

Nenhum dado é enviado para serviços externos.

---

## Principais Recursos

* Conversão de PDF escaneado para PDF pesquisável
* Extração de texto para TXT
* Exportação para Markdown
* OCR local e offline
* Suporte a múltiplas engines OCR
* Processamento em lote
* Compatível com Termux
* Interface CLI amigável
* Banner inspirado na identidade visual PDA

---

## Engines OCR

| Engine    | Status |
| --------- | ------ |
| Tesseract | ✅      |
| EasyOCR   | ✅      |
| PaddleOCR | ✅      |

A engine padrão é o Tesseract.

---

## Instalação

### Clonar o repositório

```bash
git clone https://github.com/mfaria-tech/ocr-pdf-cli.git

cd ocr-pdf-cli
```

---

### Ambiente virtual

```bash
python -m venv .venv

source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

---

### Instalação básica

```bash
pip install -e .
```

---

### Instalação com EasyOCR

```bash
pip install -e .[easyocr]
```

---

### Instalação com PaddleOCR

```bash
pip install -e .[paddleocr]
```

---

### Instalação completa

```bash
pip install -e .[all]
```

---

## Dependências Externas

### Tesseract OCR

O Tesseract deve estar instalado no sistema.

#### Debian

```bash
sudo apt install tesseract-ocr
```

#### Arch

```bash
sudo pacman -S tesseract
```

#### Fedora

```bash
sudo dnf install tesseract
```

#### Termux

```bash
pkg update

pkg install tesseract
```

#### Windows

Instale através do projeto UB Mannheim:

https://github.com/UB-Mannheim/tesseract/wiki

---

## Verificando a instalação

```bash
ocr-pdf verify
```

Exemplo:

```text
✓ Python
✓ Tesseract
✓ EasyOCR
✗ PaddleOCR
```

---

## Uso

### Informações do sistema

```bash
ocr-pdf info
```

---

### Listar engines disponíveis

```bash
ocr-pdf engines
```

---

### Converter PDF

```bash
ocr-pdf convert documento.pdf
```

---

### Escolher engine

```bash
ocr-pdf convert documento.pdf \
    --engine paddleocr
```

---

### Definir arquivo de saída

```bash
ocr-pdf convert documento.pdf \
    --output resultado.pdf
```

---

### Exportar TXT

```bash
ocr-pdf convert documento.pdf \
    --format txt
```

---

### Exportar Markdown

```bash
ocr-pdf convert documento.pdf \
    --format md
```

---

### Processamento em lote

```bash
ocr-pdf batch scans/
```

---

### Benchmark

```bash
ocr-pdf benchmark documento.pdf
```

Exemplo:

```text
┌────────────┬────────┬─────────────┐
│ Engine     │ Tempo  │ Confiança   │
├────────────┼────────┼─────────────┤
│ Tesseract  │ 2.1 s  │ 89.3 %      │
│ EasyOCR    │ 1.7 s  │ 92.8 %      │
│ PaddleOCR  │ 1.2 s  │ 95.4 %      │
└────────────┴────────┴─────────────┘
```

---

## Estrutura do Projeto

```text
ocr-pdf-cli/
+-- docs/
+-- tests/
+-- input/
+-- output/
+-- src/
    +-- ocr_pdf_cli/
        +-- cli/
        +-- config/
        +-- core/
        +-- engines/
        +-- exporters/
        +-- models/
        +-- utils/
```

---

## Roadmap

### v0.1

* Estrutura do projeto
* CLI inicial
* Tesseract

### v0.2

* EasyOCR
* PaddleOCR

### v0.3

* Processamento em lote
* Benchmark

### v1.0

* PDF pesquisável
* Pré-processamento avançado
* Cobertura de testes ampliada
* Estabilidade multiplataforma

---

## Desenvolvimento

Instalar dependências de desenvolvimento:

```bash
pip install -e .[dev]
```

Executar testes:

```bash
pytest
```

Lint:

```bash
ruff check .
```

Type checking:

```bash
mypy src
```

---

## Licença

Distribuído sob a licença MIT.

Veja o arquivo LICENSE para mais informações.

---

## Autor

Marcus Faria

Projeto desenvolvido como parte do ecossistema de ferramentas open source voltadas para produtividade, acessibilidade e processamento local de documentos.
