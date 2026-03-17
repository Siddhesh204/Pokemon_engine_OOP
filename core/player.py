# core/player.py

class TerminalPlayer:
    @staticmethod
    def choose_action(team, opponent_team) -> dict:
        active = team.active
        print(f"\n[{team.name}'s Turn] -> Active: {active.name} (HP: {active.current_hp}/{active.max_hp})")
        print("1. Fight")
        print("2. Pokemon (Switch)")
        
        while True:
            choice = input("What will you do? (1 or 2): ").strip()
            
            if choice == "1":

                if not active.has_usable_moves():
                    print(f"\n{active.name} has no moves left! It has to use Struggle!")
                    return {"type": "struggle"}
                print("\n--- MOVES ---")
                for i, move in enumerate(active.moves):
                    print(f"  {i}: {move.name} [{move.element.name}] (PP: {move.pp}/{move.max_pp})")
                print(f"  B: Back")
                
                move_idx = input("Choose a move: ").strip()
                if move_idx.upper() == "B":
                    continue # Go back to main menu
                    
                if move_idx.isdigit() and 0 <= int(move_idx) < len(active.moves):
                    if active.moves[int(move_idx)].pp > 0:
                        return {"type": "move", "index": int(move_idx)}
                    else:
                        print("No PP left for that move!")
                else:
                    print("Invalid move index.")

            elif choice == "2":
                print("\n--- TEAM ---")
                available = team.get_available_indices()
                if not available:
                    print("You have no other Pokemon left to switch to!")
                    continue
                    
                for i in available:
                    p = team.members[i]
                    print(f"  {i}: {p.name} (HP: {p.current_hp}/{p.max_hp})")
                print(f"  B: Back")
                
                switch_idx = input("Choose a Pokemon: ").strip()
                if switch_idx.upper() == "B":
                    continue
                    
                if switch_idx.isdigit() and int(switch_idx) in available:
                    return {"type": "switch", "index": int(switch_idx)}
                else:
                    print("Invalid Pokemon index.")
            else:
                print("Please type 1 or 2.")

    @staticmethod
    def choose_replacement(team) -> int:
        print(f"\n[{team.name}] {team.active.name} fainted!")
        print("--- CHOOSE REPLACEMENT ---")
        available = team.get_available_indices()
        
        for i in available:
            p = team.members[i]
            print(f"  {i}: {p.name} (HP: {p.current_hp}/{p.max_hp})")
            
        while True:
            choice = input("Send out which Pokemon? ").strip()
            if choice.isdigit() and int(choice) in available:
                return int(choice)
            print("Invalid choice.")