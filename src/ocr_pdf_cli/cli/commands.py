"""Implementação dos comandos CLI utilizando Typer e Rich."""

import logging
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ocr_pdf_cli.version import __version__
from ocr_pdf_cli.config.settings import settings
from ocr_pdf_cli.engines import ENGINES, get_engine
from ocr_pdf_cli.core.pipeline import OCRPipeline
from ocr_pdf_cli.utils.system import get_system_info
from ocr_pdf_cli.utils.logger import setup_logger

console = Console()
logger = logging.getLogger("ocr_pdf_cli")

# Cores em estilo Pastel inspiradas no PDA/Termux Bootstrap
PDA_LAVENDER = "#B4BEFE"
PDA_PINK = "#F5C2E7"
PDA_YELLOW = "#F9E2AF"
PDA_MINT = "#A6E3A1"
PDA_WHITE = "#CDD6F4"
PDA_MOON_PURPLE = "#CBA6F7"

# Logo ASCII Colorida
LOGO_ASCII = f"""[bold {PDA_MOON_PURPLE}] ██████╗  ██████╗██████╗[/]
[bold {PDA_LAVENDER}]██╔═══██╗██╔════╝██╔══██╗[/]
[bold {PDA_MINT}]██║   ██║██║     ██████╔╝[/]
[bold {PDA_YELLOW}]██║   ██║██║     ██╔══██╗[/]
[bold {PDA_PINK}]╚██████╔╝╚██████╗██║  ██║[/]
[bold {PDA_MOON_PURPLE}] ╚═════╝  ╚═════╝╚═╝  ╚═╝[/]

[bold {PDA_LAVENDER}]██████╗ ██████╗ ███████╗[/]
[bold {PDA_MINT}]██╔══██╗██╔══██╗██╔════╝[/]
[bold {PDA_YELLOW}]██████╔╝██║  ██║█████╗  [/]
[bold {PDA_PINK}]██╔═══╝ ██║  ██║██╔══╝  [/]
[bold {PDA_MOON_PURPLE}]██║     ██████╔╝██║     [/]
[bold {PDA_LAVENDER}]╚═╝     ╚═════╝ ╚═╝     [/]

      [bold {PDA_WHITE}]OCR PDF CLI[/]"""

# Mascotes disponíveis
MASCOTES = {
    "cat": f"""[bold {PDA_PINK}]  //\\_/\\\\ [/]
[bold {PDA_MOON_PURPLE}](=^･ω･^=)[/]
[bold {PDA_LAVENDER}] (")_(")[/]""",
    "cat_alt": f"""[bold {PDA_MINT}] ╱|、[/]
[bold {PDA_YELLOW}](˚ˎ 。7[/]
[bold {PDA_LAVENDER}] |、˜〵[/]
[bold {PDA_MOON_PURPLE}]じしˍ,)ノ[/]"""
}

def display_welcome_banner(mascot_type: Optional[str] = "cat") -> None:
    """Exibe o banner colorido e o mascote correspondente."""
    banner_content = LOGO_ASCII + "\n\n"
    
    if mascot_type and mascot_type in MASCOTES:
        banner_content += f"Mascote do Projeto:\n{MASCOTES[mascot_type]}\n"

    console.print(
        Panel(
            banner_content,
            border_style=f"bold {PDA_LAVENDER}",
            title=f"[bold {PDA_WHITE}]O C R - P D F - C L I[/bold {PDA_WHITE}]",
            subtitle=f"[bold {PDA_PINK}]v{__version__}[/bold {PDA_PINK}]",
            expand=False
        )
    )

# Criação do app Typer para comandos
commands_app = typer.Typer(help="Comandos auxiliares do OCR PDF CLI")

