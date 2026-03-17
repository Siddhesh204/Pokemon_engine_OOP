import time
from core import PokemonFactory, BattleEngine, Move, ClassicAttempt, ComboAttempt, FormulaDamage
from utils.common import Element, Category
 
def setup_game():
    # 1. Create our Pokemon using the Factory
    print("Initializing Pokemon...")
    gengar = PokemonFactory.create("Gengar", level=50)
    snorlax = PokemonFactory.create("Snorlax", level=50)
 
    # 2. Build Gengar's Move: Shadow Ball (Special, Ghost, 80 Power, 100% Accuracy)
    shadow_ball_effect = FormulaDamage(power=80, category=Category.SPECIAL)
    shadow_ball_attempt = ClassicAttempt(accuracy=100, on_hit_effect=shadow_ball_effect)
    shadow_ball = Move(name="Shadow Ball", element=Element.GHOST, attempt=shadow_ball_attempt)
 
    # 3. Build Snorlax's Move: Fury Swipes (Physical, Normal, 18 Power, 80% Acc, 2-5 hits)
    fury_swipes_effect = FormulaDamage(power=18, category=Category.PHYSICAL)
    fury_swipes_attempt = ComboAttempt(accuracy=80, min_hits=2, max_hits=5, per_hit_effect=fury_swipes_effect)
    fury_swipes = Move(name="Fury Swipes", element=Element.NORMAL, attempt=fury_swipes_attempt)
 
    return gengar, snorlax, shadow_ball, fury_swipes
 
def main():
    # Setup
    gengar, snorlax, gengar_move, snorlax_move = setup_game()
    
    # Initialize the Arena
    engine = BattleEngine(Player1=gengar, Player2=snorlax)
    
    print("\n" + "*"*30)
    print(f"BATTLE START: {gengar.name} vs {snorlax.name}!")
    print("*"*30)
 
    # The Main Game Loop
    while not engine.is_battle_over():
        # In a real game, you would prompt the user for input here.
        # For our simulation, we just pass their predefined moves.
        engine.excute_turn(p1_move=gengar_move, p2_move=snorlax_move)
        
        # Pause for 1.5 seconds so you can actually read the terminal output
        time.sleep(1.5)
 
    # Determine Winner
    print("\n" + "*"*30)
    print("BATTLE OVER!")
    print(engine.get_winner())
    print("*"*30)
 
if __name__ == "__main__":
    main()