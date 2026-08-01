# Trip Planner Agent

AI-powered trip planner using LangGraph that searches flights and hotels, allocates budget intelligently, and generates a micro-itinerary with top visiting spots, travel recommendations, and a detailed budget summary.

## Features

- Flight search under a user-defined budget (RapidAPI Skyscanner)
- Hotel search with per-night budget (RapidAPI Booking.com)
- Intelligent budget allocation:
  - Flight, hotel, food, local transport, other
- Auto-generated micro-itinerary and visiting spots
- Final budget summary in a clean markdown report

## Tech Stack

- Python
- LangGraph, LangChain
- Google GenAI (Gemini)
- RapidAPI (Skyscanner, Booking.com)
- Pydantic, python-dotenv, requests, regex

## Installation

```bash
git clone https://github.com/AbhishekAbhi71/trip-planner-agent.git
cd trip-planner-agent

python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root (see `.env.example`):

```text
GEMINI_API_KEY=your_gemini_api_key
RAPIDAPI_KEY=your_rapidapi_key
```

Do not commit `.env` to Git; it is already in `.gitignore`.

## Usage

Run the planner:

```bash
python -m app.main
```

Inside `app/main.py`, you can change the `user_query`, for example:

```python
user_query = "plan a trip from delhi to mumbai for 3 days under 20000 on 03 August 2026"
```

The output includes:

- Budget allocation
- Flight results
- Hotel results
- Recommendations (cheapest flight, cheapest hotel, best-value hotel)
- Micro-itinerary with visiting spots
- Budget summary

## Project Structure

```text
trip-planner-agent/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── budget.py
│   ├── tools.py
│   ├── nodes.py
│   └── graph.py
├── tests/
│   └── test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── LICENSE
```

## Example Output (Summary)

The final response from the agent is a markdown report with sections like:

1. Budget Allocation  
2. Flight Results  
3. Hotel Results  
4. Recommendations  
5. Creative Micro-Itinerary  
6. Budget Summary  

## License

MIT License — see [LICENSE](LICENSE) for details.
