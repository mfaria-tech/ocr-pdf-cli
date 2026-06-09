"""Ponto de entrada principal da CLI ocr-pdf."""

from typing import Optional
import typer
from ocr_pdf_cli.version import __version__
from ocr_pdf_cli.cli.commands import commands_app, display_welcome_banner

# Cria a aplicação principal do Typer
app = typer.Typer(
    name="ocr-pdf",
    help="Ferramenta CLI profissional para converter PDFs contendo imagens/scans em documentos pesquisáveis usando OCR local de forma offline."
)

# Registra os comandos secundários diretamente no comando principal
# Isso faz com que 'info', 'engines' e 'convert' fiquem disponíveis
app.registered_commands.extend(commands_app.registered_commands)

def version_callback(value: bool) -> None:
    """Callback para exibir a versão e encerrar imediatamente."""
    if value:
        typer.echo(f"ocr-pdf-cli versão {__version__}")
        raise typer.Exit()

@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None,
        "--version", "-V",
        callback=version_callback,
        is_eager=True,
        help="Exibe a versão do programa e sai."
    ),
    welcome: bool = typer.Option(
        False,
        "--welcome",
        help="Exibe o banner colorido e mascote de boas-vindas."
    )
) -> None:
    """OCR PDF CLI - Conversão de documentos escaneados e OCR offline."""
    if welcome:
        display_welcome_banner("cat")
        raise typer.Exit()

if __name__ == "__main__":
    app()
