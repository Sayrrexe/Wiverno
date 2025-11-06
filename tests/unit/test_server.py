"""
Unit tests for RunServer class.

Tests server initialization, configuration, and WSGI integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from wiverno.core.server import RunServer


# ============================================================================
# RunServer Initialization Tests
# ============================================================================


@pytest.mark.unit
class TestRunServerInitialization:
    """Server initialization tests."""

    def test_server_initialization_default_values(self):
        """Server should initialize with default values."""
        app = Mock()
        server = RunServer(app)

        assert server.application is app
        assert server.host == "localhost"
        assert server.port == 8000

    def test_server_initialization_custom_host_port(self):
        """Test: Custom host and port can be set."""
        app = Mock()
        server = RunServer(app, host="0.0.0.0", port=5000)

        assert server.host == "0.0.0.0"
        assert server.port == 5000

    def test_server_stores_application(self):
        """Test: Server should store application reference."""
        app = Mock()
        server = RunServer(app)

        assert server.application is app

    def test_server_with_different_ports(self):
        """Test: Different server instances can have different ports."""
        app = Mock()
        server1 = RunServer(app, port=8000)
        server2 = RunServer(app, port=9000)

        assert server1.port == 8000
        assert server2.port == 9000


# ============================================================================
# start() Method Tests
# ============================================================================


@pytest.mark.unit
class TestRunServerStart:
    """Tests for start() method for launching the server."""

    @patch("wiverno.core.server.make_server")
    def test_start_creates_wsgi_server(self, mock_make_server):
        """Test: start() should create WSGI server."""
        app = Mock()
        server = RunServer(app, host="localhost", port=8080)

        # Configure mock
        mock_httpd = MagicMock()
        mock_make_server.return_value.__enter__.return_value = mock_httpd

        # Interrupt serve_forever so test doesn't hang
        mock_httpd.serve_forever.side_effect = KeyboardInterrupt

        # Start server
        server.start()

        # Check that make_server was called with correct parameters
        mock_make_server.assert_called_once_with("localhost", 8080, app)

    @patch("wiverno.core.server.make_server")
    def test_start_calls_serve_forever(self, mock_make_server):
        """Test: start() should call serve_forever()."""
        app = Mock()
        server = RunServer(app)

        # Configure mock
        mock_httpd = MagicMock()
        mock_make_server.return_value.__enter__.return_value = mock_httpd
        mock_httpd.serve_forever.side_effect = KeyboardInterrupt

        # Start server
        server.start()

        # Check that serve_forever was called
        mock_httpd.serve_forever.assert_called_once()

    @patch("wiverno.core.server.make_server")
    def test_start_handles_keyboard_interrupt(self, mock_make_server):
        """Test: start() should correctly handle KeyboardInterrupt."""
        app = Mock()
        server = RunServer(app)

        # Configure mock to simulate Ctrl+C
        mock_httpd = MagicMock()
        mock_make_server.return_value.__enter__.return_value = mock_httpd
        mock_httpd.serve_forever.side_effect = KeyboardInterrupt

        # Start and check that no exception was raised
        try:
            server.start()
        except KeyboardInterrupt:
            pytest.fail("KeyboardInterrupt was not handled")

    @patch("wiverno.core.server.make_server")
    @patch("wiverno.core.server.logger")
    def test_start_logs_server_info(self, mock_logger, mock_make_server):
        """Test: start() should log server startup information."""
        app = Mock()
        server = RunServer(app, host="127.0.0.1", port=3000)

        # Configure mock
        mock_httpd = MagicMock()
        mock_make_server.return_value.__enter__.return_value = mock_httpd
        mock_httpd.serve_forever.side_effect = KeyboardInterrupt

        # Start server
        server.start()

        # Check logging
        mock_logger.info.assert_any_call("Serving on http://127.0.0.1:3000 ...")

    @patch("wiverno.core.server.make_server")
    @patch("wiverno.core.server.logger")
    def test_start_logs_shutdown_message(self, mock_logger, mock_make_server):
        """Test: start() should log shutdown message."""
        app = Mock()
        server = RunServer(app)

        # Configure mock
        mock_httpd = MagicMock()
        mock_make_server.return_value.__enter__.return_value = mock_httpd
        mock_httpd.serve_forever.side_effect = KeyboardInterrupt

        # Start server
        server.start()

        # Check shutdown logging
        mock_logger.info.assert_any_call("Server stopped by user.")


# ============================================================================
# RunServer Integration Tests
# ============================================================================


@pytest.mark.integration
class TestRunServerIntegration:
    """Integration tests for RunServer with real WSGI application."""

    @patch("wiverno.core.server.make_server")
    def test_server_with_real_wsgi_app(self, mock_make_server):
        """Test: Server should work with real WSGI application."""

        # Create simple WSGI application
        def simple_app(environ, start_response):
            status = "200 OK"
            headers = [("Content-Type", "text/plain")]
            start_response(status, headers)
            return [b"Hello, World!"]

        server = RunServer(simple_app, host="0.0.0.0", port=8080)

        # Configure mock
        mock_httpd = MagicMock()
        mock_make_server.return_value.__enter__.return_value = mock_httpd
        mock_httpd.serve_forever.side_effect = KeyboardInterrupt

        # Start server
        server.start()

        # Check that application was passed to make_server
        mock_make_server.assert_called_once_with("0.0.0.0", 8080, simple_app)

    @patch("wiverno.core.server.make_server")
    def test_server_with_multiple_instances(self, mock_make_server):
        """Test: Multiple server instances can be created."""
        app1 = Mock()
        app2 = Mock()

        server1 = RunServer(app1, port=8001)
        server2 = RunServer(app2, port=8002)

        # Check that servers are independent
        assert server1.application is app1
        assert server2.application is app2
        assert server1.port == 8001
        assert server2.port == 8002


# ============================================================================
# Edge Cases and Boundary Conditions
# ============================================================================


@pytest.mark.unit
class TestRunServerEdgeCases:
    """Edge case tests for RunServer."""

    def test_server_with_port_zero(self):
        """Test: Port 0 (automatic port selection) should work."""
        app = Mock()
        server = RunServer(app, port=0)

        assert server.port == 0

    def test_server_with_high_port_number(self):
        """Test: High port numbers should be accepted."""
        app = Mock()
        server = RunServer(app, port=65535)

        assert server.port == 65535

    def test_server_with_ipv6_address(self):
        """Test: IPv6 address should be accepted."""
        app = Mock()
        server = RunServer(app, host="::1")  # IPv6 localhost

        assert server.host == "::1"

    def test_server_with_callable_application(self):
        """Test: Application should be a callable object."""
        
        class CallableApp:
            def __call__(self, environ, start_response):
                status = "200 OK"
                headers = [("Content-Type", "text/plain")]
                start_response(status, headers)
                return [b"Callable App"]

        app = CallableApp()
        server = RunServer(app)

        assert callable(server.application)
        assert server.application is app

    def test_server_with_empty_host(self):
        """Test: Empty host (all interfaces) should work."""
        app = Mock()
        server = RunServer(app, host="")

        assert server.host == ""

