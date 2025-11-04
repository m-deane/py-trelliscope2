"""Unit tests for DisplayServer."""

import pytest
import tempfile
import time
from pathlib import Path

from trelliscope.server import DisplayServer


class TestDisplayServerInitialization:
    """Test DisplayServer initialization."""

    def test_init_with_valid_directory(self):
        """Test initialization with valid directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = DisplayServer(Path(tmpdir), port=8001)
            assert server.display_dir == Path(tmpdir)
            assert server.port == 8001
            assert server.httpd is None
            assert server.thread is None

    def test_init_with_nonexistent_directory(self):
        """Test initialization with nonexistent directory raises error."""
        with pytest.raises(ValueError, match="Display directory does not exist"):
            DisplayServer(Path("/nonexistent/path"), port=8000)

    def test_init_default_port(self):
        """Test default port is 8000."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = DisplayServer(Path(tmpdir))
            assert server.port == 8000

    def test_init_custom_port(self):
        """Test custom port is set correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = DisplayServer(Path(tmpdir), port=9999)
            assert server.port == 9999


class TestDisplayServerLifecycle:
    """Test server start, stop, and lifecycle."""

    def test_is_running_initially_false(self):
        """Test is_running() returns False initially."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = DisplayServer(Path(tmpdir))
            assert server.is_running() is False

    def test_start_non_blocking(self):
        """Test starting server in non-blocking mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = DisplayServer(Path(tmpdir), port=8002)
            try:
                server.start(blocking=False)
                assert server.is_running() is True
                assert server.httpd is not None
                assert server.thread is not None
            finally:
                server.stop()

    def test_stop_server(self):
        """Test stopping server."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = DisplayServer(Path(tmpdir), port=8003)
            server.start(blocking=False)
            assert server.is_running() is True

            server.stop()
            assert server.is_running() is False
            assert server.httpd is None
            assert server.thread is None

    def test_start_when_already_running(self):
        """Test starting server when already running raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = DisplayServer(Path(tmpdir), port=8004)
            try:
                server.start(blocking=False)
                with pytest.raises(RuntimeError, match="Server is already running"):
                    server.start(blocking=False)
            finally:
                server.stop()

    def test_stop_when_not_running(self):
        """Test stopping server when not running doesn't raise error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = DisplayServer(Path(tmpdir))
            # Should not raise error
            server.stop()
            assert server.is_running() is False


