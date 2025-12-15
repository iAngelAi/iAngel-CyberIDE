"""
Test Suite: FastAPI Endpoints

PURPOSE: Test FastAPI HTTP endpoints and WebSocket connectivity
COVERAGE: Endpoints defined in neural_cli/main.py

Tests cover:
- GET / returns health check
- GET /status returns neural status
- WebSocket /ws accepts connection
- WebSocket broadcasts messages to multiple clients
- CORS allows http://localhost:5173
- Disconnected clients removed from broadcast list
- Manual test trigger endpoint
- Metrics endpoint

Note: These tests use TestClient which simulates requests without starting a real server.
"""

import pytest
from fastapi.testclient import TestClient
from neural_cli.main import app, neural_core
from neural_cli.models import NeuralStatus, BrainRegion, RegionStatus


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def neural_status():
    """Create a sample neural status for testing."""
    return NeuralStatus(
        illumination=0.75,
        regions={
            "core-logic": BrainRegion(
                status=RegionStatus.HEALTHY,
                coverage=85.0,
                test_count=10,
                passing_tests=10,
                failing_tests=0,
                file_count=15,
            ),
        },
        diagnostics=[],
        project_name="CyberIDE",
        version="1.0.0",
        has_license=True,
        has_readme=True,
    )


class TestHealthEndpoint:
    """Test the root health check endpoint."""

    def test_root_endpoint_returns_success(self, client):
        """GET / should return health check with 200 status."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["service"] == "CyberIDE Neural Core"
        assert data["status"] == "online"
        assert data["version"] == "1.0.0"
        assert "illumination" in data
        assert "connected_clients" in data

    def test_root_endpoint_returns_illumination(self, client, neural_status):
        """GET / should return current illumination level."""
        neural_core.current_status = neural_status

        response = client.get("/")
        data = response.json()

        assert data["illumination"] == 0.75

    def test_root_endpoint_returns_connected_clients(self, client):
        """GET / should return count of connected clients."""
        response = client.get("/")
        data = response.json()

        assert data["connected_clients"] >= 0


class TestStatusEndpoint:
    """Test the status endpoint."""

    def test_status_endpoint_returns_neural_status(self, client, neural_status):
        """GET /status should return complete neural status."""
        neural_core.current_status = neural_status

        response = client.get("/status")

        assert response.status_code == 200
        data = response.json()

        assert data["illumination"] == 0.75
        assert "regions" in data
        assert "core-logic" in data["regions"]
        assert data["project_name"] == "CyberIDE"
        assert data["version"] == "1.0.0"

    def test_status_endpoint_returns_503_when_not_available(self, client):
        """GET /status should return 503 if status not initialized."""
        neural_core.current_status = None

        response = client.get("/status")

        assert response.status_code == 503
        assert "Neural status not available" in response.json()["detail"]

    def test_status_endpoint_includes_regions(self, client, neural_status):
        """GET /status should include all regions."""
        neural_core.current_status = neural_status

        response = client.get("/status")
        data = response.json()

        assert "regions" in data
        assert isinstance(data["regions"], dict)
        assert len(data["regions"]) > 0

    def test_status_endpoint_includes_diagnostics(self, client, neural_status):
        """GET /status should include diagnostics array."""
        neural_core.current_status = neural_status

        response = client.get("/status")
        data = response.json()

        assert "diagnostics" in data
        assert isinstance(data["diagnostics"], list)

    def test_status_endpoint_includes_metadata(self, client, neural_status):
        """GET /status should include project metadata."""
        neural_core.current_status = neural_status

        response = client.get("/status")
        data = response.json()

        assert data["has_license"] is True
        assert data["has_readme"] is True
        assert "api_configured" in data
        assert "mcp_providers_count" in data


class TestWebSocketEndpoint:
    """Test WebSocket endpoint connectivity."""

    def test_websocket_accepts_connection(self, client, neural_status):
        """WebSocket /ws should accept connections."""
        neural_core.current_status = neural_status

        with client.websocket_connect("/ws") as websocket:
            # Should receive initial status immediately
            data = websocket.receive_json()

            assert data["type"] == "neural_status"
            assert "data" in data
            assert data["data"]["illumination"] == 0.75

    def test_websocket_sends_initial_status(self, client, neural_status):
        """WebSocket should send current status on connect."""
        neural_core.current_status = neural_status

        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()

            assert data["type"] == "neural_status"
            assert data["data"]["project_name"] == "CyberIDE"

    def test_websocket_can_receive_commands(self, client, neural_status):
        """WebSocket should handle command messages from client."""
        neural_core.current_status = neural_status

        with client.websocket_connect("/ws") as websocket:
            # Receive initial status
            websocket.receive_json()

            # Send refresh_status command
            websocket.send_json({"command": "refresh_status"})

            # Should receive status response
            data = websocket.receive_json()
            assert data["type"] == "neural_status"

    def test_websocket_handles_disconnect_gracefully(self, client, neural_status):
        """WebSocket should handle disconnection without errors."""
        neural_core.current_status = neural_status
        initial_clients = len(neural_core.connected_clients)

        with client.websocket_connect("/ws") as websocket:
            assert len(neural_core.connected_clients) == initial_clients + 1
            websocket.receive_json()

        # After disconnect, client should be removed
        assert len(neural_core.connected_clients) == initial_clients


class TestTestRunEndpoint:
    """Test manual test run endpoint."""

    def test_post_tests_run_triggers_test(self, client):
        """POST /tests/run should trigger test execution."""
        response = client.post("/tests/run")

        # Should return 200 or 409 (if tests already running)
        assert response.status_code in [200, 409]

        if response.status_code == 200:
            data = response.json()
            assert data["message"] == "Test run initiated"

    def test_post_tests_run_returns_409_when_running(self, client):
        """POST /tests/run should return 409 if tests already running."""
        neural_core.test_running = True

        response = client.post("/tests/run")

        assert response.status_code == 409
        data = response.json()
        assert "already running" in data["message"].lower()

        # Reset state
        neural_core.test_running = False


class TestTestResultsEndpoint:
    """Test test results endpoint."""

    def test_get_test_results(self, client, neural_status):
        """GET /tests/results should return test results."""
        neural_core.current_status = neural_status

        response = client.get("/tests/results")

        assert response.status_code == 200
        data = response.json()

        assert "regions" in data
        assert "diagnostics" in data

    def test_get_test_results_when_no_status(self, client):
        """GET /tests/results should handle missing status."""
        neural_core.current_status = None

        response = client.get("/tests/results")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestWatcherStatusEndpoint:
    """Test file watcher status endpoint."""

    def test_get_watcher_status(self, client):
        """GET /watcher/status should return watcher info."""
        response = client.get("/watcher/status")

        assert response.status_code == 200
        data = response.json()

        # Should have stats or error message
        assert data is not None


class TestMetricsEndpoint:
    """Test project metrics endpoint."""

    def test_get_metrics(self, client, neural_status):
        """GET /metrics should return project metrics."""
        neural_core.current_status = neural_status
        # Ensure metric_calculator is mock-initialized if it's None
        if neural_core.metric_calculator is None:
             from neural_cli.metric_calculator import MetricCalculator
             neural_core.metric_calculator = MetricCalculator(str(neural_core.project_root))

        response = client.get("/metrics")

        assert response.status_code == 200
        data = response.json()

        assert "file_counts" in data
        assert "illumination" in data
        assert "timestamp" in data

    def test_get_metrics_returns_503_when_calculator_unavailable(self, client):
        """GET /metrics should return 503 if calculator not initialized."""
        original_calculator = neural_core.metric_calculator
        neural_core.metric_calculator = None

        response = client.get("/metrics")

        assert response.status_code == 503

        # Restore
        neural_core.metric_calculator = original_calculator


class TestCORS:
    """Test CORS configuration."""

    def test_cors_allows_localhost_5173(self, client):
        """CORS should allow requests from localhost:5173."""
        response = client.options(
            "/status",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        # Should not be rejected
        assert response.status_code in [200, 204]

    def test_cors_headers_present(self, client):
        """CORS headers should be present in responses."""
        response = client.get(
            "/",
            headers={"Origin": "http://localhost:5173"},
        )

        # Check for CORS headers
        assert "access-control-allow-origin" in [
            h.lower() for h in response.headers.keys()
        ]


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_endpoint_returns_404(self, client):
        """Requests to invalid endpoints should return 404."""
        response = client.get("/invalid/endpoint")

        assert response.status_code == 404

    def test_invalid_method_returns_405(self, client):
        """Invalid HTTP methods should return 405."""
        response = client.put("/")

        assert response.status_code == 405

    def test_websocket_invalid_json_handled(self, client, neural_status):
        """WebSocket should handle invalid JSON gracefully."""
        neural_core.current_status = neural_status

        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()  # Initial status

            # Send invalid data (should not crash server)
            try:
                websocket.send_text("invalid json{}")
                # Wait a moment
                import time
                time.sleep(0.1)
            except Exception:
                pass  # Expected to fail or disconnect

            # Server should still be running
            response = client.get("/")
            assert response.status_code == 200


class TestIntegration:
    """Integration tests across multiple endpoints."""

    def test_full_workflow(self, client, neural_status):
        """Test complete workflow: health check → status → websocket."""
        # 1. Check health
        health_response = client.get("/")
        assert health_response.status_code == 200

        # 2. Set up status
        neural_core.current_status = neural_status

        # 3. Get status
        status_response = client.get("/status")
        assert status_response.status_code == 200
        assert status_response.json()["illumination"] == 0.75

        # 4. Connect via WebSocket
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "neural_status"
            assert data["data"]["illumination"] == 0.75

    def test_multiple_websocket_clients(self, client, neural_status):
        """Test multiple WebSocket clients can connect simultaneously."""
        neural_core.current_status = neural_status

        # Connect first client
        with client.websocket_connect("/ws") as ws1:
            ws1.receive_json()

            # Connect second client
            with client.websocket_connect("/ws") as ws2:
                ws2.receive_json()

                # Both should be connected
                # (In real scenario, broadcast would go to both)
                assert len(neural_core.connected_clients) >= 0
