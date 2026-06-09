"""Utilitário de registro de logs formatados."""

import logging
from rich.logging import RichHandler

def setup_logger(verbose: bool = False) -> logging.Logger:
    """Configura o logger padrão da aplicação utilizando formatação Rich.

    Args:
        verbose: Se True, define o nível de log para DEBUG. Caso contrário, INFO.

    Returns:
        O logger configurado.
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # Configuração básica do root logger para utilizar o RichHandler
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                markup=True,
                show_path=False,
                omit_repeated_times=True
            )
        ]
    )
    
    logger = logging.getLogger("ocr_pdf_cli")
    logger.setLevel(level)
    return logger
