"""
Development server with hot reload functionality.

This module provides a development server that automatically restarts when
Python source files are modified, making it easier to develop and test
Wiverno applications.
"""

import sys
import time
import subprocess
from pathlib import Path
from threading import Thread, Event
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

console = Console()


class DebounceHandler(FileSystemEventHandler):
    """
    File system event handler with debouncing to prevent excessive restarts.
    
    Attributes:
        restart_callback: Function to call when files change.
        debounce_seconds: Minimum time between restarts in seconds.
        ignore_patterns: List of patterns to ignore.
    """

    def __init__(
        self,
        restart_callback: Any,
        debounce_seconds: float = 1.0,
        ignore_patterns: list[str] | None = None,
    ) -> None:
        """
        Initialize the debounce handler.
        
        Args:
            restart_callback: Function to call on file changes.
            debounce_seconds: Time to wait before triggering restart.
            ignore_patterns: Patterns to ignore (e.g., __pycache__, .venv).
        """
        super().__init__()
        self.restart_callback = restart_callback
        self.debounce_seconds = debounce_seconds
        self.ignore_patterns = ignore_patterns or []
        self._last_triggered = 0.0
        self._pending_event: Event = Event()
        self._debounce_thread: Thread | None = None

    def _should_ignore(self, path: str) -> bool:
        """
        Check if a path should be ignored based on patterns.
        
        Args:
            path: File path to check.
            
        Returns:
            True if path should be ignored, False otherwise.
        """
        path_obj = Path(path)
        path_str = str(path_obj)
        
        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return True
            if path_obj.match(pattern):
                return True
        return False

    def _debounce_restart(self) -> None:
        """Execute restart after debounce period."""
        time.sleep(self.debounce_seconds)
        if self._pending_event.is_set():
            current_time = time.time()
            if current_time - self._last_triggered >= self.debounce_seconds:
                self._last_triggered = current_time
                self._pending_event.clear()
                self.restart_callback()

    def on_modified(self, event: FileSystemEvent) -> None:
        """
        Handle file modification events.
        
        Args:
            event: File system event.
        """
        if event.is_directory:
            return

        # Only watch Python files
        if not event.src_path.endswith(".py"):
            return

        # Check ignore patterns
        if self._should_ignore(event.src_path):
            return

        console.print(f"[yellow]WARNING: File changed:[/yellow] {event.src_path}")

        self._pending_event.set()
        
        # Start debounce thread if not already running
        if self._debounce_thread is None or not self._debounce_thread.is_alive():
            self._debounce_thread = Thread(target=self._debounce_restart, daemon=True)
            self._debounce_thread.start()


