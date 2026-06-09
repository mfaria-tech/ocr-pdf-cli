"""Pipeline principal de processamento de OCR em PDFs."""

import logging
from pathlib import Path
from typing import Optional

from ocr_pdf_cli.config.settings import settings
from ocr_pdf_cli.core.pdf_loader import PDFLoader
from ocr_pdf_cli.core.image_preprocessor import ImagePreprocessor
from ocr_pdf_cli.core.text_postprocessor import TextPostprocessor
from ocr_pdf_cli.engines import get_engine
from ocr_pdf_cli.utils.files import temp_dir_context
from ocr_pdf_cli.exporters.pdf import PDFExporter
from ocr_pdf_cli.exporters.txt import TXTExporter
from ocr_pdf_cli.exporters.markdown import MarkdownExporter

logger = logging.getLogger("ocr_pdf_cli")

class OCRPipeline:
    """Pipeline que coordena o fluxo de processamento de PDFs."""

    def __init__(
        self,
        engine_name: str = "tesseract",
        language: str = "por",
        dpi: int = 300,
        preprocess: bool = True,
        binarize: bool = False,
    ) -> None:
        """Inicializa as etapas do pipeline.

        Args:
            engine_name: Nome do mecanismo OCR (ex: 'tesseract').
            language: Código do idioma para OCR (ex: 'por').
            dpi: Resolução de renderização de imagem das páginas.
            preprocess: Habilita conversão para escala de cinza por padrão.
            binarize: Habilita binarização (P&B) da imagem.
        """
        self.engine_name = engine_name.strip().lower()
        self.language = language
        self.dpi = dpi
        self.preprocess = preprocess
        self.binarize = binarize

        self.loader = PDFLoader()
        self.preprocessor = ImagePreprocessor()
        self.postprocessor = TextPostprocessor()
        
        # Obtém a engine selecionada
        self.engine = get_engine(self.engine_name)

    def run(
        self,
        input_path: Path,
        output_dir: Path,
        output_format: str = "pdf"
    ) -> Path:
        """Executa o pipeline completo no PDF de entrada.

        Args:
            input_path: Arquivo PDF de entrada contendo scans/imagens.
            output_dir: Diretório onde o arquivo gerado será salvo.
            output_format: O formato de exportação ('pdf', 'txt' ou 'markdown'/'md').

        Returns:
            O caminho do arquivo exportado com sucesso.
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_path}")
            
        if not self.engine.is_available:
            raise RuntimeError(
                f"A engine OCR '{self.engine_name}' não está operacional ou instalada no sistema. "
                "Por favor, verifique as dependências locais."
            )

        logger.info(f"Iniciando pipeline OCR: [cyan]{input_path.name}[/cyan] -> [magenta]{output_format}[/magenta]")
        
        # 1. Carregar e Renderizar PDF em Imagens
        document, images = self.loader.load_pdf(input_path, dpi=self.dpi)
        logger.info(f"PDF carregado. {len(images)} página(s) renderizada(s) com sucesso a {self.dpi} DPI.")
        
        # Cria o diretório de saída caso não exista
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Usamos um diretório temporário para salvar as imagens pré-processadas das páginas.
        # Estas imagens são necessárias para desenhar a imagem no PDF pesquisável final.
        with temp_dir_context() as temp_dir:
            for idx, img in enumerate(images):
                page = document.pages[idx]
                page_num = page.page_number
                logger.info(f"Processando página {page_num}/{len(images)}...")

                # 2. Pré-processar a imagem
                if self.preprocess or self.binarize:
                    img = self.preprocessor.preprocess(
                        img,
                        grayscale=self.preprocess,
                        binarize=self.binarize
                    )
                
                # Salva a imagem temporariamente
                temp_img_path = temp_dir / f"page_{page_num}.png"
                img.save(temp_img_path)
                page.image_path = str(temp_img_path)

                # 3. Executar o OCR
                logger.debug(f"Executando OCR da página {page_num} usando {self.engine_name}")
                ocr_result = self.engine.extract_page(img, lang=self.language, page_number=page_num)
                
                # 4. Pós-processar o texto extraído
                ocr_result.text = self.postprocessor.postprocess(ocr_result.text)
                page.ocr_result = ocr_result
                
                # Exibe prévia do texto extraído (primeiras linhas)
                sample_lines = ocr_result.text.split("\n")[:3]
                preview = " | ".join(sample_lines)
                if len(preview) > 60:
                    preview = preview[:57] + "..."
                logger.info(f"Página {page_num} processada. Prévia: '{preview or '[Sem Texto]'}'")

            # 5. Exportar resultado final
            file_stem = input_path.stem
            fmt = output_format.strip().lower()

            if fmt == "pdf":
                dest_path = output_dir / f"{file_stem}_searchable.pdf"
                logger.info(f"Gerando PDF pesquisável em: {dest_path}")
                PDFExporter().export(document, dest_path)
                
            elif fmt in ("txt", "text"):
                dest_path = output_dir / f"{file_stem}.txt"
                logger.info(f"Gerando arquivo de texto simples em: {dest_path}")
                TXTExporter().export(document, dest_path)
                
            elif fmt in ("md", "markdown"):
                dest_path = output_dir / f"{file_stem}.md"
                logger.info(f"Gerando arquivo Markdown em: {dest_path}")
                MarkdownExporter().export(document, dest_path)
                
            else:
                raise ValueError(f"Formato de exportação desconhecido: '{output_format}'")

            return dest_path
