import logging
from collections.abc import Callable
from wsgiref.simple_server import make_server

logger = logging.getLogger(__name__)


class RunServer:
    """
    Simple WSGI server to run a Wiverno application.

    Attributes:
        application (Callable): A WSGI-compatible application.
        host (str): The hostname to bind the server to.
        port (int): The port number to bind the server to.
    """

    def __init__(self, application: Callable, host: str = "localhost", port: int = 8000):
        """
        Initializes the server with application, host, and port.

        Args:
            application (Callable): A WSGI-compatible application.
            host (str, optional): Hostname for the server. Defaults to 'localhost'.
            port (int, optional): Port for the server. Defaults to 8000.
        """
        self.host: str = host
        self.port: int = port
        self.application: Callable = application

    def start(self) -> None:
        """
        Starts the WSGI server and serves the application forever.

        The server will continue running until interrupted by KeyboardInterrupt (Ctrl+C).
        """
        try:
            with make_server(self.host, self.port, self.application) as httpd:
                logger.info(f"Serving on http://{self.host}:{self.port} ...")
                httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped by user.")
