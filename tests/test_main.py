"""Tests for the main module."""

import argparse
import logging
import os
from io import StringIO
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.main import (
    configure_logging,
    create_mcp_app,
    main,
    parse_args,
    validate_rasdaman_connection,
    DEFAULT_RASDAMAN_URL,
    DEFAULT_RASDAMAN_USERNAME,
    DEFAULT_RASDAMAN_PASSWORD,
    DEFAULT_MCP_PORT,
    DEFAULT_MCP_HOST,
    DEFAULT_MCP_TRANSPORT,
)


class TestConfigureLogging:
    """Test cases for configure_logging function."""

    @patch('logging.basicConfig')
    def test_configure_logging_sets_level(self, mock_basic_config):
        """Test that logging level is set correctly."""
        configure_logging("DEBUG")
        mock_basic_config.assert_called()
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs['level'] == logging.DEBUG

        configure_logging("INFO")
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs['level'] == logging.INFO

        configure_logging("WARNING")
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs['level'] == logging.WARNING

        configure_logging("ERROR")
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs['level'] == logging.ERROR

        configure_logging("CRITICAL")
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs['level'] == logging.CRITICAL

    def test_configure_logging_silences_noisy_libs(self):
        """Test that noisy libraries are silenced."""
        configure_logging("DEBUG")
        
        for lib in ["docket.worker", "mcp.server.streamable_http_manager", "mcp.server.lowlevel.server"]:
            assert logging.getLogger(lib).level == logging.WARNING


class TestParseArgs:
    """Test cases for parse_args function."""

    @patch('sys.argv', ['rasdaman-mcp'])
    def test_default_values(self):
        """Test parsing with no arguments uses defaults."""
        args = parse_args()
        
        assert args.transport == DEFAULT_MCP_TRANSPORT
        assert args.port == DEFAULT_MCP_PORT
        assert args.host == DEFAULT_MCP_HOST
        assert args.rasdaman_url == os.getenv("RASDAMAN_URL", DEFAULT_RASDAMAN_URL)
        assert args.username == os.getenv("RASDAMAN_USERNAME", DEFAULT_RASDAMAN_USERNAME)
        assert args.password == os.getenv("RASDAMAN_PASSWORD", DEFAULT_RASDAMAN_PASSWORD)
        assert args.log_level == "INFO"

    @patch('sys.argv', ['rasdaman-mcp', '--transport', 'http'])
    def test_transport_argument(self):
        """Test parsing transport argument."""
        args = parse_args()
        assert args.transport == "http"

    @patch('sys.argv', ['rasdaman-mcp', '--port', '9000'])
    def test_port_argument(self):
        """Test parsing port argument."""
        args = parse_args()
        assert args.port == 9000

    @patch('sys.argv', ['rasdaman-mcp', '--host', '0.0.0.0'])
    def test_host_argument(self):
        """Test parsing host argument."""
        args = parse_args()
        assert args.host == "0.0.0.0"

    @patch('sys.argv', ['rasdaman-mcp', '--rasdaman-url', 'http://custom:8080/ows'])
    def test_rasdaman_url_argument(self):
        """Test parsing rasdaman-url argument."""
        args = parse_args()
        assert args.rasdaman_url == "http://custom:8080/ows"

    @patch('sys.argv', ['rasdaman-mcp', '--username', 'admin'])
    def test_username_argument(self):
        """Test parsing username argument."""
        args = parse_args()
        assert args.username == "admin"

    @patch('sys.argv', ['rasdaman-mcp', '--password', 'secret'])
    def test_password_argument(self):
        """Test parsing password argument."""
        args = parse_args()
        assert args.password == "secret"

    @patch('sys.argv', ['rasdaman-mcp', '--log-level', 'DEBUG'])
    def test_log_level_argument(self):
        """Test parsing log-level argument."""
        args = parse_args()
        assert args.log_level == "DEBUG"

    @patch.dict(os.environ, {'RASDAMAN_URL': 'http://env:8080/ows'})
    @patch('sys.argv', ['rasdaman-mcp'])
    def test_rasdaman_url_from_env(self):
        """Test that RASDAMAN_URL environment variable is used."""
        args = parse_args()
        assert args.rasdaman_url == "http://env:8080/ows"

    @patch.dict(os.environ, {'RASDAMAN_USERNAME': 'envuser'})
    @patch('sys.argv', ['rasdaman-mcp'])
    def test_username_from_env(self):
        """Test that RASDAMAN_USERNAME environment variable is used."""
        args = parse_args()
        assert args.username == "envuser"

    @patch.dict(os.environ, {'RASDAMAN_PASSWORD': 'envpass'})
    @patch('sys.argv', ['rasdaman-mcp'])
    def test_password_from_env(self):
        """Test that RASDAMAN_PASSWORD environment variable is used."""
        args = parse_args()
        assert args.password == "envpass"

    @patch.dict(os.environ, {
        'RASDAMAN_URL': 'http://env:8080/ows',
        'RASDAMAN_USERNAME': 'envuser',
        'RASDAMAN_PASSWORD': 'envpass'
    })
    @patch('sys.argv', [
        'rasdaman-mcp',
        '--rasdaman-url', 'http://arg:8080/ows',
        '--username', 'arguser',
        '--password', 'argpass'
    ])
    def test_cli_args_override_env(self):
        """Test that CLI arguments override environment variables."""
        args = parse_args()
        assert args.rasdaman_url == "http://arg:8080/ows"
        assert args.username == "arguser"
        assert args.password == "argpass"


