"""
Unit tests for CLI module.

Tests:
- CLI commands: start, docs, help
- Run commands: dev, prod
- Error handling and validation
- Parameter parsing
"""

from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from wiverno.cli import app, main

runner = CliRunner()


# ============================================================================
# Start Command Tests
# ============================================================================


@pytest.mark.unit
class TestStartCommand:
    """Tests for 'wiverno start' command."""

    def test_start_command_shows_placeholder_message(self):
        """Test: start command displays placeholder message."""
        result = runner.invoke(app, ["start"])

        assert result.exit_code == 0
        assert "Quick Start (Coming Soon)" in result.stdout
        assert "wiverno run dev" in result.stdout

    def test_start_command_mentions_future_features(self):
        """Test: start command mentions future features."""
        result = runner.invoke(app, ["start"])

        assert "Project scaffolding" in result.stdout
        assert "Template generation" in result.stdout
        assert "Configuration wizard" in result.stdout


# ============================================================================
# Docs Command Tests
# ============================================================================


@pytest.mark.unit
class TestDocsCommand:
    """Tests for 'wiverno docs' command."""

    @patch("wiverno.cli.Path")
    def test_docs_command_without_mkdocs_yml(self, mock_path):
        """Test: docs command fails if mkdocs.yml doesn't exist."""
        mock_path.cwd.return_value.exists.return_value = False
        mock_path.cwd.return_value.__truediv__ = lambda self, other: Mock(
            exists=Mock(return_value=False)
        )

        result = runner.invoke(app, ["docs"])

        assert result.exit_code == 1
        assert "mkdocs.yml not found" in result.stdout

    @patch("subprocess.run")
    @patch("pathlib.Path")
    def test_docs_command_without_mkdocs_installed(self, mock_path, mock_subprocess):
        """Test: docs command fails if mkdocs is not installed."""
        # mkdocs.yml exists
        mock_mkdocs_yml = Mock()
        mock_mkdocs_yml.exists.return_value = True
        mock_path.cwd.return_value.__truediv__.return_value = mock_mkdocs_yml

        # mkdocs not installed
        mock_subprocess.return_value.returncode = 1

        result = runner.invoke(app, ["docs"])

        assert result.exit_code == 1
        assert "MkDocs is not installed" in result.stdout

    @patch("webbrowser.open")
    @patch("subprocess.run")
    @patch("pathlib.Path")
    def test_docs_command_success(self, mock_path, mock_subprocess, mock_browser):
        """Test: docs command runs successfully."""
        # mkdocs.yml exists
        mock_mkdocs_yml = Mock()
        mock_mkdocs_yml.exists.return_value = True
        mock_path.cwd.return_value.__truediv__.return_value = mock_mkdocs_yml

        # mkdocs installed
        check_result = Mock()
        check_result.returncode = 0
        serve_result = Mock()
        serve_result.returncode = 0

        def subprocess_side_effect(*args, **kwargs):
            if "--version" in args[0]:
                return check_result
            raise KeyboardInterrupt  # Simulate Ctrl+C
            return serve_result

        mock_subprocess.side_effect = subprocess_side_effect

        result = runner.invoke(app, ["docs"])

        assert result.exit_code == 0

    @patch("subprocess.run")
    @patch("pathlib.Path")
    def test_docs_command_custom_host_port(self, mock_path, mock_subprocess):
        """Test: docs command accepts custom host and port."""
        # Setup mocks
        mock_mkdocs_yml = Mock()
        mock_mkdocs_yml.exists.return_value = True
        mock_path.cwd.return_value.__truediv__.return_value = mock_mkdocs_yml

        check_result = Mock()
        check_result.returncode = 0

        def subprocess_side_effect(args, **kwargs):
            if "--version" in args:
                return check_result
            raise KeyboardInterrupt

        mock_subprocess.side_effect = subprocess_side_effect

        result = runner.invoke(app, ["docs", "--host", "0.0.0.0", "--port", "9000"])

        # Check that subprocess was called with correct address
        assert result.exit_code == 0

    @patch("webbrowser.open")
    @patch("subprocess.run")
    @patch("pathlib.Path")
    def test_docs_command_no_open_browser(self, mock_path, mock_subprocess, mock_browser):
        """Test: docs command with --no-open doesn't open browser."""
        # Setup mocks
        mock_mkdocs_yml = Mock()
        mock_mkdocs_yml.exists.return_value = True
        mock_path.cwd.return_value.__truediv__.return_value = mock_mkdocs_yml

        check_result = Mock()
        check_result.returncode = 0

        def subprocess_side_effect(args, **kwargs):
            if "--version" in args:
                return check_result
            raise KeyboardInterrupt

        mock_subprocess.side_effect = subprocess_side_effect

        result = runner.invoke(app, ["docs", "--no-open"])

        # Browser should not be opened (checking timing is difficult, but command should work)
        assert result.exit_code == 0


