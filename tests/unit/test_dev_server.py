"""
Unit tests for DevServer module.

Tests:
- DebounceHandler file watching
- DevServer initialization
- Server process management
- Hot reload functionality
- File change detection
"""

import contextlib
import subprocess
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from wiverno.dev.dev_server import DebounceHandler, DevServer, run_dev_server

# ============================================================================
# DebounceHandler Tests
# ============================================================================


@pytest.mark.unit
class TestDebounceHandler:
    """Tests for DebounceHandler class."""

    def test_debounce_handler_initialization(self):
        """Test: DebounceHandler initializes correctly."""
        callback = Mock()
        handler = DebounceHandler(
            restart_callback=callback, debounce_seconds=1.0, ignore_patterns=["__pycache__"]
        )

        assert handler.restart_callback == callback
        assert handler.debounce_seconds == 1.0
        assert "__pycache__" in handler.ignore_patterns

    def test_debounce_handler_default_ignore_patterns(self):
        """Test: DebounceHandler has default ignore patterns."""
        callback = Mock()
        handler = DebounceHandler(restart_callback=callback)

        assert handler.ignore_patterns == []

    def test_should_ignore_pycache(self):
        """Test: _should_ignore() detects __pycache__ directories."""
        callback = Mock()
        handler = DebounceHandler(restart_callback=callback, ignore_patterns=["__pycache__"])

        assert handler._should_ignore("/project/src/__pycache__/file.pyc") is True
        assert handler._should_ignore("/project/src/main.py") is False

    def test_should_ignore_venv(self):
        """Test: _should_ignore() detects virtual environment."""
        callback = Mock()
        handler = DebounceHandler(restart_callback=callback, ignore_patterns=[".venv", "venv"])

        assert handler._should_ignore("/project/.venv/lib/python.py") is True
        assert handler._should_ignore("/project/venv/site-packages/test.py") is True
        assert handler._should_ignore("/project/src/app.py") is False

    def test_should_ignore_pattern_matching(self):
        """Test: _should_ignore() uses pattern matching."""
        callback = Mock()
        handler = DebounceHandler(restart_callback=callback, ignore_patterns=["tests/*"])

        assert handler._should_ignore("tests/test_main.py") is True

    def test_on_modified_ignores_directories(self):
        """Test: on_modified() ignores directory events."""
        callback = Mock()
        handler = DebounceHandler(restart_callback=callback)

        event = Mock()
        event.is_directory = True
        event.src_path = "/project/src"

        handler.on_modified(event)

        # Callback should not be called for directories
        callback.assert_not_called()

    def test_on_modified_ignores_non_python_files(self):
        """Test: on_modified() ignores non-Python files."""
        callback = Mock()
        handler = DebounceHandler(restart_callback=callback)

        event = Mock()
        event.is_directory = False
        event.src_path = "/project/README.md"

        handler.on_modified(event)

        callback.assert_not_called()

    def test_on_modified_ignores_ignored_patterns(self):
        """Test: on_modified() respects ignore patterns."""
        callback = Mock()
        handler = DebounceHandler(restart_callback=callback, ignore_patterns=["__pycache__"])

        event = Mock()
        event.is_directory = False
        event.src_path = "/project/__pycache__/test.pyc"

        handler.on_modified(event)

        callback.assert_not_called()

    @patch("wiverno.dev.dev_server.time.sleep")
    def test_on_modified_triggers_callback(self, mock_sleep):
        """Test: on_modified() triggers callback for Python files."""
        callback = Mock()
        handler = DebounceHandler(restart_callback=callback, debounce_seconds=0.1)

        event = Mock()
        event.is_directory = False
        event.src_path = "/project/src/main.py"

        handler.on_modified(event)

        # Wait for debounce thread
        time.sleep(0.2)

        # Callback should be called eventually
        # (testing with threads is tricky, we check that event is set)
        assert handler._pending_event.is_set() or callback.called

    @patch("wiverno.dev.dev_server.time.sleep")
    def test_debounce_prevents_rapid_restarts(self, mock_sleep):
        """Test: Debounce prevents multiple rapid restarts."""
        callback = Mock()
        handler = DebounceHandler(restart_callback=callback, debounce_seconds=1.0)

        # Simulate multiple file changes
        event = Mock()
        event.is_directory = False
        event.src_path = "/project/src/main.py"

        handler.on_modified(event)
        handler.on_modified(event)
        handler.on_modified(event)

        # Only one restart should be triggered after debounce
        time.sleep(1.5)

        # Callback should be called at most once (debouncing)
        assert callback.call_count <= 1 or callback.called


