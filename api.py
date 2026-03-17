import sys
import io
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.battle import BattleEngine
from core.ai import SmartAI
from mainloop import build_showcase_team

app = FastAPI(title="Pokemon Showdown API")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

game_engine = None

class PlayerAction(BaseModel):
    action_type: str
    index: int

@app.post("/start_game")
def start_game():
    global game_engine
    red_team = build_showcase_team("Player 1")
    blue_team = build_showcase_team("AI Blue")
    
    # Hijack the print statements for the battle start Intimidate triggers!
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    game_engine = BattleEngine(t1=red_team, t2=blue_team)
    game_engine.start_battle() 
    
    sys.stdout = sys.__stdout__ # Give the terminal its print powers back
    
    # Clean up the output into a list of strings
    raw_log = captured_output.getvalue().strip().split('\n')
    game_engine.last_log = [line for line in raw_log if line.strip() != ""]
    
    return get_battle_state()
@app.post("/execute_turn")
def execute_turn(action: PlayerAction):
    global game_engine
    if not game_engine: return {"status": "waiting"}

    if game_engine.t1.active.is_fainted:
        if action.action_type == "switch":
            game_engine.t1.switch(action.index) # Swap the Pokemon
            game_engine.last_log = [f"Player sent out {game_engine.t1.active.name}!"]
            return get_battle_state() # Return immediately, do NOT let the AI attack!

    # --- NORMAL TURN LOGIC ---
    p1_action = {"type": action.action_type, "index": action.index}
    p2_action = SmartAI.choose_action(game_engine.t2, game_engine.t1)

    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    game_engine.excute_turn(p1_action, p2_action)
    
    sys.stdout = sys.__stdout__ 
    
    raw_log = captured_output.getvalue().strip().split('\n')
    game_engine.last_log = [line for line in raw_log if line.strip() != ""]

    if game_engine.is_battle_over():
        return {"status": "game_over", "winner": game_engine.get_winner()}

    return get_battle_state()

@app.get("/get_battle_state")
def get_battle_state():
    global game_engine
    if not game_engine: return {"status": "waiting"}

    p1 = game_engine.t1.active
    p2 = game_engine.t2.active

    return {
        "status": "active",
        "turn": game_engine.turn_count,
        "weather": game_engine.weather.name,
        "log": getattr(game_engine, "last_log", []), # NEW: Send the log!
        "player": {
            "name": p1.name, "hp": max(0, p1.current_hp), "max_hp": p1.max_hp,
            "status": p1.status.name if hasattr(p1.status, 'name') else "NONE",
            "moves": [{"name": m.name, "pp": m.pp, "max_pp": m.max_pp, "element": m.element.name} for m in p1.moves],
            "party": [{"name": poke.name, "hp": max(0, poke.current_hp), "max_hp": poke.max_hp, "is_active": poke == p1} for poke in game_engine.t1.members]
        },
        "opponent": {
            "name": p2.name, "hp": max(0, p2.current_hp), "max_hp": p2.max_hp,
            "status": p2.status.name if hasattr(p2.status, 'name') else "NONE"
        }
    }