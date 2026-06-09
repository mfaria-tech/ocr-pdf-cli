"""Testes unitários da interface CLI."""

from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from ocr_pdf_cli.cli.main import app
from ocr_pdf_cli.version import __version__

runner = CliRunner()

def test_cli_version() -> None:
    """Verifica se a flag --version retorna a versão correta."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout

def test_cli_info() -> None:
    """Verifica o comando info de forma isolada."""
    # Mock de get_system_info para garantir independência operacional do teste
    mock_sys_info = {
        "os": "win32",
        "friendly_os": "Windows",
        "platform": "Windows-10",
        "python_version": "3.11.0",
        "is_termux": False
    }
    with patch("ocr_pdf_cli.cli.commands.get_system_info", return_value=mock_sys_info):
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "OCR PDF CLI" in result.stdout
        assert "cat" in result.stdout or "m_type" not in result.stdout  # Verificando se rodou ok

def test_cli_info_mascot_alt() -> None:
    """Verifica se o comando info aceita o mascote alternativo."""
    mock_sys_info = {
        "os": "win32",
        "friendly_os": "Windows",
        "platform": "Windows-10",
        "python_version": "3.11.0",
        "is_termux": False
    }
    with patch("ocr_pdf_cli.cli.commands.get_system_info", return_value=mock_sys_info):
        result = runner.invoke(app, ["info", "--mascot", "cat_alt"])
        assert result.exit_code == 0
        # Checar se o mascote alt foi renderizado
        assert "╱|、" in result.stdout

def test_cli_engines() -> None:
    """Verifica se o comando engines é executado sem erros."""
    result = runner.invoke(app, ["engines"])
    assert result.exit_code == 0
    assert "tesseract" in result.stdout
    assert "easyocr" in result.stdout
    assert "paddleocr" in result.stdout
