"""Tests for the RasdamanActions class."""

import io
import json
import tempfile
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
from PIL import Image
from wcps.model import WCPSClientException
from wcps.service import WCPSResult, WCPSResultType

from src.rasdaman_actions import RasdamanActions, SAVE_THRESHOLD
from src.wcps_crash_course import WCPS_CRASH_COURSE


class TestRasdamanActionsInit:
    """Test cases for RasdamanActions initialization."""

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_init_creates_services(self, mock_wcps_class, mock_wcs_class):
        """Test that initialization creates WCS and WCPS services."""
        mock_wcs_instance = MagicMock()
        mock_wcps_instance = MagicMock()
        mock_wcs_class.return_value = mock_wcs_instance
        mock_wcps_class.return_value = mock_wcps_instance

        actions = RasdamanActions(
            rasdaman_url="http://test:8080/rasdaman/ows",
            username="testuser",
            password="testpass"
        )

        assert actions.rasdaman_url == "http://test:8080/rasdaman/ows"
        assert actions.username == "testuser"
        assert actions.password == "testpass"
        mock_wcs_class.assert_called_once_with(
            "http://test:8080/rasdaman/ows",
            username="testuser",
            password="testpass"
        )
        mock_wcps_class.assert_called_once_with(
            "http://test:8080/rasdaman/ows",
            username="testuser",
            password="testpass"
        )


class TestListCoveragesAction:
    """Test cases for list_coverages_action method."""

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_list_coverages_success(self, mock_wcps_class, mock_wcs_class):
        """Test successful listing of coverages."""
        mock_wcs_instance = MagicMock()
        mock_wcs_instance.list_coverages.return_value = {
            "coverage1": MagicMock(),
            "coverage2": MagicMock(),
            "coverage3": MagicMock()
        }
        mock_wcs_class.return_value = mock_wcs_instance

        actions = RasdamanActions("http://test", "user", "pass")
        result = actions.list_coverages_action()

        assert isinstance(result, list)
        assert len(result) == 3
        assert "coverage1" in result
        assert "coverage2" in result
        assert "coverage3" in result
        mock_wcs_instance.list_coverages.assert_called_once()

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_list_coverages_empty(self, mock_wcps_class, mock_wcs_class):
        """Test listing coverages when none exist."""
        mock_wcs_instance = MagicMock()
        mock_wcs_instance.list_coverages.return_value = {}
        mock_wcs_class.return_value = mock_wcs_instance

        actions = RasdamanActions("http://test", "user", "pass")
        result = actions.list_coverages_action()

        assert isinstance(result, list)
        assert len(result) == 0

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_list_coverages_logs_info(self, mock_wcps_class, mock_wcs_class, caplog):
        """Test that listing coverages logs appropriate messages."""
        import logging
        caplog.set_level(logging.INFO)
        
        mock_wcs_instance = MagicMock()
        mock_wcs_instance.list_coverages.return_value = {"cov1": MagicMock()}
        mock_wcs_class.return_value = mock_wcs_instance

        actions = RasdamanActions("http://test", "user", "pass")
        actions.list_coverages_action()

        assert "Listing coverages" in caplog.text


class TestDescribeCoverageAction:
    """Test cases for describe_coverage_action method."""

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_describe_coverage_success(self, mock_wcps_class, mock_wcs_class):
        """Test successful description of a coverage."""
        mock_coverage = MagicMock()
        mock_coverage.to_short_str.return_value = "Coverage: test_cov\nDimensions: 3"
        
        mock_wcs_instance = MagicMock()
        mock_wcs_instance.list_full_info.return_value = mock_coverage
        mock_wcs_class.return_value = mock_wcs_instance

        actions = RasdamanActions("http://test", "user", "pass")
        result = actions.describe_coverage_action("test_cov")

        assert result == "Coverage: test_cov\nDimensions: 3"
        mock_wcs_instance.list_full_info.assert_called_once_with("test_cov")

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_describe_coverage_logs_info(self, mock_wcps_class, mock_wcs_class, caplog):
        """Test that describing coverage logs appropriate messages."""
        import logging
        caplog.set_level(logging.INFO)
        
        mock_coverage = MagicMock()
        mock_coverage.to_short_str.return_value = "test"
        
        mock_wcs_instance = MagicMock()
        mock_wcs_instance.list_full_info.return_value = mock_coverage
        mock_wcs_class.return_value = mock_wcs_instance

        actions = RasdamanActions("http://test", "user", "pass")
        actions.describe_coverage_action("my_coverage")

        assert "Describing coverage: my_coverage" in caplog.text


