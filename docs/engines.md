# Motores OCR (Engines)

O **ocr-pdf-cli** foi projetado para funcionar de modo 100% offline, sem depender de conexões externas ou APIs de terceiros. Para isso, ele utiliza motores locais de OCR.

## Engines Suportadas

### 1. Tesseract OCR (Padrão)
O Tesseract é o motor padrão do projeto. É altamente robusto, suporta centenas de idiomas e possui excelente performance em CPUs convencionais.

Para utilizar este motor, a biblioteca de sistema `tesseract` deve estar instalada e o seu executável adicionado no `PATH` do sistema.

#### Instalação do Tesseract por Plataforma:

* **Windows:**
  Faça o download do instalador atualizado através do repositório oficial ou via gerenciador de pacotes:
  ```powershell
  winget install UB.TesseractOCR
  ```
  Certifique-se de adicionar o caminho de instalação (geralmente `C:\Program Files\Tesseract-OCR`) às Variáveis de Ambiente do seu Sistema (`PATH`).

* **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt update
  sudo apt install tesseract-ocr tesseract-ocr-por
  ```

* **macOS (Homebrew):**
  ```bash
  brew install tesseract tesseract-lang
  ```

* **Termux (Android):**
  ```bash
  pkg install tesseract tesseract-langs
  ```

---

### 2. EasyOCR (Opcional / Futuro)
O EasyOCR é um motor baseado em PyTorch que apresenta excelente taxa de assertividade, principalmente para textos estilizados ou com ruído pesado.

Necessita de GPU com aceleração CUDA para obter performance ideal. O suporte à exportação de coordenadas exatas para gerar PDFs pesquisáveis com EasyOCR está planejado para versões futuras.

Para instalar as dependências opcionais:
```bash
pip install ocr-pdf-cli[easyocr]
```

---

### 3. PaddleOCR (Opcional / Futuro)
O PaddleOCR é outro motor de OCR estado-da-arte, otimizado para cenários empresariais complexos e documentos de tabelas. Ele exige a instalação do ecossistema PaddlePaddle.

Para instalar as dependências opcionais:
```bash
pip install ocr-pdf-cli[paddleocr]
```