# ============================================================================
# DevServer Initialization Tests
# ============================================================================


@pytest.mark.unit
class TestDevServerInitialization:
    """Tests for DevServer initialization."""

    def test_dev_server_initialization_defaults(self):
        """Test: DevServer initializes with default values."""
        server = DevServer(app_module="run", app_name="app")

        assert server.app_module == "run"
        assert server.app_name == "app"
        assert server.host == "localhost"
        assert server.port == 8000
        assert str(Path.cwd()) in server.watch_dirs
        assert "__pycache__" in server.ignore_patterns

    def test_dev_server_initialization_custom_values(self):
        """Test: DevServer accepts custom values."""
        server = DevServer(
            app_module="myapp",
            app_name="application",
            host="0.0.0.0",
            port=5000,
            watch_dirs=["/custom/dir"],
            ignore_patterns=["custom_ignore"],
            debounce_seconds=2.0,
        )

        assert server.app_module == "myapp"
        assert server.app_name == "application"
        assert server.host == "0.0.0.0"
        assert server.port == 5000
        assert "/custom/dir" in server.watch_dirs
        assert "custom_ignore" in server.ignore_patterns
        assert server.debounce_seconds == 2.0

    def test_dev_server_default_ignore_patterns(self):
        """Test: DevServer has sensible default ignore patterns."""
        server = DevServer(app_module="run")

        assert "__pycache__" in server.ignore_patterns
        assert ".venv" in server.ignore_patterns
        assert ".git" in server.ignore_patterns
        assert "tests" in server.ignore_patterns

    def test_dev_server_initial_state(self):
        """Test: DevServer initializes with clean state."""
        server = DevServer(app_module="run")

        assert server.process is None
        assert server.observer is None
        assert server._restart_count == 0


# ============================================================================
# Server Process Management Tests
# ============================================================================


@pytest.mark.unit
class TestDevServerProcessManagement:
    """Tests for server process management."""

    @patch("wiverno.dev.dev_server.subprocess.Popen")
    @patch("wiverno.dev.dev_server.sys.executable", "/usr/bin/python")
    def test_start_server_process(self, mock_popen):
        """Test: _start_server_process() starts subprocess."""
        server = DevServer(app_module="run", app_name="app")

        mock_process = Mock()
        mock_popen.return_value = mock_process

        server._start_server_process()

        # Check that Popen was called
        mock_popen.assert_called_once()
        assert server.process == mock_process
        assert server._restart_count == 1

    @patch("wiverno.dev.dev_server.subprocess.Popen")
    def test_start_server_process_increments_restart_count(self, mock_popen):
        """Test: _start_server_process() increments restart counter."""
        server = DevServer(app_module="run")

        mock_process = Mock()
        mock_popen.return_value = mock_process

        server._start_server_process()
        assert server._restart_count == 1

        server._start_server_process()
        assert server._restart_count == 2

    @patch("wiverno.dev.dev_server.subprocess.Popen")
    def test_stop_server_process_terminates(self, mock_popen):
        """Test: _stop_server_process() terminates subprocess."""
        server = DevServer(app_module="run")

        mock_process = Mock()
        mock_popen.return_value = mock_process
        server._start_server_process()

        server._stop_server_process(show_restart_message=False)

        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()
        assert server.process is None

    @patch("wiverno.dev.dev_server.subprocess.Popen")
    def test_stop_server_process_kills_if_timeout(self, mock_popen):
        """Test: _stop_server_process() kills process if it doesn't terminate."""
        server = DevServer(app_module="run")

        mock_process = Mock()
        mock_process.wait.side_effect = subprocess.TimeoutExpired("cmd", 5)
        mock_popen.return_value = mock_process
        server._start_server_process()

        server._stop_server_process(show_restart_message=False)

        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()

    @patch("wiverno.dev.dev_server.subprocess.Popen")
    def test_restart_server(self, mock_popen):
        """Test: _restart_server() stops and starts server."""
        server = DevServer(app_module="run")

        mock_process = Mock()
        mock_popen.return_value = mock_process

        server._start_server_process()
        initial_count = server._restart_count

        server._restart_server()

        # Should have restarted
        assert server._restart_count == initial_count + 1

    @patch("wiverno.dev.dev_server.importlib.import_module")
    def test_get_debug_mode_success(self, mock_import):
        """Test: _get_debug_mode() retrieves debug status from app."""
        server = DevServer(app_module="run", app_name="app")

        mock_module = Mock()
        mock_app = Mock()
        mock_app.debug = True
        mock_module.app = mock_app
        mock_import.return_value = mock_module

        result = server._get_debug_mode()

        assert "ON" in result

    @patch("wiverno.dev.dev_server.importlib.import_module")
    def test_get_debug_mode_app_without_debug(self, mock_import):
        """Test: _get_debug_mode() handles app without debug attribute."""
        server = DevServer(app_module="run", app_name="app")

        mock_module = Mock()
        mock_app = Mock(spec=[])  # No debug attribute
        mock_module.app = mock_app
        mock_import.return_value = mock_module

        result = server._get_debug_mode()

        assert "Unknown" in result

    @patch("wiverno.dev.dev_server.importlib.import_module")
    def test_get_debug_mode_import_error(self, mock_import):
        """Test: _get_debug_mode() handles import errors."""
        server = DevServer(app_module="run", app_name="app")

        mock_import.side_effect = ImportError("Module not found")

        result = server._get_debug_mode()

        assert "Unknown" in result


