"""Tests for the Timer class."""

import logging
import time
from unittest.mock import patch

import pytest

from src.timer import Timer


class TestTimer:
    """Test cases for the Timer class."""

    def test_init(self):
        """Test Timer initialization."""
        timer = Timer()
        assert timer.start_time is None
        assert timer.end_time is None

    def test_enter(self):
        """Test context manager entry sets start_time."""
        timer = Timer()
        with timer as t:
            assert t.start_time is not None
            assert t.end_time is None
            assert t is timer

    def test_exit(self):
        """Test context manager exit sets end_time."""
        timer = Timer()
        with timer:
            pass
        assert timer.end_time is not None

    def test_elapsed_before_enter(self):
        """Test elapsed property returns None before entering context."""
        timer = Timer()
        assert timer.elapsed is None

    def test_elapsed_inside_context(self):
        """Test elapsed property works inside context manager."""
        timer = Timer()
        with timer:
            time.sleep(0.01)
            elapsed = timer.elapsed
            assert elapsed is not None
            assert elapsed > 0

    def test_elapsed_after_exit(self):
        """Test elapsed property after context manager exit."""
        timer = Timer()
        with timer:
            time.sleep(0.01)
        elapsed = timer.elapsed
        assert elapsed is not None
        assert elapsed > 0

    def test_log_before_enter(self):
        """Test log method does nothing before entering context."""
        timer = Timer()
        # Should not raise any exception
        timer.log("test message")

    def test_log_with_message(self, caplog):
        """Test log method with a message."""
        caplog.set_level(logging.INFO)
        timer = Timer()
        with timer:
            time.sleep(0.01)
            timer.log("Test operation")
        
        assert "Test operation in" in caplog.text
        assert "s" in caplog.text

    def test_log_without_message(self, caplog):
        """Test log method without a message."""
        caplog.set_level(logging.INFO)
        timer = Timer()
        with timer:
            time.sleep(0.01)
            timer.log()
        
        assert " in " in caplog.text
        assert "s" in caplog.text

    @patch('time.time')
    def test_elapsed_calculation(self, mock_time):
        """Test elapsed time calculation with mocked time."""
        mock_time.side_effect = [100.0, 105.5]  # start, end
        
        timer = Timer()
        with timer:
            pass
        
        assert timer.elapsed == 5.5

    @patch('time.time')
    def test_elapsed_inside_context_with_mocked_time(self, mock_time):
        """Test elapsed property inside context with mocked time."""
        # Use a list to track calls and return different values
        # Need 4 values: start, first check, second check, exit
        call_count = [0]
        times = [100.0, 102.0, 103.0, 104.0]  # start, first check, second check, exit
        def mock_time_func():
            result = times[call_count[0]]
            call_count[0] += 1
            return result
        
        mock_time.side_effect = mock_time_func
        
        timer = Timer()
        with timer:
            elapsed1 = timer.elapsed  # Should be 2.0
            elapsed2 = timer.elapsed  # Should be 3.0
        
        assert elapsed1 == 2.0
        assert elapsed2 == 3.0
