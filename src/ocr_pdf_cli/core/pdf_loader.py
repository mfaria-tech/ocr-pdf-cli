"""Módulo para carregamento e renderização de PDFs."""

import logging
from pathlib import Path
from typing import List, Tuple
from PIL import Image
import pypdfium2 as pdfium  # type: ignore

from ocr_pdf_cli.models.document import Document
from ocr_pdf_cli.models.page import Page

logger = logging.getLogger("ocr_pdf_cli")

class PDFLoader:
    """Carrega arquivos PDF e renderiza suas páginas como imagens PIL."""

    def load_pdf(self, pdf_path: Path, dpi: int = 300) -> Tuple[Document, List[Image.Image]]:
        """Carrega o PDF e renderiza cada página em uma imagem.

        Args:
            pdf_path: O caminho do arquivo PDF a ser carregado.
            dpi: A resolução de renderização das imagens.

        Returns:
            Uma tupla contendo o modelo Document e uma lista de imagens PIL das páginas.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")

        logger.debug(f"Abrindo PDF via pypdfium2: {pdf_path}")
        pdf = pdfium.PdfDocument(str(pdf_path))
        
        document = Document(
            file_path=str(pdf_path),
            metadata={"pages_count": len(pdf), "dpi": dpi}
        )
        
        images: List[Image.Image] = []

        for page_idx in range(len(pdf)):
            page_num = page_idx + 1
            logger.debug(f"Renderizando página {page_num}/{len(pdf)} a {dpi} DPI...")
            
            page = pdf.get_page(page_idx)
            width, height = page.get_size()  # Largura e altura em pontos PDF
            
            # Fator de escala para renderizar a imagem no DPI correto
            scale = dpi / 72.0
            
            # Renderiza a página para um bitmap e converte para imagem PIL
            bitmap = page.render(scale=scale)
            pil_image = bitmap.to_pil()
            
            # Adiciona ao resultado
            images.append(pil_image)
            
            # Armazena metadados da página
            page_model = Page(
                page_number=page_num,
                width=int(width),
                height=int(height),
            )
            document.pages.append(page_model)
            
        return document, images
