# ✈️ Full-Stack Agentic AI Trip Planner

A **Full-Stack Agentic AI Trip Planner** that intelligently creates personalized travel plans based on destination, travel dates, budget, number of travelers, and travel preferences.

The application combines a **HTML/CSS/JavaScript frontend**, **FastAPI backend**, **LangChain + LangGraph agent workflow**, **Google Gemini LLM**, and **real-time travel APIs** to generate complete trip plans including transportation, hotels, activities, budget allocation, and day-wise itineraries.

---

## 🚀 Features

* 🤖 **Agentic AI-powered trip planning**
* 🌐 **Full-stack web application**
* ✈️ **Flight/transportation search**
* 🏨 **Hotel search and recommendations**
* 💰 **Budget allocation and optimization**
* ⭐ **Cheapest and best-value options**
* 📍 **Tourist attraction recommendations**
* 🗓️ **Day-wise micro itinerary**
* 👥 **Multiple traveler support**
* 🔄 **One-way and round-trip planning**
* 🎯 **Budget, Balanced, and Comfort travel styles**
* 📊 **Complete trip cost breakdown**
* 🧠 **LLM-powered planning and decision making**
* 🔧 **LangGraph-based agent workflow**
* ⚡ **FastAPI REST backend**
* 💻 **Interactive HTML/CSS/JavaScript frontend**

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │       USER          │
                         │  Trip Requirements  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    FRONTEND         │
                         │ HTML + CSS + JS     │
                         └──────────┬──────────┘
                                    │
                              HTTP / REST API
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FASTAPI        │
                         │      BACKEND        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    LANGGRAPH        │
                         │   AGENT WORKFLOW    │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
              Transportation      Hotels        Activities
                 Tools             Tools           Tools
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   GEMINI LLM        │
                         │ Reasoning & Planning│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Budget Optimization  │
                         │ + Itinerary Builder  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   FINAL TRIP PLAN   │
                         │ Transport + Hotel   │
                         │ Activities + Budget │
                         │ Day-wise Itinerary  │
                         └─────────────────────┘
```

---

# 🧠 How It Works

The user enters their travel requirements through the web interface.

For example:

```text
Origin: Delhi
Destination: Mumbai
Duration: 4 Days
Travelers: 2
Budget: ₹50,000
Travel Style: Balanced
Trip Type: Round Trip
```

The request is sent from the frontend to the **FastAPI backend**.

The backend passes the request to the **LangGraph agent**, which coordinates the trip-planning workflow.

The agent can:

1. Understand the user's travel requirements.
2. Search transportation options.
3. Search suitable hotels.
4. Find relevant tourist attractions.
5. Analyze available options.
6. Allocate the user's budget.
7. Compare different options.
8. Identify suitable cheapest and best-value choices.
9. Generate a day-wise itinerary.
10. Return the final structured trip plan to the frontend.

---

# 🛠️ Tech Stack

## Frontend

* **HTML5**
* **CSS3**
* **JavaScript**
* REST API integration
* Interactive trip-planning interface

## Backend

* **Python**
* **FastAPI**
* **Pydantic**
* REST APIs
* Environment-based configuration

## AI / Agentic AI

* **Google Gemini**
* **LangChain**
* **LangGraph**
* LLM-based reasoning
* Tool calling
* Agentic workflow orchestration

## External Services

* **RapidAPI**
* Travel APIs
* Flight/transportation data
* Hotel data

---

# 📁 Project Structure

```text
trip-planner-agent/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── backend/
│   ├── main.py
│   ├── agents/
│   ├── tools/
│   ├── models/
│   └── services/
│
├── requirements.txt
├── .env.example
├── README.md
└── ...
```

> The structure above represents the logical separation of the frontend and backend. Update the names if your actual repository structure differs.

---

# ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/AbhishekAbhi71/trip-planner-agent.git
```

### 2. Navigate to the project

```bash
cd trip-planner-agent
```

### 3. Create a virtual environment

```bash
python -m venv myenv
```

### 4. Activate the environment

Windows:

```bash
myenv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file and configure the required API keys.

```env
GEMINI_API_KEY=your_gemini_api_key
RAPIDAPI_KEY=your_rapidapi_key
```

Add any additional API credentials required by the travel APIs used by the application.

**Never commit your `.env` file or API keys to GitHub.**

---

# ▶️ Running the Application

Start the FastAPI backend:

```bash
uvicorn main:app --reload
```

The backend will run locally and expose the REST API.

The frontend can then communicate with the FastAPI backend through the configured API endpoints.

---

# 💡 Example

### User Request

```text
Plan a 4-day trip from Delhi to Mumbai
for 2 people with a budget of ₹50,000.
I prefer a balanced travel experience.
```

### AI Generated Plan

```text
✈️ Transportation
Delhi → Mumbai
Round Trip

🏨 Hotel
Recommended hotel options
Price comparison

📍 Attractions
• Gateway of India
• Marine Drive
• Colaba Causeway
• Elephanta Caves

💰 Budget
Transportation: ₹12,000
Hotel: ₹16,000
Food: ₹8,000
Activities: ₹4,000
Local Transport: ₹5,000

Estimated Total: ₹45,000

🗓️ Itinerary

Day 1
Arrival → Hotel → Marine Drive

Day 2
Gateway of India → Colaba → South Mumbai

Day 3
Elephanta Caves → Local sightseeing

Day 4
Shopping → Checkout → Departure
```

---

# 🎯 Project Objective

The objective of this project is to build a **practical AI travel agent** that goes beyond simple text generation.

Instead of only generating an itinerary, the system combines:

```text
LLM
 +
Agentic AI
 +
LangGraph
 +
External Tools
 +
Travel APIs
 +
Budget Optimization
 +
Full-Stack Web Application
```

to create an end-to-end intelligent travel planning experience.

---

# 🔮 Future Improvements

* 🗺️ Interactive maps
* 🌦️ Weather-aware itinerary planning
* 🍽️ Restaurant recommendations
* 🚕 Local transportation planning
* 💳 Real-time price tracking
* 🔐 User authentication
* 💾 Persistent trip history
* 📱 Responsive mobile UI
* ⚡ Streaming AI responses
* 📊 Trip cost comparison dashboard
* 🧠 More advanced multi-agent planning

---

# 👨‍💻 Author

## Abhishek Kumar Abhi

MCA Student | AI/ML & Generative AI Enthusiast

### Interests

* Machine Learning
* Deep Learning
* Natural Language Processing
* Generative AI
* Agentic AI
* Retrieval-Augmented Generation
* AI Agents

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

---

## 📄 License

This project is intended for educational and portfolio purposes.
