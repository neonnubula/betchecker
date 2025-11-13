import os
import pytest
from fastapi.testclient import TestClient

# Ensure the DB path is set for the app to locate the database in runtime
os.environ.setdefault("DB_PATH", "/Users/d/BetChecker-PlayerDatabase/afl_stats.db")

# Import the app after setting env
from app.main import app  # noqa: E402

client = TestClient(app)


@pytest.mark.parametrize(
    "query",
    [
        {
            "player_name": "Scott Pendlebury",
            "stat": "disposals",
            "threshold": 25,
        }
    ],
)
def test_over_under_returns_two_fields_only(query):
    response = client.get("/search/over-under", params=query)
    assert response.status_code in (200, 404, 400)
    # For Step 1, we're asserting the contract shape on success
    if response.status_code == 200:
        data = response.json()
        assert set(data.keys()) == {"over", "under"}
        assert isinstance(data["over"], int)
        assert isinstance(data["under"], int)