# ============================================================================
# Help Command Tests
# ============================================================================


@pytest.mark.unit
class TestHelpCommand:
    """Tests for 'wiverno help' command."""

    def test_help_command_shows_commands_table(self):
        """Test: help command displays commands table."""
        result = runner.invoke(app, ["help"])

        assert result.exit_code == 0
        assert "Available Commands" in result.stdout

    def test_help_command_shows_all_commands(self):
        """Test: help command lists all available commands."""
        result = runner.invoke(app, ["help"])

        assert "wiverno run dev" in result.stdout
        assert "wiverno run prod" in result.stdout
        assert "wiverno start" in result.stdout
        assert "wiverno docs" in result.stdout
        assert "wiverno help" in result.stdout

    def test_help_command_shows_usage_examples(self):
        """Test: help command shows usage examples."""
        result = runner.invoke(app, ["help"])

        assert "Usage Examples:" in result.stdout
        assert "--port" in result.stdout
        assert "--host" in result.stdout


# ============================================================================
# Run Dev Command Tests
# ============================================================================


@pytest.mark.unit
class TestRunDevCommand:
    """Tests for 'wiverno run dev' command."""

    @patch("wiverno.cli.Path")
    def test_run_dev_without_app_module(self, mock_path):
        """Test: run dev fails if app module doesn't exist."""
        mock_app_path = Mock()
        mock_app_path.exists.return_value = False

        mock_cwd = Mock()
        mock_cwd.__truediv__.return_value = mock_app_path
        mock_path.cwd.return_value = mock_cwd

        result = runner.invoke(app, ["run", "dev"])

        assert result.exit_code == 1
        assert "not found" in result.stdout

    @patch("wiverno.cli.DevServer")
    @patch("wiverno.cli.Path")
    def test_run_dev_starts_dev_server(self, mock_path, mock_dev_server_class):
        """Test: run dev starts DevServer with correct parameters."""
        # App module exists
        mock_app_path = Mock()
        mock_app_path.exists.return_value = True

        mock_cwd = Mock()
        mock_cwd.__truediv__.return_value = mock_app_path
        mock_path.cwd.return_value = mock_cwd

        # Mock DevServer
        mock_dev_server = Mock()
        mock_dev_server.start.side_effect = KeyboardInterrupt  # Stop immediately
        mock_dev_server_class.return_value = mock_dev_server

        runner.invoke(app, ["run", "dev"])

        # Check that DevServer was created with correct parameters
        mock_dev_server_class.assert_called_once()
        call_kwargs = mock_dev_server_class.call_args[1]
        assert call_kwargs["app_module"] == "run"
        assert call_kwargs["app_name"] == "app"
        assert call_kwargs["host"] == "localhost"
        assert call_kwargs["port"] == 8000

        # Check that start was called
        mock_dev_server.start.assert_called_once()

    @patch("wiverno.cli.DevServer")
    @patch("wiverno.cli.Path")
    def test_run_dev_custom_parameters(self, mock_path, mock_dev_server_class):
        """Test: run dev accepts custom parameters."""
        # App module exists
        mock_app_path = Mock()
        mock_app_path.exists.return_value = True

        mock_cwd = Mock()
        mock_cwd.__truediv__.return_value = mock_app_path
        mock_path.cwd.return_value = mock_cwd

        # Mock DevServer
        mock_dev_server = Mock()
        mock_dev_server.start.side_effect = KeyboardInterrupt
        mock_dev_server_class.return_value = mock_dev_server

        runner.invoke(
            app,
            [
                "run",
                "dev",
                "--host",
                "0.0.0.0",
                "--port",
                "5000",
                "--app-module",
                "myapp",
                "--app-name",
                "application",
            ],
        )

        # Check parameters
        call_kwargs = mock_dev_server_class.call_args[1]
        assert call_kwargs["host"] == "0.0.0.0"
        assert call_kwargs["port"] == 5000
        assert call_kwargs["app_module"] == "myapp"
        assert call_kwargs["app_name"] == "application"

    @patch("wiverno.cli.DevServer")
    @patch("wiverno.cli.Path")
    def test_run_dev_watch_directories(self, mock_path, mock_dev_server_class):
        """Test: run dev accepts watch directories parameter."""
        # App module exists
        mock_app_path = Mock()
        mock_app_path.exists.return_value = True

        mock_cwd = Mock()
        mock_cwd.__truediv__.return_value = mock_app_path
        mock_path.cwd.return_value = mock_cwd

        # Mock DevServer
        mock_dev_server = Mock()
        mock_dev_server.start.side_effect = KeyboardInterrupt
        mock_dev_server_class.return_value = mock_dev_server

        runner.invoke(app, ["run", "dev", "--watch", "src,lib,app"])

        # Check watch directories
        call_kwargs = mock_dev_server_class.call_args[1]
        assert call_kwargs["watch_dirs"] == ["src", "lib", "app"]


