# Custom Pokémon Battle Engine

A fully custom, mathematically accurate, event-driven Pokémon battle simulator built from scratch.

## Architecture
* **Backend:** Python (Object-Oriented, Decoupled Architecture)
* **API Bridge:** FastAPI & Pydantic
* **Frontend:** React, Vite, Tailwind CSS (v3)
* **AI:** Custom Heuristic Scoring Bot

## Features
* Retroactive Fairy & Steel types integrated into Gen 1.
* Weather systems, Stat Modifiers, and Status Conditions.
* Dynamic JSON loading for Pokedex and Move pools.
* Priority queue systems and mid-turn forced switching.

## How to Run

### 1. Start the API (Backend)
Open a terminal in the root directory and run:
\`\`\`bash
python -m uvicorn api:app --reload
\`\`\`
*(The server will start on `http://127.0.0.1:8000`)*

### 2. Start the UI (Frontend)
Open a second terminal, navigate to the frontend folder, and start Vite:
\`\`\`bash
cd frontend
npm run dev
\`\`\`
*(The UI will be available at `http://localhost:5173/`)*