# Use fastapi to create Chart object below

from fastapi import FastAPI
from pydantic import BaseModel
from core import T5

app = FastAPI()


class FastChart(BaseModel):
    income_summary_account: str
    retained_earnings_account: str
    accounts: dict[str, tuple[T5, list[str]]]


class ChartRequest(BaseModel):
    pass


@app.post("/chart/new")
def create_chart(
    income_summary_account: str = "isa", retained_earnings_account: str = "re"
) -> FastChart:
    return FastChart(
        income_summary_account=income_summary_account,
        retained_earnings_account=retained_earnings_account,
        accounts={retained_earnings_account: (T5.Capital, [])},
    )

from fastapi.testclient import TestClient

client = TestClient(app)

def test_chart_new():
    payload = {
        "income_summary_account": "current_profit",
        "retained_earnings_account": "retained_earnings",
    }
    response = client.post("/chart/new", params=payload)
    assert response.status_code == 200
    assert response.json() == {
        "income_summary_account": "current_profit",
        "retained_earnings_account": "retained_earnings",
        "accounts": {"retained_earnings": ["capital", []]},
    }


test_chart_new()
print(create_chart())