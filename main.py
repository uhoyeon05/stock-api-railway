from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# CORS 허용 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 환경변수에서 API 키 읽기
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "여기에_API_키_입력")
BASE_URL = "https://www.alphavantage.co/query"

# ✅ /api 제거한 새로운 라우터 경로
@app.get("/price")
def get_stock_price(ticker: str):
    url = f"{BASE_URL}?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={ticker}&apikey={API_KEY}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        json_data = res.json()

        if "Note" in json_data or "Error Message" in json_data:
            return {"error": "API limit or invalid request", "details": json_data}

        data = json_data.get("Monthly Adjusted Time Series", {})
        if not data:
            return {"error": "No time series data returned", "raw_response": json_data}

        result = [
            {"date": date, "close": float(val.get("5. adjusted close", 0))}
            for date, val in sorted(data.items())[-120:]
        ]
        return {"ticker": ticker, "prices": result}
    except Exception as e:
        return {"error": "Failed to fetch or parse price data", "details": str(e)}


@app.get("/income")
def get_income_statement(ticker: str):
    url = f"{BASE_URL}?function=INCOME_STATEMENT&symbol={ticker}&apikey={API_KEY}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        json_data = res.json()

        if "Note" in json_data or "Error Message" in json_data:
            return {"error": "API limit or invalid request", "details": json_data}

        data = json_data.get("annualReports", [])
        return {"ticker": ticker, "data": data}
    except Exception as e:
        return {"error": "Failed to fetch or parse income data", "details": str(e)}
