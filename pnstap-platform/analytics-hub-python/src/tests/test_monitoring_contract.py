import os
import sys
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "test-only-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC))

from routers.monitoring import router  # noqa: E402


def test_monitoring_routes_are_company_scoped():
    paths = {route.path for route in router.routes}
    assert "/api/monitoring/alerts" in paths
    assert "/api/monitoring/network" in paths
    assert "/api/monitoring/assets" in paths
    assert "/api/monitoring/notifications" in paths
