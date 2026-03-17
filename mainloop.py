import time
from core.team import Team
from core.pokemon import PokemonFactory
from core.moves import MoveFactory
from core.battle import BattleEngine
from core.ai import BasicAI,SmartAI
from core.player import TerminalPlayer
from core.modifiers import Intimidate, Leftovers

def build_showcase_team(team_name: str) -> Team:
    team = Team(team_name)
    
    # 1. The Weather & Priority Setter
    p1 = PokemonFactory.create("Gengar", level=50)
    p1.name = "[Weather] Gengar" 
    p1.moves = [MoveFactory.create("Rain Dance"), MoveFactory.create("Quick Attack")]
    p1.ability = Intimidate()
    team.add_pokemon(p1)

    # 2. The Setup Sweeper
    p2 = PokemonFactory.create("Snorlax", level=50)
    p2.name = "[Setup] Snorlax"
    p2.moves = [MoveFactory.create("Swords Dance"), MoveFactory.create("Body Slam")]
    p2.item = Leftovers()
    team.add_pokemon(p2)

    # 3. The Status Hexer
    p3 = PokemonFactory.create("Gengar", level=50)
    p3.name = "[Hex] Gengar"
    p3.moves = [MoveFactory.create("Thunder Wave"), MoveFactory.create("Hex"), MoveFactory.create("Toxic")]
    team.add_pokemon(p3)

    # 4. The Standard Attacker (Replaced U-Turn Snorlax)
    p4 = PokemonFactory.create("Snorlax", level=50)
    p4.name = "[Attacker] Snorlax"
    p4.moves = [MoveFactory.create("Body Slam"), MoveFactory.create("Fury Swipes")]
    team.add_pokemon(p4)

    # 5. The Heavy Hitter
    p5 = PokemonFactory.create("Gengar", level=50)
    p5.name = "[Striker] Gengar"
    p5.moves = [MoveFactory.create("Shadow Ball"), MoveFactory.create("Focus Blast")]
    team.add_pokemon(p5)

    # 6. The PP Stall (Only has a 5 PP move to force Struggle quickly)
    p6 = PokemonFactory.create("Snorlax", level=50)
    p6.name = "[Struggle] Snorlax"
    p6.moves = [MoveFactory.create("Focus Blast")] 
    team.add_pokemon(p6)

    # AI randomly picks the lead
    team.set_lead(BasicAI.choose_lead(team))
    return team

def main():
    print("\n" + "="*40)
    print(" ⚡ POKEMON SHOWDOWN ENGINE: GEN 1 ⚡")
    print("="*40)
    print("1. Player vs AI")
    print("2. Player vs Player")
    print("3. AI vs AI")
    print("="*40)
    
    while True:
        mode = input("Select Game Mode (1/2/3): ").strip()
        if mode in ["1", "2", "3"]:
            break
        print("Invalid choice. Please type 1, 2, or 3.")
    # Assign Controllers based on Game Mode
    # t1_controller = TerminalPlayer if mode in ["1", "2"] else BasicAI
    # t2_controller = TerminalPlayer if mode == "2" else BasicAI
    # At the top of mainloop.py


    t1_controller = TerminalPlayer if mode in ["1", "2"] else SmartAI
    t2_controller = TerminalPlayer if mode == "2" else SmartAI
    
    # ... [Down at the lead setup] ...
    # team.set_lead(SmartAI.choose_lead(team))
    
    # NEW: Dynamically name the teams so the Engine knows who is who!
    t1_name = "Player 1" if mode in ["1", "2"] else "AI Red"
    t2_name = "Player 2" if mode == "2" else "AI Blue"
    
    # Build the 6v6 Showcase Teams using the correct names
    red_team = build_showcase_team(t1_name)
    blue_team = build_showcase_team(t2_name)
    
    engine = BattleEngine(t1=red_team, t2=blue_team)
    
    print("\n" + "*"*40)
    print(f"BATTLE START: {red_team.name} vs {blue_team.name}!")
    print("*"*40)

    # Triggers Intimidate for the leads!
    engine.start_battle()

    while not engine.is_battle_over():
        # Dynamic Controller Inputs
        p1_action = t1_controller.choose_action(team=red_team, opponent_team=blue_team)
        p2_action = t2_controller.choose_action(team=blue_team, opponent_team=red_team)
        
        engine.excute_turn(p1_action=p1_action, p2_action=p2_action)
        
        # Pause so you can actually read the terminal
        time.sleep(1.5 if mode != "3" else 0) 

    print("\n" + "*"*40)
    print("BATTLE OVER!")
    print(engine.get_winner())
    print("*"*40)

if __name__ == "__main__":
    main()