class TestValidateRasdamanConnection:
    """Test cases for validate_rasdaman_connection function."""

    @patch('src.main.requests.head')
    def test_successful_connection(self, mock_head):
        """Test successful connection validation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response

        # Should not raise any exception
        validate_rasdaman_connection("http://test:8080/rasdaman/ows")
        mock_head.assert_called_once_with("http://test:8080/rasdaman/ows", timeout=5)

    @patch('src.main.requests.head')
    def test_failed_connection(self, mock_head, caplog):
        """Test failed connection validation logs warning."""
        caplog.set_level(logging.WARNING)
        from requests import RequestException
        mock_head.side_effect = RequestException("Connection refused")

        validate_rasdaman_connection("http://test:8080/rasdaman/ows")
        
        assert "Could not reach Rasdaman" in caplog.text


class TestCreateMCPApp:
    """Test cases for create_mcp_app function."""

    @patch('src.main.RasdamanActions')
    @patch('src.main.FastMCP')
    def test_creates_fastmcp_instance(self, mock_fastmcp_class, mock_actions_class):
        """Test that function creates a FastMCP instance."""
        mock_mcp = MagicMock()
        mock_fastmcp_class.return_value = mock_mcp
        
        mock_actions = MagicMock()
        mock_actions.list_coverages_action.return_value = ["cov1", "cov2"]
        mock_actions.describe_coverage_action.return_value = "coverage info"
        mock_actions.wcps_query_crash_course_action.return_value = "crash course"
        mock_actions.execute_wcps_query_action.return_value = "query result"
        mock_actions_class.return_value = mock_actions

        result = create_mcp_app("http://test", "user", "pass")

        mock_fastmcp_class.assert_called_once()
        assert result == mock_mcp

    @patch('src.main.RasdamanActions')
    @patch('src.main.FastMCP')
    def test_registers_tools(self, mock_fastmcp_class, mock_actions_class):
        """Test that all tools are registered with the MCP app."""
        mock_mcp = MagicMock()
        mock_fastmcp_class.return_value = mock_mcp
        
        mock_actions = MagicMock()
        mock_actions_class.return_value = mock_actions

        create_mcp_app("http://test", "user", "pass")

        # Check that tool decorator was called 4 times (for 4 tools)
        assert mock_mcp.tool.call_count == 4

    @patch('src.main.RasdamanActions')
    @patch('src.main.FastMCP')
    def test_creates_rasdaman_actions(self, mock_fastmcp_class, mock_actions_class):
        """Test that RasdamanActions is created with correct parameters."""
        mock_mcp = MagicMock()
        mock_fastmcp_class.return_value = mock_mcp
        
        mock_actions = MagicMock()
        mock_actions_class.return_value = mock_actions

        create_mcp_app("http://test:8080/ows", "testuser", "testpass")

        mock_actions_class.assert_called_once_with(
            rasdaman_url="http://test:8080/ows",
            username="testuser",
            password="testpass"
        )


class TestMain:
    """Test cases for main function."""

    @patch('src.main.validate_rasdaman_connection')
    @patch('src.main.create_mcp_app')
    @patch('src.main.configure_logging')
    @patch('src.main.parse_args')
    def test_main_stdio_transport(self, mock_parse_args, mock_configure_logging, 
                                   mock_create_mcp_app, mock_validate):
        """Test main function with stdio transport."""
        mock_args = MagicMock()
        mock_args.transport = "stdio"
        mock_args.log_level = "INFO"
        mock_args.rasdaman_url = "http://test:8080/ows"
        mock_args.username = "user"
        mock_args.password = "pass"
        mock_parse_args.return_value = mock_args

        mock_mcp = MagicMock()
        mock_create_mcp_app.return_value = mock_mcp

        main()

        mock_configure_logging.assert_called_once_with(log_level="INFO")
        mock_validate.assert_called_once_with("http://test:8080/ows")
        mock_create_mcp_app.assert_called_once_with("http://test:8080/ows", "user", "pass")
        mock_mcp.run.assert_called_once_with(transport="stdio", log_level="INFO")

    @patch('src.main.validate_rasdaman_connection')
    @patch('src.main.create_mcp_app')
    @patch('src.main.configure_logging')
    @patch('src.main.parse_args')
    def test_main_http_transport(self, mock_parse_args, mock_configure_logging,
                                  mock_create_mcp_app, mock_validate):
        """Test main function with http transport."""
        mock_args = MagicMock()
        mock_args.transport = "http"
        mock_args.log_level = "DEBUG"
        mock_args.host = "127.0.0.1"
        mock_args.port = 8000
        mock_args.rasdaman_url = "http://test:8080/ows"
        mock_args.username = "user"
        mock_args.password = "pass"
        mock_parse_args.return_value = mock_args

        mock_mcp = MagicMock()
        mock_create_mcp_app.return_value = mock_mcp

        main()

        mock_mcp.run.assert_called_once_with(
            transport="http", 
            port=8000, 
            host="127.0.0.1",
            log_level="DEBUG"
        )
