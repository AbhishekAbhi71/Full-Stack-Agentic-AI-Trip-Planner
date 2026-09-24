from .flight_tools import (
    search_oneway_flights,
    search_roundtrip_flights,
)
from .location_tools import (
    search_location,
)
from .hotel_tools import (
    search_hotel,
)
ALL_TOOLS = [
    search_oneway_flights,
    search_roundtrip_flights,
    search_location,
    search_hotel,
]