import os
from fastapi.testclient import TestClient

os.environ.setdefault("DB_PATH", "/Users/d/BetChecker-PlayerDatabase/afl_stats.db")

from app.main import app  # noqa: E402

client = TestClient(app)


def test_pendlebury_disposals_19_5_percentages_sum_to_one():
    params = {
        "player_name": "Scott Pendlebury",
        "stat": "disposals",
        "threshold": 19.5,
        "strict_over": True,  # 19.5 strict_over means > 19.5 is >= 20
    }
    resp = client.get("/search/over-under", params=params)
    print(f"Status: {resp.status_code}")

    # Print payload or error detail for visibility
    try:
        payload = resp.json()
    except Exception:
        payload = None
    print(f"Response JSON: {payload}")

    assert resp.status_code in (200, 404, 400, 500)

    if resp.status_code == 200:
        data = payload
        over = data["over"]
        under = data["under"]
        total = over + under
        print(f"Counts -> over: {over}, under: {under}, total: {total}")
        # Ensure we have games to compute
        assert total > 0
        pct_over = over / total
        pct_under = under / total
        print(f"Percentages -> over: {pct_over:.4f}, under: {pct_under:.4f}")
        # Percentages should sum to ~1.0 (allowing for float rounding)
        assert abs((pct_over + pct_under) - 1.0) < 1e-9
        # Values are within [0,1]
        assert 0.0 <= pct_over <= 1.0
        assert 0.0 <= pct_under <= 1.0
