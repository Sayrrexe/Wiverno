import logging
import signal
import sys
from collections.abc import Callable
from typing import Any
from wsgiref.simple_server import WSGIServer, make_server

logger = logging.getLogger(__name__)


class RunServer:
    """
    WSGI server to run a Wiverno application.

    This server is built on Python's wsgiref.simple_server and includes
    improvements for better production readiness:
    - Graceful shutdown handling
    - Enhanced logging
    - Error handling
    - Configurable request queue size

    Note:
        While this server is improved for stability, for high-traffic production
        environments, consider using dedicated WSGI servers like Gunicorn, uWSGI,
        or Waitress which offer better performance and concurrency.

    Attributes:
        application (Callable): A WSGI-compatible application.
        host (str): The hostname to bind the server to.
        port (int): The port number to bind the server to.
        request_queue_size (int): Maximum number of queued connections.
    """

    def __init__(
        self,
        application: Callable[..., Any],
        host: str = "localhost",
        port: int = 8000,
        request_queue_size: int = 5,
    ) -> None:
        """
        Initializes the server with application, host, and port.

        Args:
            application (Callable): A WSGI-compatible application.
            host (str, optional): Hostname for the server. Defaults to 'localhost'.
            port (int, optional): Port for the server. Defaults to 8000.
            request_queue_size (int, optional): Max queued connections. Defaults to 5.
        """
        self.host: str = host
        self.port: int = port
        self.application: Callable[..., Any] = application
        self.request_queue_size: int = request_queue_size
        self._httpd: WSGIServer | None = None
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum: int, frame: Any) -> None:
        """
        Handle shutdown signals gracefully.

        Args:
            signum: Signal number.
            frame: Current stack frame.
        """
        signal_name = signal.Signals(signum).name
        logger.info(f"Received {signal_name}, initiating graceful shutdown...")
        self.stop()
        sys.exit(0)

    def start(self) -> None:
        """
        Starts the WSGI server and serves the application forever.

        The server will continue running until interrupted by SIGINT (Ctrl+C)
        or SIGTERM signal. Implements graceful shutdown to finish processing
        current requests before stopping.

        Raises:
            OSError: If the server cannot bind to the specified host:port.
        """
        try:
            self._httpd = make_server(
                self.host,
                self.port,
                self.application,
                server_class=WSGIServer,
            )
            self._httpd.request_queue_size = self.request_queue_size

            logger.info(
                f"Wiverno server started on http://{self.host}:{self.port}"
            )
            logger.info(
                f"Request queue size: {self.request_queue_size}"
            )
            logger.info("Press Ctrl+C to stop the server")

            self._httpd.serve_forever()

        except OSError as e:
            logger.error(f"Failed to start server: {e}")
            raise
        except KeyboardInterrupt:
            logger.info("Server stopped by user.")
            self.stop()
        except Exception as e:
            logger.exception(f"Unexpected error in server: {e}")
            self.stop()
            raise

    def stop(self) -> None:
        """
        Stop the server gracefully.

        Shuts down the server, allowing current requests to complete.
        """
        if self._httpd:
            logger.info("Shutting down server...")
            self._httpd.shutdown()
            self._httpd.server_close()
            logger.info("Server stopped successfully.")
            self._httpd = None
