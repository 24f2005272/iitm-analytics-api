
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from collections import defaultdict
from typing import List
from secrets import compare_digest
import os

app = FastAPI()

API_KEY = os.environ["API_KEY"]
EMAIL = "24f2005272@ds.study.iitm.ac.in"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: List[Event]


@app.post("/analytics")
def analytics(
    data: AnalyticsRequest,
    x_api_key: str | None = Header(default=None),
):
    if x_api_key is None or not compare_digest(
        x_api_key, API_KEY
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    totals = defaultdict(float)
    revenue = 0.0

    for event in data.events:
        if event.amount > 0:
            revenue += event.amount
            totals[event.user] += event.amount

    top_user = (
        max(totals, key=totals.get)
        if totals else None
    )

    return {
        "email": EMAIL,
        "total_events": len(data.events),
        "unique_users": len(
            {event.user for event in data.events}
        ),
        "revenue": round(revenue, 6),
        "top_user": top_user,
    }


@app.get("/")
def health():
    return {"status": "ok"}