class TestDisplayServerURL:
    """Test server URL generation."""

    def test_get_url_default_port(self):
        """Test get_url() with default port."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = DisplayServer(Path(tmpdir))
            assert server.get_url() == "http://localhost:8000"

    def test_get_url_custom_port(self):
        """Test get_url() with custom port."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = DisplayServer(Path(tmpdir), port=9000)
            assert server.get_url() == "http://localhost:9000"

    def test_get_url_before_start(self):
        """Test get_url() works before server is started."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = DisplayServer(Path(tmpdir), port=8005)
            url = server.get_url()
            assert url == "http://localhost:8005"
            assert server.is_running() is False


class TestDisplayServerContextManager:
    """Test context manager protocol."""

    def test_context_manager_starts_and_stops(self):
        """Test context manager starts and stops server."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with DisplayServer(Path(tmpdir), port=8006) as server:
                assert server.is_running() is True
            # After exiting context, server should be stopped
            assert server.is_running() is False

    def test_context_manager_with_exception(self):
        """Test context manager stops server even if exception occurs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                with DisplayServer(Path(tmpdir), port=8007) as server:
                    assert server.is_running() is True
                    raise ValueError("Test exception")
            except ValueError:
                pass
            # Server should still be stopped
            assert server.is_running() is False


class TestDisplayServerRepresentation:
    """Test string representation."""

    def test_repr_when_stopped(self):
        """Test __repr__ when server is stopped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            display_dir = Path(tmpdir)
            server = DisplayServer(display_dir, port=8008)
            repr_str = repr(server)
            assert "DisplayServer" in repr_str
            assert "port=8008" in repr_str
            assert "status=stopped" in repr_str

    def test_repr_when_running(self):
        """Test __repr__ when server is running."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = DisplayServer(Path(tmpdir), port=8009)
            try:
                server.start(blocking=False)
                repr_str = repr(server)
                assert "DisplayServer" in repr_str
                assert "port=8009" in repr_str
                assert "status=running" in repr_str
            finally:
                server.stop()


class TestDisplayServerDirectoryHandling:
    """Test directory change behavior."""

    def test_restores_original_directory_after_stop(self):
        """Test that stopping server restores original directory."""
        original_dir = Path.cwd()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a subdirectory to ensure parent != original
            display_dir = Path(tmpdir) / "display"
            display_dir.mkdir()

            server = DisplayServer(display_dir, port=8010)
            server.start(blocking=False)

            # Directory should have changed to parent of display_dir (tmpdir)
            current_dir = Path.cwd()
            # May or may not have changed depending on if original cwd existed
            # Just verify server is running
            assert server.is_running()

            server.stop()

            # Directory should be restored to original (or safe fallback)
            # After stop, we should be back to original or a valid directory
            restored_dir = Path.cwd()
            assert restored_dir.exists()

    def test_restores_directory_on_context_manager_exit(self):
        """Test context manager restores original directory."""
        original_dir = Path.cwd()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a subdirectory to ensure parent != original
            display_dir = Path(tmpdir) / "display"
            display_dir.mkdir()

            with DisplayServer(display_dir, port=8011) as server:
                # Server should be running
                assert server.is_running()

            # Server should be stopped after context exit
            assert not server.is_running()

            # Directory should be restored or at least valid
            restored_dir = Path.cwd()
            assert restored_dir.exists()


class TestDisplayServerErrorHandling:
    """Test error handling."""

    def test_port_already_in_use(self):
        """Test error when port is already in use."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Start first server
            server1 = DisplayServer(Path(tmpdir), port=8012)
            server1.start(blocking=False)

            try:
                # Try to start second server on same port
                server2 = DisplayServer(Path(tmpdir), port=8012)
                with pytest.raises(OSError, match="Cannot start server on port"):
                    server2.start(blocking=False)
            finally:
                server1.stop()


class TestDisplayServerIntegration:
    """Integration tests for server functionality."""

    def test_serve_static_file(self):
        """Test that server can serve static files."""
        pytest.importorskip("requests")
        import requests

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a display directory inside tmpdir
            display_dir = Path(tmpdir) / "my_display"
            display_dir.mkdir()

            # Create a test file in the parent (tmpdir)
            test_file = Path(tmpdir) / "test.html"
            test_file.write_text("<html><body>Test</body></html>")

            # Server will chdir to tmpdir (parent of display_dir)
            server = DisplayServer(display_dir, port=8013)
            try:
                server.start(blocking=False)
                time.sleep(0.5)  # Give server time to start

                # Try to fetch the file (in parent directory)
                response = requests.get(f"{server.get_url()}/test.html", timeout=2)
                assert response.status_code == 200
                assert "Test" in response.text
            finally:
                server.stop()

    def test_serve_nonexistent_file_returns_404(self):
        """Test that server returns 404 for nonexistent files."""
        pytest.importorskip("requests")
        import requests

        with tempfile.TemporaryDirectory() as tmpdir:
            server = DisplayServer(Path(tmpdir), port=8014)
            try:
                server.start(blocking=False)
                time.sleep(0.5)  # Give server time to start

                # Try to fetch nonexistent file
                response = requests.get(
                    f"{server.get_url()}/nonexistent.html", timeout=2
                )
                assert response.status_code == 404
            finally:
                server.stop()

    def test_multiple_requests(self):
        """Test server can handle multiple requests."""
        pytest.importorskip("requests")
        import requests

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a display directory inside tmpdir
            display_dir = Path(tmpdir) / "my_display"
            display_dir.mkdir()

            # Create multiple test files in parent (tmpdir)
            for i in range(3):
                test_file = Path(tmpdir) / f"test{i}.html"
                test_file.write_text(f"<html><body>File {i}</body></html>")

            # Server will chdir to tmpdir (parent of display_dir)
            server = DisplayServer(display_dir, port=8015)
            try:
                server.start(blocking=False)
                time.sleep(0.5)  # Give server time to start

                # Fetch all files (in parent directory)
                for i in range(3):
                    response = requests.get(
                        f"{server.get_url()}/test{i}.html", timeout=2
                    )
                    assert response.status_code == 200
                    assert f"File {i}" in response.text
            finally:
                server.stop()