@commands_app.command(name="info")
def info_command(
    mascot: str = typer.Option(
        "cat",
        "--mascot", "-m",
        help="Tipo de mascote a ser exibido ('cat', 'cat_alt' ou 'none')"
    )
) -> None:
    """Exibe informações do sistema, compatibilidade de engines e mascotes."""
    # Exibe o banner principal com o mascote solicitado
    m_type = mascot if mascot != "none" else None
    display_welcome_banner(mascot_type=m_type)
    
    sys_info = get_system_info()
    
    # Exibe tabela do sistema
    sys_table = Table(
        title="[bold #CDD6F4]Informações do Sistema[/bold #CDD6F4]",
        title_style="bold",
        show_header=False,
        border_style=PDA_LAVENDER
    )
    sys_table.add_column("Chave", style=f"bold {PDA_MINT}")
    sys_table.add_column("Valor", style=PDA_WHITE)
    
    sys_table.add_row("Sistema Operacional", sys_info["friendly_os"])
    sys_table.add_row("Plataforma", sys_info["platform"])
    sys_table.add_row("Versão do Python", sys_info["python_version"])
    sys_table.add_row("Executando em Termux?", "Sim (Android)" if sys_info["is_termux"] else "Não")
    
    console.print(sys_table)
    console.print()

    # Tabela com as engines e se estão ativas
    eng_table = Table(
        title="[bold #CDD6F4]Mecanismos OCR (Engines)[/bold #CDD6F4]",
        border_style=PDA_LAVENDER
    )
    eng_table.add_column("Engine", style=f"bold {PDA_MOON_PURPLE}")
    eng_table.add_column("Disponível", style="bold")
    eng_table.add_column("Status", style=PDA_WHITE)

    for eng_name in ENGINES:
        try:
            eng_instance = get_engine(eng_name)
            is_avail = eng_instance.is_available
            avail_str = "[green]✔ Sim[/green]" if is_avail else "[red]✘ Não[/red]"
            status_str = "Pronto para uso" if is_avail else "Falta instalar/configurar"
            if eng_name != "tesseract" and is_avail:
                status_str += " (Opcional)"
            elif eng_name != "tesseract":
                status_str = "Placeholder / Não implementado"
        except Exception:
            avail_str = "[red]✘ Não[/red]"
            status_str = "Erro ao carregar"
            
        eng_table.add_row(eng_name, avail_str, status_str)

    console.print(eng_table)

@commands_app.command(name="engines")
def engines_command() -> None:
    """Lista os mecanismos OCR configurados e seus status de disponibilidade."""
    table = Table(
        title="[bold #CDD6F4]Motores de Reconhecimento OCR[/bold #CDD6F4]",
        border_style=PDA_LAVENDER
    )
    table.add_column("Motor (Engine)", style=f"bold {PDA_MINT}")
    table.add_column("Disponibilidade", style="bold")
    table.add_column("Padrão", style="bold")
    table.add_column("Tipo", style=PDA_WHITE)

    for name in ENGINES:
        try:
            eng = get_engine(name)
            avail = "[green]Disponível[/green]" if eng.is_available else "[red]Indisponível[/red]"
        except Exception:
            avail = "[red]Erro de carregamento[/red]"
            
        is_default = "[yellow]Sim[/yellow]" if name == settings.default_engine else "Não"
        type_str = "Principal" if name == "tesseract" else "Opcional (Esqueleto)"
        table.add_row(name, avail, is_default, type_str)

    console.print(table)

@commands_app.command(name="convert")
def convert_command(
    input_file: Path = typer.Argument(
        ...,
        help="Caminho para o arquivo PDF escaneado (imagens)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True
    ),
    output_dir: Path = typer.Option(
        Path("output"),
        "--output", "-o",
        help="Diretório onde o arquivo gerado será salvo"
    ),
    format_type: str = typer.Option(
        settings.default_output_format,
        "--format", "-f",
        help="Formato de exportação ('pdf', 'txt' ou 'markdown')"
    ),
    engine: str = typer.Option(
        settings.default_engine,
        "--engine", "-e",
        help="Mecanismo OCR a ser utilizado ('tesseract', 'easyocr', 'paddleocr')"
    ),
    language: str = typer.Option(
        settings.default_language,
        "--lang", "-l",
        help="Idioma a ser utilizado pelo OCR (ex: 'por', 'eng')"
    ),
    dpi: int = typer.Option(
        settings.default_dpi,
        "--dpi", "-d",
        help="DPI a ser utilizado na renderização das páginas do PDF"
    ),
    preprocess: bool = typer.Option(
        True,
        "--preprocess/--no-preprocess",
        help="Habilita/Desabilita conversão prévia da imagem para tons de cinza"
    ),
    binarize: bool = typer.Option(
        False,
        "--binarize/--no-binarize",
        help="Habilita/Desabilita binarização (P&B puro) antes do processamento"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Habilita exibição de logs detalhados (DEBUG)"
    )
) -> None:
    """Converte um PDF composto por imagens em documento pesquisável ou extrai o texto."""
    # Configura o logger
    setup_logger(verbose=verbose)
    
    try:
        pipeline = OCRPipeline(
            engine_name=engine,
            language=language,
            dpi=dpi,
            preprocess=preprocess,
            binarize=binarize
        )
        
        pipeline.run(
            input_path=input_file,
            output_dir=output_dir,
            output_format=format_type
        )
    except Exception as e:
        console.print(f"\n[red][bold]Erro de Execução:[/bold] {e}[/red]")
        if verbose:
            logger.exception("Detalhes da falha:")
        raise typer.Exit(code=1)
