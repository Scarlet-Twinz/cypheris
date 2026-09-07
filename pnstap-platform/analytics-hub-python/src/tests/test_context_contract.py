import os
import sys
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "test-only-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC))

from routers.context import router  # noqa: E402
from routers.sensors import router as sensors_router  # noqa: E402


def test_context_routes_exist():
    paths = {route.path for route in router.routes}
    assert "/api/context/summary" in paths
    assert "/api/context/assets" in paths
    assert "/api/context/identities" in paths
    assert "/api/context/investigations" in paths
    assert "/api/context/timeline" in paths
    assert "/api/context/drift" in paths


def test_sensor_ingestion_route_exists():
    paths = {route.path for route in sensors_router.routes}
    assert "/api/sensors/telemetry" in paths