class TestWCPSQueryCrashCourseAction:
    """Test cases for wcps_query_crash_course_action method."""

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_returns_crash_course_content(self, mock_wcps_class, mock_wcs_class):
        """Test that the crash course action returns the WCPS crash course."""
        actions = RasdamanActions("http://test", "user", "pass")
        result = actions.wcps_query_crash_course_action()

        assert result == WCPS_CRASH_COURSE
        assert "WCPS Crash Course" in result

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_logs_info(self, mock_wcps_class, mock_wcs_class, caplog):
        """Test that the crash course action logs appropriately."""
        import logging
        caplog.set_level(logging.INFO)
        
        actions = RasdamanActions("http://test", "user", "pass")
        actions.wcps_query_crash_course_action()

        assert "Returning WCPS crash course" in caplog.text


class TestExecuteWCPSQueryAction:
    """Test cases for execute_wcps_query_action method."""

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_execute_scalar_result(self, mock_wcps_class, mock_wcs_class):
        """Test execution returning a scalar result."""
        mock_result = MagicMock()
        mock_result.type = WCPSResultType.SCALAR
        mock_result.value = 42.5
        
        mock_wcps_instance = MagicMock()
        mock_wcps_instance.execute.return_value = mock_result
        mock_wcps_class.return_value = mock_wcps_instance

        actions = RasdamanActions("http://test", "user", "pass")
        result = actions.execute_wcps_query_action("for $c in (test) return avg($c)")

        assert result == "42.5"

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_execute_multiband_scalar_result(self, mock_wcps_class, mock_wcs_class):
        """Test execution returning a multiband scalar result."""
        mock_result = MagicMock()
        mock_result.type = WCPSResultType.MULTIBAND_SCALAR
        mock_result.value = {"red": 255, "green": 128, "blue": 0}
        
        mock_wcps_instance = MagicMock()
        mock_wcps_instance.execute.return_value = mock_result
        mock_wcps_class.return_value = mock_wcps_instance

        actions = RasdamanActions("http://test", "user", "pass")
        result = actions.execute_wcps_query_action("for $c in (test) return $c[Lat(0), Lon(0)]")

        assert "255" in result
        assert "128" in result
        assert "0" in result

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_execute_json_result_small(self, mock_wcps_class, mock_wcs_class):
        """Test execution returning a small JSON result (below threshold)."""
        json_data = {"values": [1, 2, 3], "count": 3}
        mock_result = MagicMock()
        mock_result.type = WCPSResultType.JSON
        mock_result.value = json_data
        
        mock_wcps_instance = MagicMock()
        mock_wcps_instance.execute.return_value = mock_result
        mock_wcps_class.return_value = mock_wcps_instance

        actions = RasdamanActions("http://test", "user", "pass")
        result = actions.execute_wcps_query_action("for $c in (test) return encode($c, 'application/json')")

        assert json.dumps(json_data) == result

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_execute_json_result_large(self, mock_wcps_class, mock_wcs_class):
        """Test execution returning a large JSON result (saved to file)."""
        # Create a large JSON that exceeds SAVE_THRESHOLD
        large_data = {"values": list(range(SAVE_THRESHOLD))}
        json_str = json.dumps(large_data)
        
        mock_result = MagicMock()
        mock_result.type = WCPSResultType.JSON
        mock_result.value = large_data
        
        mock_wcps_instance = MagicMock()
        mock_wcps_instance.execute.return_value = mock_result
        mock_wcps_class.return_value = mock_wcps_instance

        actions = RasdamanActions("http://test", "user", "pass")
        result = actions.execute_wcps_query_action("for $c in (test) return encode($c, 'application/json')")

        assert "JSON result saved in file" in result
        # Extract filename and verify file exists with correct content
        filename = result.split("file ")[1].strip()
        with open(filename, 'r') as f:
            content = f.read()
            assert json.loads(content) == large_data

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_execute_image_result(self, mock_wcps_class, mock_wcs_class):
        """Test execution returning an image result."""
        # Create a simple test image
        img = Image.new('RGB', (100, 50), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_data = img_bytes.getvalue()
        
        mock_result = MagicMock()
        mock_result.type = WCPSResultType.IMAGE
        mock_result.value = img_data
        
        mock_wcps_instance = MagicMock()
        mock_wcps_instance.execute.return_value = mock_result
        mock_wcps_class.return_value = mock_wcps_instance

        actions = RasdamanActions("http://test", "user", "pass")
        result = actions.execute_wcps_query_action("for $c in (test) return encode($c, 'image/png')")

        assert "Image result saved in file" in result
        assert "100 x 50 pixels" in result
        assert "3 bands" in result

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    @patch('src.rasdaman_actions.nc.Dataset')
    def test_execute_netcdf_result(self, mock_dataset_class, mock_wcps_class, mock_wcs_class):
        """Test execution returning a NetCDF result."""
        # Mock NetCDF data - create a simple class to avoid MagicMock issues
        class MockVariable:
            def __init__(self, dtype, shape, dimensions, attrs):
                self.dtype = dtype
                self.shape = shape
                self.dimensions = dimensions
                self.__dict__.update(attrs)
        
        mock_dataset = MagicMock()
        mock_dataset.dimensions = {
            "time": MagicMock(__len__=Mock(return_value=10)),
            "lat": MagicMock(__len__=Mock(return_value=100)),
            "lon": MagicMock(__len__=Mock(return_value=200))
        }
        mock_dataset.variables = {
            "time": Mock(dimensions=("time",)),
            "lat": Mock(dimensions=("lat",)),
            "lon": Mock(dimensions=("lon",)),
            "temperature": MockVariable(
                dtype="float32",
                shape=(10, 100, 200),
                dimensions=("time", "lat", "lon"),
                attrs={"units": "celsius"}
            )
        }
        mock_dataset_class.return_value.__enter__ = Mock(return_value=mock_dataset)
        mock_dataset_class.return_value.__exit__ = Mock(return_value=False)
        
        mock_result = MagicMock()
        mock_result.type = WCPSResultType.NETCDF
        mock_result.value = b"fake_netcdf_data"
        
        mock_wcps_instance = MagicMock()
        mock_wcps_instance.execute.return_value = mock_result
        mock_wcps_class.return_value = mock_wcps_instance

        actions = RasdamanActions("http://test", "user", "pass")
        result = actions.execute_wcps_query_action("for $c in (test) return encode($c, 'netcdf')")

        assert "Netcdf result saved in file" in result
        assert "dimensions:" in result.lower()
        assert "variables:" in result.lower()

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_execute_wcps_exception(self, mock_wcps_class, mock_wcs_class):
        """Test handling of WCPSClientException during execution."""
        mock_wcps_instance = MagicMock()
        mock_wcps_instance.execute.side_effect = WCPSClientException("Query syntax error")
        mock_wcps_class.return_value = mock_wcps_instance

        actions = RasdamanActions("http://test", "user", "pass")
        result = actions.execute_wcps_query_action("invalid query")

        assert "Executing WCPS query failed" in result
        assert "Query syntax error" in result

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_execute_general_exception(self, mock_wcps_class, mock_wcs_class):
        """Test handling of general exception during result processing."""
        mock_result = MagicMock()
        mock_result.type = WCPSResultType.IMAGE
        # Invalid image data that will cause Image.open to fail
        mock_result.value = b"not_valid_image_data"
        
        mock_wcps_instance = MagicMock()
        mock_wcps_instance.execute.return_value = mock_result
        mock_wcps_class.return_value = mock_wcps_instance

        actions = RasdamanActions("http://test", "user", "pass")
        result = actions.execute_wcps_query_action("for $c in (test) return encode($c, 'image/png')")

        assert "Failed handling WCPS query result" in result

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_execute_numpy_result(self, mock_wcps_class, mock_wcs_class):
        """Test execution returning a numpy array result type."""
        # Create a simple class to avoid MagicMock issues with type attribute
        class MockResult:
            def __init__(self, result_type, value):
                self.type = result_type
                self.value = value
            def capitalize(self):
                return "Numpy"
        
        mock_result = MockResult(WCPSResultType.NUMPY, b"some_binary_data")
        
        mock_wcps_instance = MagicMock()
        mock_wcps_instance.execute.return_value = mock_result
        mock_wcps_class.return_value = mock_wcps_instance

        actions = RasdamanActions("http://test", "user", "pass")
        result = actions.execute_wcps_query_action("for $c in (test) return $c")

        assert "result saved in file" in result.lower()
        assert "bytes" in result

    @patch('src.rasdaman_actions.WebCoverageService')
    @patch('src.rasdaman_actions.WCPSConnection')
    def test_execute_logs_info(self, mock_wcps_class, mock_wcs_class, caplog):
        """Test that query execution logs appropriate messages."""
        import logging
        caplog.set_level(logging.INFO)
        
        mock_result = MagicMock()
        mock_result.type = WCPSResultType.SCALAR
        mock_result.value = 42
        
        mock_wcps_instance = MagicMock()
        mock_wcps_instance.execute.return_value = mock_result
        mock_wcps_class.return_value = mock_wcps_instance

        actions = RasdamanActions("http://test", "user", "pass")
        actions.execute_wcps_query_action("for $c in (test) return 42")

        assert "Executing WCPS query" in caplog.text