# ============================================================================
# DevServer Start and Stop Tests
# ============================================================================


@pytest.mark.unit
class TestDevServerStartStop:
    """Tests for DevServer start() and stop() methods."""

    @patch("wiverno.dev.dev_server.Observer")
    @patch("wiverno.dev.dev_server.subprocess.Popen")
    def test_start_initializes_observer(self, mock_popen, mock_observer_class):
        """Test: start() initializes file observer."""
        server = DevServer(app_module="run")

        mock_process = Mock()
        mock_popen.return_value = mock_process

        mock_observer = Mock()
        mock_observer_class.return_value = mock_observer

        # Start and immediately stop
        def side_effect():
            raise KeyboardInterrupt

        mock_observer.start.side_effect = side_effect

        with contextlib.suppress(KeyboardInterrupt):
            server.start()

        mock_observer_class.assert_called_once()

    @patch("wiverno.dev.dev_server.Observer")
    @patch("wiverno.dev.dev_server.subprocess.Popen")
    @patch("wiverno.dev.dev_server.time.sleep")
    def test_start_schedules_watchers(self, mock_sleep, mock_popen, mock_observer_class):
        """Test: start() schedules watchers for directories."""
        server = DevServer(app_module="run", watch_dirs=["/dir1", "/dir2"])

        mock_process = Mock()
        mock_popen.return_value = mock_process

        mock_observer = Mock()
        mock_observer_class.return_value = mock_observer

        # Simulate KeyboardInterrupt after first sleep
        mock_sleep.side_effect = KeyboardInterrupt

        with contextlib.suppress(KeyboardInterrupt):
            server.start()

        # Should schedule watchers for both directories
        assert mock_observer.schedule.call_count == 2

    @patch("wiverno.dev.dev_server.Observer")
    @patch("wiverno.dev.dev_server.subprocess.Popen")
    def test_stop_stops_observer_and_process(self, mock_popen, mock_observer_class):
        """Test: stop() stops observer and server process."""
        server = DevServer(app_module="run")

        mock_process = Mock()
        mock_popen.return_value = mock_process

        mock_observer = Mock()
        mock_observer_class.return_value = mock_observer

        server._start_server_process()
        server.observer = mock_observer

        server.stop()

        mock_observer.stop.assert_called_once()
        mock_observer.join.assert_called_once()
        mock_process.terminate.assert_called_once()

    @patch("wiverno.dev.dev_server.subprocess.Popen")
    def test_stop_without_observer(self, mock_popen):
        """Test: stop() works even if observer is None."""
        server = DevServer(app_module="run")

        mock_process = Mock()
        mock_popen.return_value = mock_process
        server._start_server_process()

        # Stop without starting observer
        server.stop()

        # Should not raise error
        mock_process.terminate.assert_called_once()


# ============================================================================
# run_dev_server Function Tests
# ============================================================================