class DevServer:
    """
    Development server with hot reload capabilities.
    
    This server monitors Python files for changes and automatically restarts
    the application when modifications are detected.
    """

    def __init__(
        self,
        app_module: str,
        app_name: str = "app",
        host: str = "localhost",
        port: int = 8000,
        watch_dirs: list[str] | None = None,
        ignore_patterns: list[str] | None = None,
        debounce_seconds: float = 1.0,
    ) -> None:
        """
        Initialize the development server.
        
        Args:
            app_module: Module path containing the WSGI application (e.g., 'run').
            app_name: Name of the application variable in the module (default: 'app').
            host: Server host address.
            port: Server port.
            watch_dirs: Directories to watch for changes. If None, watches current directory.
            ignore_patterns: Patterns to ignore (default: __pycache__, .venv, tests).
            debounce_seconds: Time to wait before restarting after file changes.
        """
        self.app_module = app_module
        self.app_name = app_name
        self.host = host
        self.port = port
        self.watch_dirs = watch_dirs or [str(Path.cwd())]
        self.ignore_patterns = ignore_patterns or [
            "__pycache__",
            ".venv",
            "venv",
            ".git",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "tests",
            "htmlcov",
            ".coverage",
        ]
        self.debounce_seconds = debounce_seconds
        self.process: subprocess.Popen[bytes] | None = None
        self.observer: Observer | None = None 
        self._restart_count = 0

    def _get_debug_mode(self) -> str:
        """
        Get debug mode status from the application.
        
        Returns:
            String representation of debug mode status.
        """
        try:
            import importlib
            module = importlib.import_module(self.app_module)
            app = getattr(module, self.app_name)
            if hasattr(app, 'debug'):
                return "[green]ON[/green]" if app.debug else "[red]OFF[/red]"
            return "[dim]Unknown[/dim]"
        except Exception:
            return "[dim]Unknown[/dim]"

    def _start_server_process(self) -> None:
        """Start the WSGI server process."""
        if self.process:
            self._stop_server_process()

        self._restart_count += 1
        
        # Get debug mode from app
        debug_status = self._get_debug_mode()
        
        # Print server info immediately
        console.print(Panel(
            Text.from_markup(
                f"[bold cyan]Wiverno[/bold cyan] [bold green]Development Server[/bold green]\n\n"
                f"[cyan]Server:[/cyan] http://{self.host}:{self.port}\n"
                f"[cyan]Debug Mode:[/cyan] {debug_status}\n"
                f"[cyan]Restart:[/cyan] #{self._restart_count}\n"
                f"[dim]Press Ctrl+C to stop[/dim]"
            ),
            border_style="green",
            expand=False,
        ))

        # Create command to run the server
        # We'll use a Python command that imports and runs the app
        python_code = f"""
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from wiverno.core.server import RunServer
from {self.app_module} import {self.app_name}

server = RunServer({self.app_name}, host="{self.host}", port={self.port})
server.start()
"""
        
        # Start subprocess without capturing output - let it print directly
        self.process = subprocess.Popen(
            [sys.executable, "-u", "-c", python_code],
        )

    def _stop_server_process(self, show_restart_message: bool = True) -> None:
        """Stop the WSGI server process.
        
        Args:
            show_restart_message: If True, show the restarting message.
        """
        if self.process:
            if show_restart_message:
                console.print("[yellow]>> Restarting server...[/yellow]")
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def _restart_server(self) -> None:
        """Restart the server after file changes."""
        console.print("[yellow]>> Server restarting...[/yellow]")
        self._stop_server_process(show_restart_message=False)
        self._start_server_process()

    def start(self) -> None:
        """
        Start the development server with hot reload.
        
        This method starts the server and sets up file watching for automatic
        restarts when Python files are modified.
        
        Hot Reload работает следующим образом:
        1. Watchdog отслеживает изменения в .py файлах в указанных директориях
        2. При изменении файла срабатывает событие FileSystemEvent
        3. Debounce механизм ждет 1 секунду, чтобы собрать все изменения
        4. После задержки запускается перезапуск сервера
        5. Старый процесс сервера корректно завершается (terminate)
        6. Запускается новый процесс с обновленным кодом
        7. Счетчик перезапусков увеличивается для отслеживания
        """
        console.print(
            "[bold cyan]Wiverno[/bold cyan] [bold]Hot Reload[/bold] [green]enabled[/green]"
        )

        # Start the server
        self._start_server_process()

        # Set up file watching
        event_handler = DebounceHandler(
            restart_callback=self._restart_server,
            debounce_seconds=self.debounce_seconds,
            ignore_patterns=self.ignore_patterns,
        )

        self.observer = Observer()
        for watch_dir in self.watch_dirs:
            self.observer.schedule(event_handler, watch_dir, recursive=True)
        
        self.observer.start()

        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold red]>> Stopping development server...[/bold red]")
            self.stop()

    def stop(self) -> None:
        """Stop the development server and file watcher."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        self._stop_server_process(show_restart_message=False)
        console.print("[green]>> Server stopped successfully[/green]")


def run_dev_server(
    app_module: str = "run",
    app_name: str = "app",
    host: str = "localhost",
    port: int = 8000,
) -> None:
    """
    Convenience function to run the development server.
    
    Args:
        app_module: Module path containing the WSGI application.
        app_name: Name of the application variable in the module.
        host: Server host address.
        port: Server port.
    """
    dev_server = DevServer(
        app_module=app_module,
        app_name=app_name,
        host=host,
        port=port,
    )
    dev_server.start()
