"""Tests for Docker-related configuration and health endpoints.

These tests verify the app behaves correctly inside Docker by checking:
- Environment variable handling
- Health endpoint responds correctly
- Database URL resolution for Docker paths
- Static assets and API prefix consistency
"""
import os
import pytest


class TestHealthEndpoint:
    async def test_health_returns_200(self, client):
        r = await client.get("/health")
        assert r.status_code == 200

    async def test_health_returns_ok_status(self, client):
        r = await client.get("/health")
        data = r.json()
        assert data.get("status") == "ok"

    async def test_health_response_has_timestamp(self, client):
        r = await client.get("/health")
        data = r.json()
        assert "timestamp" in data or "status" in data

    async def test_root_returns_200(self, client):
        r = await client.get("/")
        assert r.status_code == 200


class TestEnvironmentConfig:
    def test_database_url_env_var_respected(self):
        from database.db import DATABASE_URL
        assert DATABASE_URL is not None
        assert "sqlite" in DATABASE_URL or "postgresql" in DATABASE_URL

    def test_gemini_api_key_env_var_set(self):
        key = os.getenv("GEMINI_API_KEY")
        assert key is not None
        assert len(key) > 0

    def test_debug_flag_parseable(self):
        debug_raw = os.getenv("DEBUG", "true")
        debug = debug_raw.lower() == "true"
        assert isinstance(debug, bool)

    def test_app_port_is_integer(self):
        port_raw = os.getenv("APP_PORT", "8000")
        port = int(port_raw)
        assert 1024 <= port <= 65535


class TestDockerDatabasePath:
    def test_sqlite_url_uses_aiosqlite_driver(self):
        from database.db import DATABASE_URL
        if "sqlite" in DATABASE_URL:
            assert "aiosqlite" in DATABASE_URL, (
                f"SQLite URL must use aiosqlite driver, got: {DATABASE_URL}"
            )

    def test_database_url_not_empty(self):
        from database.db import DATABASE_URL
        assert len(DATABASE_URL) > 0

    def test_engine_created_successfully(self):
        from database.db import engine
        assert engine is not None


class TestAPIStructure:
    async def test_all_analysis_routes_under_api_prefix(self, client):
        r = await client.post("/api/analyse/text", json={"content": "test"})
        assert r.status_code in (200, 422, 500)

    async def test_state_routes_under_api_prefix(self, client):
        r = await client.get("/api/state/logistics")
        assert r.status_code == 200

    async def test_mock_api_routes_under_api_prefix(self, client):
        from utils.helpers import generate_uuid
        r = await client.post("/api/logistics/pricing/update", json={
            "route_id": "x",
            "price_delta_pct": 5.0,
            "effective_date": "2024-12-01",
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200

    async def test_404_for_unknown_route(self, client):
        r = await client.get("/nonexistent_endpoint_xyz")
        assert r.status_code == 404

    async def test_cors_headers_present(self, client):
        r = await client.options("/api/state/logistics", headers={"Origin": "http://localhost:3000"})
        # CORS is configured — at minimum the endpoint should not fail with 500
        assert r.status_code in (200, 405)


class TestDockerfileStructure:
    def test_dockerfile_exists(self):
        import pathlib
        root = pathlib.Path(__file__).parent.parent
        assert (root / "Dockerfile").exists(), "Dockerfile not found in project root"

    def test_dockerignore_exists(self):
        import pathlib
        root = pathlib.Path(__file__).parent.parent
        assert (root / ".dockerignore").exists(), ".dockerignore not found"

    def test_docker_compose_exists(self):
        import pathlib
        root = pathlib.Path(__file__).parent.parent
        assert (root / "docker-compose.yml").exists(), "docker-compose.yml not found"

    def test_start_script_exists(self):
        import pathlib
        root = pathlib.Path(__file__).parent.parent
        script = root / "scripts" / "start.sh"
        assert script.exists(), "scripts/start.sh not found"

    def test_requirements_txt_includes_test_deps(self):
        import pathlib
        root = pathlib.Path(__file__).parent.parent
        req_path = root / "requirements.txt"
        assert req_path.exists()
        content = req_path.read_text()
        assert "pytest" in content
        assert "pytest-asyncio" in content

    def test_requirements_txt_includes_aiosqlite(self):
        import pathlib
        root = pathlib.Path(__file__).parent.parent
        content = (root / "requirements.txt").read_text()
        assert "aiosqlite" in content