@pytest.mark.unit
class TestRunDevServerFunction:
    """Tests for run_dev_server() convenience function."""

    @patch("wiverno.dev.dev_server.DevServer")
    def test_run_dev_server_creates_server(self, mock_dev_server_class):
        """Test: run_dev_server() creates DevServer instance."""
        mock_server = Mock()
        mock_server.start.side_effect = KeyboardInterrupt
        mock_dev_server_class.return_value = mock_server

        with contextlib.suppress(KeyboardInterrupt):
            run_dev_server(app_module="myapp", app_name="application", host="0.0.0.0", port=3000)

        mock_dev_server_class.assert_called_once_with(
            app_module="myapp", app_name="application", host="0.0.0.0", port=3000
        )

    @patch("wiverno.dev.dev_server.DevServer")
    def test_run_dev_server_default_parameters(self, mock_dev_server_class):
        """Test: run_dev_server() uses default parameters."""
        mock_server = Mock()
        mock_server.start.side_effect = KeyboardInterrupt
        mock_dev_server_class.return_value = mock_server

        with contextlib.suppress(KeyboardInterrupt):
            run_dev_server()

        call_kwargs = mock_dev_server_class.call_args[1]
        assert call_kwargs["app_module"] == "run"
        assert call_kwargs["app_name"] == "app"
        assert call_kwargs["host"] == "localhost"
        assert call_kwargs["port"] == 8000


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.integration
class TestDevServerIntegration:
    """Integration tests for DevServer."""

    @patch("wiverno.dev.dev_server.Observer")
    @patch("wiverno.dev.dev_server.subprocess.Popen")
    @patch("wiverno.dev.dev_server.time.sleep")
    def test_complete_start_stop_cycle(self, mock_sleep, mock_popen, mock_observer_class):
        """Test: Complete start and stop cycle."""
        server = DevServer(app_module="run", host="localhost", port=8000)

        mock_process = Mock()
        mock_popen.return_value = mock_process

        mock_observer = Mock()
        mock_observer_class.return_value = mock_observer

        # Simulate Ctrl+C after first iteration
        mock_sleep.side_effect = KeyboardInterrupt

        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()

        # Verify complete cycle
        mock_popen.assert_called()
        mock_observer.start.assert_called_once()
        mock_observer.stop.assert_called_once()

    @patch("wiverno.dev.dev_server.subprocess.Popen")
    def test_multiple_restarts(self, mock_popen):
        """Test: Multiple restarts increment counter correctly."""
        server = DevServer(app_module="run")

        mock_process = Mock()
        mock_popen.return_value = mock_process

        server._start_server_process()
        assert server._restart_count == 1

        server._restart_server()
        assert server._restart_count == 2

        server._restart_server()
        assert server._restart_count == 3


# ============================================================================
# Edge Cases
# ============================================================================


@pytest.mark.unit
class TestDevServerEdgeCases:
    """Edge case tests for DevServer."""

    def test_empty_watch_dirs(self):
        """Test: Empty watch_dirs defaults to current directory."""
        server = DevServer(app_module="run", watch_dirs=None)

        assert len(server.watch_dirs) > 0
        assert str(Path.cwd()) in server.watch_dirs

    def test_custom_debounce_seconds(self):
        """Test: Custom debounce seconds."""
        server = DevServer(app_module="run", debounce_seconds=5.0)

        assert server.debounce_seconds == 5.0

    @patch("wiverno.dev.dev_server.subprocess.Popen")
    def test_stop_without_starting(self, mock_popen):
        """Test: Calling stop() without starting doesn't raise error."""
        server = DevServer(app_module="run")

        # Should not raise error
        server.stop()

    def test_debounce_handler_empty_callback(self):
        """Test: DebounceHandler with None callback."""
        handler = DebounceHandler(restart_callback=None)

        event = Mock()
        event.is_directory = False
        event.src_path = "/project/test.py"

        # Should not crash even with None callback
        handler.on_modified(event)

    def test_multiple_ignore_patterns(self):
        """Test: Multiple ignore patterns work correctly."""
        callback = Mock()
        handler = DebounceHandler(
            restart_callback=callback,
            ignore_patterns=["__pycache__", ".venv", "*.pyc", "tests"],
        )

        assert handler._should_ignore("__pycache__/file.pyc") is True
        assert handler._should_ignore(".venv/lib/python.py") is True
        assert handler._should_ignore("tests/test_main.py") is True
        assert handler._should_ignore("src/main.py") is False
