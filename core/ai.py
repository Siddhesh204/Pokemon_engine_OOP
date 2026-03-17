import random
from core.pokemon import Pokemon
from utils.common import get_type_multiplier

class BasicAI:
    @staticmethod
    def choose_move(attacker: Pokemon, defender: Pokemon) -> int:
        valid_moves = []
        
        for index, move in enumerate(attacker.moves):
            effectiveness = get_type_multiplier(move.element, defender.Elements)
            if effectiveness > 0.0:
                valid_moves.append(index)
        if not valid_moves:
            return 0
            
        return random.choice(valid_moves)
    @staticmethod
    def choose_action(team, opponent_team) -> dict:
        """
        Returns an Action dictionary: {"type": "move"|"switch", "index": int}
        """
        attacker = team.active
        defender = opponent_team.active
        
        # In core/ai.py inside BasicAI.choose_action
        valid_moves = []
        for index, move in enumerate(attacker.moves):
            # Check if the move has PP left!
            if move.pp > 0:
                effectiveness = get_type_multiplier(move.element, defender.Elements)
                if effectiveness > 0.0:
                    valid_moves.append(index)

        if not attacker.has_usable_moves():
            print(f"[{team.name}'s {attacker.name} has no moves left!]")
            return {"type": "struggle"}

        if valid_moves:
            return {"type": "move", "index": random.choice(valid_moves)}
        
        available_switches = team.get_available_indices()
        if available_switches:
            print(f"[{team.name}'s AI detects a bad matchup and decides to switch!]")
            return {"type": "switch", "index": available_switches[0]}

        return {"type": "move", "index": 0}

    @staticmethod
    def choose_replacement(team) -> int:
        """Picks the first available Pokemon to replace a fainted one."""
        available = team.get_available_indices()
        if available:
            return available[0]
        return -1
    # Add this inside the BasicAI class in core/ai.py

    @staticmethod
    def choose_lead(team) -> int:
        """
        Picks a lead Pokemon before the battle starts.
        Chooses randomly from all healthy team members.
        """
        valid_leads = [i for i, p in enumerate(team.members) if not p.is_fainted]
        
        if valid_leads:
            return random.choice(valid_leads)
        
        return 0 # Fallback
import random
from utils.common import get_type_multiplier, Status, Element

class SmartAI:
    @staticmethod
    def choose_lead(team) -> int:
        """Picks a random healthy lead."""
        valid_leads = [i for i, p in enumerate(team.members) if not p.is_fainted]
        return random.choice(valid_leads) if valid_leads else 0

    @staticmethod
    def choose_replacement(team) -> int:
        """Picks the first available healthy Pokemon."""
        available = team.get_available_indices()
        return available[0] if available else 0

    @staticmethod
    def evaluate_matchup(attacker, defender) -> int:
        """A simple +1 / -1 score based on offensive type advantage."""
        score = 0
        for move in attacker.moves:
            # Only check damage moves
            if hasattr(move.attempt, 'on_hit_effect') and hasattr(move.attempt.on_hit_effect, 'power'):
                effectiveness = get_type_multiplier(move.element, defender.Elements)
                if effectiveness > 1.0: score += 1
                elif effectiveness < 1.0: score -= 1
        return score

    @staticmethod
    def choose_action(team, opponent_team) -> dict:
        attacker = team.active
        defender = opponent_team.active

        if not attacker.has_usable_moves():
            return {"type": "struggle"}

        # --- 1. SMART SWITCHING LOGIC ---
        # Initialize a turn tracker on the team if it doesn't exist
        if not hasattr(team, "turns_on_field"):
            team.turns_on_field = 0
        team.turns_on_field += 1

        matchup_score = SmartAI.evaluate_matchup(attacker, defender)
        
        # Only switch if matchup is bad AND we've been on the field for at least 1 full turn.
        # This completely breaks the infinite switching loop!
        if matchup_score < 0 and team.turns_on_field > 1:
            available = team.get_available_indices()
            if available:
                best_switch_idx = available[0]
                best_score = -999
                
                # Scan the bench for a Pokemon that actually beats the opponent
                for idx in available:
                    candidate = team.members[idx]
                    score = SmartAI.evaluate_matchup(candidate, defender)
                    if score > best_score:
                        best_score = score
                        best_switch_idx = idx
                
                # If we found a positive matchup, switch to them and reset the field timer!
                if best_score > 0:
                    print(f"[{team.name}'s AI calculated a {best_score} advantage and is switching!]")
                    team.turns_on_field = 0 # Reset timer
                    return {"type": "switch", "index": best_switch_idx}

        # --- 2. MOVE SCORING SYSTEM ---
        best_move_idx = 0
        best_move_score = -1

        for i, move in enumerate(attacker.moves):
            if move.pp <= 0:
                continue

            score = 0
            
            # Check what kind of effect the move has by looking at its dictionary data implicitly
            # A. STATUS MOVES (Toxic, Thunder Wave)
            if move.name in ["Toxic", "Thunder Wave"]:
                if defender.status == Status.NONE:
                    score = 80 # Very high priority if the enemy is healthy
                else:
                    score = 0  # Literally worthless if they already have a status

            # B. SETUP MOVES (Swords Dance)
            elif move.name == "Swords Dance":
                if team.turns_on_field < 3:
                    score = 70 # High priority early on
                else:
                    score = 20 # Low priority if we've been fighting a while

            # C. WEATHER MOVES (Rain Dance)
            elif move.name == "Rain Dance":
                # Give it a random high chance to setup weather early
                score = 75 if team.turns_on_field == 1 else 10

            # D. DAMAGE MOVES (Shadow Ball, Focus Blast, Hex)
            else:
                # Get the base power
                power = 60 # Default fallback
                if hasattr(move.attempt, 'on_hit_effect') and hasattr(move.attempt.on_hit_effect, 'power'):
                    power = move.attempt.on_hit_effect.power

                # Hex logic! Double the simulated power if enemy is statused
                if move.name == "Hex" and defender.status != Status.NONE:
                    power *= 2

                effectiveness = get_type_multiplier(move.element, defender.Elements)
                stab = 1.5 if move.element in attacker.Elements else 1.0
                
                # The mathematical core of the AI's decision:
                score = int(power * effectiveness * stab)
                
                # If they are immune, score is 0
                if effectiveness == 0:
                    score = 0

            # Add a tiny bit of RNG so the AI isn't 100% perfectly predictable
            score += random.randint(0, 5)

            if score > best_move_score:
                best_move_score = score
                best_move_idx = i

        return {"type": "move", "index": best_move_idx}