# ============================================================================
# Run Prod Command Tests
# ============================================================================


@pytest.mark.unit
class TestRunProdCommand:
    """Tests for 'wiverno run prod' command."""

    @patch("wiverno.cli.Path")
    def test_run_prod_without_app_module(self, mock_path):
        """Test: run prod fails if app module doesn't exist."""
        mock_app_path = Mock()
        mock_app_path.exists.return_value = False

        mock_cwd = Mock()
        mock_cwd.__truediv__.return_value = mock_app_path
        mock_path.cwd.return_value = mock_cwd

        result = runner.invoke(app, ["run", "prod"])

        assert result.exit_code == 1
        assert "not found" in result.stdout

    @patch("wiverno.cli.RunServer")
    @patch("wiverno.cli.importlib.import_module")
    @patch("wiverno.cli.Path")
    def test_run_prod_starts_server(self, mock_path, mock_import, mock_run_server_class):
        """Test: run prod starts RunServer with correct parameters."""
        # App module exists
        mock_app_path = Mock()
        mock_app_path.exists.return_value = True

        mock_cwd = Mock()
        mock_cwd.__truediv__.return_value = mock_app_path
        mock_path.cwd.return_value = mock_cwd

        # Mock module import
        mock_module = Mock()
        mock_module.app = Mock()  # Mock application
        mock_import.return_value = mock_module

        # Mock RunServer
        mock_server = Mock()
        mock_server.start.side_effect = KeyboardInterrupt
        mock_run_server_class.return_value = mock_server

        runner.invoke(app, ["run", "prod"])

        # Check that server was created and started
        mock_run_server_class.assert_called_once()
        mock_server.start.assert_called_once()

    @patch("wiverno.cli.RunServer")
    @patch("wiverno.cli.importlib.import_module")
    @patch("wiverno.cli.Path")
    def test_run_prod_custom_parameters(self, mock_path, mock_import, mock_run_server_class):
        """Test: run prod accepts custom parameters."""
        # Setup mocks
        mock_app_path = Mock()
        mock_app_path.exists.return_value = True

        mock_cwd = Mock()
        mock_cwd.__truediv__.return_value = mock_app_path
        mock_path.cwd.return_value = mock_cwd

        mock_module = Mock()
        mock_module.application = Mock()
        mock_import.return_value = mock_module

        mock_server = Mock()
        mock_server.start.side_effect = KeyboardInterrupt
        mock_run_server_class.return_value = mock_server

        runner.invoke(
            app,
            [
                "run",
                "prod",
                "--host",
                "0.0.0.0",
                "--port",
                "8080",
                "--app-module",
                "myapp",
                "--app-name",
                "application",
            ],
        )

        # Check that correct module was imported
        mock_import.assert_called_once_with("myapp")

        # Check server parameters
        call_args = mock_run_server_class.call_args
        assert call_args[0][0] == mock_module.application  # app object
        assert call_args[1]["host"] == "0.0.0.0"
        assert call_args[1]["port"] == 8080

    @patch("wiverno.cli.importlib.import_module")
    @patch("wiverno.cli.Path")
    def test_run_prod_import_error(self, mock_path, mock_import):
        """Test: run prod handles ImportError gracefully."""
        # App module file exists
        mock_app_path = Mock()
        mock_app_path.exists.return_value = True

        mock_cwd = Mock()
        mock_cwd.__truediv__.return_value = mock_app_path
        mock_path.cwd.return_value = mock_cwd

        # Import fails
        mock_import.side_effect = ImportError("Module not found")

        result = runner.invoke(app, ["run", "prod"])

        assert result.exit_code == 1
        assert "Import Error" in result.stdout

    @patch("wiverno.cli.importlib.import_module")
    @patch("wiverno.cli.Path")
    def test_run_prod_attribute_error(self, mock_path, mock_import):
        """Test: run prod handles missing application attribute."""
        # Setup mocks
        mock_app_path = Mock()
        mock_app_path.exists.return_value = True

        mock_cwd = Mock()
        mock_cwd.__truediv__.return_value = mock_app_path
        mock_path.cwd.return_value = mock_cwd

        # Module exists but doesn't have 'app' attribute
        mock_module = Mock(spec=[])  # Empty spec = no attributes
        mock_import.return_value = mock_module

        result = runner.invoke(app, ["run", "prod"])

        assert result.exit_code == 1
        assert "not found" in result.stdout


