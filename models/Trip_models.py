from typing import Optional, Literal
from pydantic import BaseModel, Field

class TripRequest(BaseModel):
    origin: Optional[str] = Field(default=None, description="Starting city")
    destination: str = Field(description="Destination city")
    departure_date: Optional[str] = Field(default=None, description="Departure date in YYYY-MM-DD if available")
    trip_days: int = Field(default=1, ge=1, description="Number of days of stay/trip")
    total_budget: Optional[float] = Field(default=None, description="Total trip budget in INR if explicitly provided")
    travel_style: Literal["budget", "balanced", "comfort"] = Field(default="balanced")
    travelers: int = Field(default=1, ge=1, description="Number of travelers (default 1)")
    trip_type: Literal["oneway", "roundtrip"] = Field(default="oneway", description="One-way or round-trip")
    return_date: Optional[str] = Field(default=None, description="Return date in YYYY-MM-DD if available")