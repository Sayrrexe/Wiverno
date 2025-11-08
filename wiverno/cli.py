"""
CLI interface for Wiverno framework.

Provides commands for running development and production servers,
generating documentation, and managing Wiverno projects.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

app = typer.Typer(
    name="wiverno",
    help="Wiverno - A lightweight WSGI framework for Python",
    add_completion=False,
)

console = Console()


@app.command("start")
def start() -> None:
    """
    Quick start a Wiverno server (placeholder command).
    
    This command will be enhanced in future versions to provide
    project scaffolding and quick start functionality.
    """
    console.print(Panel(
        Text.from_markup(
            "[bold yellow]Quick Start (Coming Soon)[/bold yellow]\n\n"
            "This command is currently a placeholder.\n"
            "Use [cyan]wiverno run dev[/cyan] to start a development server.\n\n"
            "Future features:\n"
            "  - Project scaffolding\n"
            "  - Template generation\n"
            "  - Configuration wizard"
        ),
        border_style="yellow",
        expand=False,
    ))


@app.command("docs")
def docs(
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        "-h",
        help="Documentation server host",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Documentation server port",
    ),
    open_browser: bool = typer.Option(
        True,
        "--open/--no-open",
        help="Open browser automatically when serving",
    ),
) -> None:
    """
    Serve project documentation using MkDocs with live reload.
    
    This command starts a local documentation server that automatically
    reloads when you make changes to your documentation files.
    
    Examples:
        wiverno docs                    # Serve docs at http://127.0.0.1:8000
        wiverno docs --port 3000        # Serve on custom port
        wiverno docs --no-open          # Don't open browser automatically
    """
    import subprocess
    import sys
    import webbrowser
    from time import sleep
    
    # Check if mkdocs.yml exists
    mkdocs_config = Path.cwd() / "mkdocs.yml"
    if not mkdocs_config.exists():
        console.print(
            "[bold red]ERROR:[/bold red] mkdocs.yml not found in current directory.\n\n"
            "[yellow]This command requires MkDocs to be configured.[/yellow]\n"
            f"[dim]Current directory: {Path.cwd()}[/dim]\n\n"
            "[cyan]To set up documentation:[/cyan]\n"
            "1. Create mkdocs.yml in your project root\n"
            "2. Install mkdocs-material: [green]uv pip install mkdocs-material[/green]\n"
            "3. Run: [green]wiverno docs --serve[/green]"
        )
        raise typer.Exit(1)
    
    try:
        # Check if mkdocs is installed
        result = subprocess.run(
            [sys.executable, "-m", "mkdocs", "--version"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise FileNotFoundError
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print(
            "[bold red]ERROR:[/bold red] MkDocs is not installed.\n\n"
            "[yellow]Install MkDocs to use this command:[/yellow]\n"
            "[green]$ uv pip install mkdocs-material mkdocstrings[python][/green]\n\n"
            "Or install all dev dependencies:\n"
            "[green]$ uv pip install -e .[dev][/green]"
        )
        raise typer.Exit(1)
    
    # Serve documentation
    url = f"http://{host}:{port}"
    console.print(Panel(
        Text.from_markup(
            "[bold cyan]Wiverno[/bold cyan] [bold green]Documentation Server[/bold green]\n\n"
            f"[cyan]Server:[/cyan] {url}\n"
            f"[cyan]Config:[/cyan] mkdocs.yml\n"
            f"[dim]Press Ctrl+C to stop[/dim]\n\n"
            "[yellow]Watching for changes...[/yellow]"
        ),
        border_style="green",
        expand=False,
    ))
    
    # Open browser if requested
    if open_browser:
        # Give server a moment to start
        def open_in_browser():
            sleep(1.5)
            try:
                webbrowser.open(url)
                console.print(f"[dim]>> Opened {url} in browser[/dim]")
            except Exception:
                pass
        
        import threading
        browser_thread = threading.Thread(target=open_in_browser, daemon=True)
        browser_thread.start()
    
    try:
        # Run mkdocs serve
        subprocess.run(
            [sys.executable, "-m", "mkdocs", "serve", "-a", f"{host}:{port}"],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]ERROR:[/bold red] Server failed: {e}")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[green]>> Documentation server stopped[/green]")


@app.command("help")
def show_help() -> None:
    """
    Show comprehensive help and usage examples.
    """
    console.print(Panel(
        Text.from_markup(
            "[bold cyan]Wiverno[/bold cyan] [bold]CLI Help[/bold]\n\n"
            "A lightweight WSGI framework for building fast and flexible Python web applications."
        ),
        border_style="cyan",
        expand=False,
    ))
    
    # Create commands table
    table = Table(title="Available Commands", show_header=True, header_style="bold cyan")
    table.add_column("Command", style="green", width=20)
    table.add_column("Description", style="white")
    
    table.add_row(
        "wiverno run dev",
        "Start development server with hot reload",
    )
    table.add_row(
        "wiverno run prod",
        "Start production server",
    )
    table.add_row(
        "wiverno start",
        "Quick start (placeholder for future features)",
    )
    table.add_row(
        "wiverno docs",
        "Serve documentation with live reload",
    )
    table.add_row(
        "wiverno help",
        "Show this help message",
    )
    
    console.print(table)
    
    # Usage examples
    console.print("\n[bold cyan]Usage Examples:[/bold cyan]\n")
    examples = [
        ("Start dev server with defaults", "wiverno run dev"),
        ("Start dev server on custom port", "wiverno run dev --port 3000"),
        ("Start dev server on all interfaces", "wiverno run dev --host 0.0.0.0"),
        ("Start production server", "wiverno run prod --host 0.0.0.0 --port 8080"),
        ("Custom app location", "wiverno run dev --app-module myapp --app-name application"),
        ("Serve documentation", "wiverno docs"),
        ("Serve docs on custom port", "wiverno docs --port 8001"),
    ]
    
    for desc, cmd in examples:
        console.print(f"  [dim]{desc}:[/dim]")
        console.print(f"  [green]$ {cmd}[/green]\n")
    
    console.print("[dim]For more information, visit: https://github.com/Sayrrexe/Wiverno[/dim]")


run_app = typer.Typer(help="Run Wiverno server in different modes")
app.add_typer(run_app, name="run")


@run_app.command("dev")
def run_dev(
    host: str = typer.Option(
        "localhost",
        "--host",
        "-h",
        help="Server host address",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Server port number",
    ),
    app_module: str = typer.Option(
        "run",
        "--app-module",
        "-m",
        help="Module containing the WSGI application",
    ),
    app_name: str = typer.Option(
        "app",
        "--app-name",
        "-a",
        help="Name of the application variable in the module",
    ),
    watch_dirs: Optional[str] = typer.Option(
        None,
        "--watch",
        "-w",
        help="Comma-separated list of directories to watch (default: current directory)",
    ),
) -> None:
    """
    Start development server with hot reload.
    
    The development server automatically restarts when Python files are modified,
    making it perfect for development and testing.
    
    Examples:
        wiverno run dev
        wiverno run dev --port 3000
        wiverno run dev --host 0.0.0.0 --port 8080
        wiverno run dev --app-module myapp --app-name application
    """
    try:
        from wiverno.dev.dev_server import DevServer
        
        # Parse watch directories
        watch_dir_list = None
        if watch_dirs:
            watch_dir_list = [d.strip() for d in watch_dirs.split(",")]
        
        # Check if the app module exists
        app_path = Path.cwd() / f"{app_module}.py"
        if not app_path.exists():
            console.print(
                f"[bold red]ERROR:[/bold red] Module '{app_module}.py' not found in current directory.\n"
                f"[dim]Current directory: {Path.cwd()}[/dim]\n\n"
                f"[yellow]TIP:[/yellow] Make sure you're in the project root or specify "
                f"the correct module with --app-module"
            )
            raise typer.Exit(1)
        
        dev_server = DevServer(
            app_module=app_module,
            app_name=app_name,
            host=host,
            port=port,
            watch_dirs=watch_dir_list,
        )
        dev_server.start()
        
    except ImportError as e:
        console.print(
            f"[bold red]Import Error:[/bold red] {e}\n\n"
            "[yellow]TIP:[/yellow] Make sure all development dependencies are installed:\n"
            "[green]$ uv pip install -e .[dev][/green]"
        )
        raise typer.Exit(1)
    except KeyboardInterrupt:
        pass


@run_app.command("prod")
def run_prod(
    host: str = typer.Option(
        "localhost",
        "--host",
        "-h",
        help="Server host address",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Server port number",
    ),
    app_module: str = typer.Option(
        "run",
        "--app-module",
        "-m",
        help="Module containing the WSGI application",
    ),
    app_name: str = typer.Option(
        "app",
        "--app-name",
        "-a",
        help="Name of the application variable in the module",
    ),
) -> None:
    """
    Start production server without hot reload.
    
    This command runs the server in production mode without file watching
    or automatic restarts. Suitable for deployment.
    
    Examples:
        wiverno run prod
        wiverno run prod --host 0.0.0.0 --port 8080
        wiverno run prod --app-module myapp --app-name application
    """
    try:
        console.print(Panel(
            Text.from_markup(
                "[bold cyan]Wiverno[/bold cyan] [bold green]Production Server[/bold green]\n\n"
                f"[cyan]Server:[/cyan] http://{host}:{port}\n"
                f"[cyan]Module:[/cyan] {app_module}.{app_name}\n"
                f"[dim]Press Ctrl+C to stop[/dim]"
            ),
            border_style="green",
            expand=False,
        ))
        
        # Check if the app module exists
        app_path = Path.cwd() / f"{app_module}.py"
        if not app_path.exists():
            console.print(
                f"[bold red]ERROR:[/bold red] Module '{app_module}.py' not found in current directory.\n"
                f"[dim]Current directory: {Path.cwd()}[/dim]\n\n"
                f"[yellow]TIP:[/yellow] Make sure you're in the project root or specify "
                f"the correct module with --app-module"
            )
            raise typer.Exit(1)
        
        # Import and run the application
        import importlib
        from wiverno.core.server import RunServer
        
        module = importlib.import_module(app_module)
        application = getattr(module, app_name)
        
        server = RunServer(application, host=host, port=port)
        server.start()
        
    except ImportError as e:
        console.print(
            f"[bold red]Import Error:[/bold red] {e}\n\n"
            f"[yellow]TIP:[/yellow] Make sure the module '{app_module}' exists and "
            f"contains a variable named '{app_name}'"
        )
        raise typer.Exit(1)
    except AttributeError:
        console.print(
            f"[bold red]ERROR:[/bold red] Application '{app_name}' not found in module '{app_module}'\n\n"
            f"[yellow]TIP:[/yellow] Make sure your {app_module}.py contains:\n"
            f"[green]{app_name} = Wiverno()[/green]"
        )
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[green]>> Server stopped successfully[/green]")


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