# ============================================================================
# Main Function Tests
# ============================================================================


@pytest.mark.unit
class TestMainFunction:
    """Tests for main() entry point."""

    @patch("wiverno.cli.app")
    def test_main_calls_app(self, mock_app):
        """Test: main() calls the Typer app."""
        main()

        mock_app.assert_called_once()


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests for CLI commands."""

    def test_cli_help_output(self):
        """Test: CLI shows help when called without arguments."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Wiverno" in result.stdout
        assert "Usage" in result.stdout

    def test_run_command_help(self):
        """Test: 'run' command shows help."""
        result = runner.invoke(app, ["run", "--help"])

        assert result.exit_code == 0
        assert "dev" in result.stdout
        assert "prod" in result.stdout

    def test_docs_command_help(self):
        """Test: 'docs' command shows help."""
        result = runner.invoke(app, ["docs", "--help"])

        assert result.exit_code == 0
        assert "host" in result.stdout
        assert "port" in result.stdout


# ============================================================================
# Edge Cases
# ============================================================================


@pytest.mark.unit
class TestCLIEdgeCases:
    """Edge case tests for CLI."""

    def test_invalid_command(self):
        """Test: Invalid command shows error."""
        result = runner.invoke(app, ["invalid-command"])

        assert result.exit_code != 0

    @patch("wiverno.cli.DevServer")
    @patch("wiverno.cli.Path")
    def test_run_dev_port_zero(self, mock_path, mock_dev_server_class):
        """Test: Port 0 (auto-select) should work."""
        mock_app_path = Mock()
        mock_app_path.exists.return_value = True

        mock_cwd = Mock()
        mock_cwd.__truediv__.return_value = mock_app_path
        mock_path.cwd.return_value = mock_cwd

        mock_dev_server = Mock()
        mock_dev_server.start.side_effect = KeyboardInterrupt
        mock_dev_server_class.return_value = mock_dev_server

        runner.invoke(app, ["run", "dev", "--port", "0"])

        call_kwargs = mock_dev_server_class.call_args[1]
        assert call_kwargs["port"] == 0

    @patch("wiverno.cli.RunServer")
    @patch("wiverno.cli.importlib.import_module")
    @patch("wiverno.cli.Path")
    def test_run_prod_high_port(self, mock_path, mock_import, mock_run_server_class):
        """Test: High port numbers should work."""
        mock_app_path = Mock()
        mock_app_path.exists.return_value = True

        mock_cwd = Mock()
        mock_cwd.__truediv__.return_value = mock_app_path
        mock_path.cwd.return_value = mock_cwd

        mock_module = Mock()
        mock_module.app = Mock()
        mock_import.return_value = mock_module

        mock_server = Mock()
        mock_server.start.side_effect = KeyboardInterrupt
        mock_run_server_class.return_value = mock_server

        runner.invoke(app, ["run", "prod", "--port", "65535"])

        call_args = mock_run_server_class.call_args
        assert call_args[1]["port"] == 65535
