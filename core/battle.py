# core/battle.py
import random
from core.pokemon import Pokemon
from core.player import TerminalPlayer
from utils.common import Weather, Element

class BattleContext:
    def __init__(self, attacker, defender, move, engine):
        self.attacker = attacker
        self.defender = defender
        self.move = move
        self.engine = engine  
        self.force_switch = False


class BattleEngine:
    def __init__(self, t1, t2):
        self.t1 = t1
        self.t2 = t2
        self.turn_count = 1
        self.max_turns = 400
        self.weather = Weather.CLEAR
        self.weather_turns = 0
        self.last_log: list[str] = []

    def is_battle_over(self) -> bool:
        return self.t1.is_wiped_out() or self.t2.is_wiped_out() or self.turn_count >= self.max_turns

    def get_winner(self) -> str:
        if self.t1.is_wiped_out() and self.t2.is_wiped_out():
            return "It's a draw!"
        elif self.t1.is_wiped_out():
            return f"{self.t2.name} wins!"
        elif self.t2.is_wiped_out():
            return f"{self.t1.name} wins!"
        # ADD THIS CHECK:
        elif self.turn_count >= self.max_turns:
            return "Turn limit reached! It's a draw!"
            
        return "Battle is ongoing..."
    
    def set_weather(self, new_weather: Weather, turns: int = 5):
        self.weather = new_weather
        self.weather_turns = turns
        
        weather_messages = {
            Weather.SUN: "The sunlight turned harsh!",
            Weather.RAIN: "It started to rain!",
            Weather.SANDSTORM: "A sandstorm kicked up!",
            Weather.HAIL: "It started to hail!"
        }
        print(f"\n[{weather_messages.get(new_weather, 'The weather cleared.')}]")

    def excute_turn(self, p1_action: dict, p2_action: dict):
        """The Main Turn Loop - now completely sleek and readable."""
        print(f"\n>{'='*10} TURN {self.turn_count} {'='*10}")
        
        self._phase1_switches(p1_action, p2_action)
        self._phase2_attacks(p1_action, p2_action)
        self._phase3_end_of_turn()
        self._phase4_replacements()

        self.turn_count += 1

    def _phase1_switches(self, p1_action: dict, p2_action: dict):
        """Handles manual switching and Switch-In Abilities."""
        if p1_action["type"] == "switch":
            self.t1.switch(p1_action["index"])
            if self.t1.active.ability:
                self.t1.active.ability.on_switch_in(self, self.t1.active)
                
        if p2_action["type"] == "switch":
            self.t2.switch(p2_action["index"])
            if self.t2.active.ability:
                self.t2.active.ability.on_switch_in(self, self.t2.active)

    def _phase2_attacks(self, p1_action: dict, p2_action: dict):
        """Builds the attack queue, sorts by Priority/Speed, and executes moves."""
        from core.moves import MoveFactory
        attacks_to_process = []
        
        # 1. Build the Queue
        if p1_action["type"] in ["move", "struggle"]:
            move = self.t1.active.moves[p1_action["index"]] if p1_action["type"] == "move" else MoveFactory.create("Struggle")
            attacks_to_process.append({"team": self.t1, "target": self.t2, "move": move})
            
        if p2_action["type"] in ["move", "struggle"]:
            move = self.t2.active.moves[p2_action["index"]] if p2_action["type"] == "move" else MoveFactory.create("Struggle")
            attacks_to_process.append({"team": self.t2, "target": self.t1, "move": move})

        # 2. Sort by Priority FIRST, then by Speed (both descending)
        attacks_to_process.sort(
            key=lambda x: (x["move"].priority, x["team"].active.speed), 
            reverse=True
        )

        # 3. Execute Attacks
        for attack in attacks_to_process:
            atk_poke = attack["team"].active
            def_poke = attack["target"].active
            move = attack["move"]
            
            if atk_poke.is_fainted:
                continue
            if def_poke.is_fainted:
                print(f"\n> {atk_poke.name} attacked, but there was no target!")
                continue
            if not atk_poke.can_attack(): # Checks Paralysis, Sleep, Freeze
                continue

            print(f"\n> {atk_poke.name} used {move.name}! (PP: {max(0, move.pp - 1)}/{move.max_pp})")
            
            # Context and execution
            context = BattleContext(attacker=atk_poke, defender=def_poke, move=move, engine=self)
            move.attempt.apply(context)

    def _phase3_end_of_turn(self):
        """Applies Burn/Poison, Weather damage, and Item/Ability end-turn hooks."""
        # Status Damage
        self.t1.active.apply_end_of_turn_effects()
        self.t2.active.apply_end_of_turn_effects()
        
        # Weather Damage
        if self.weather in [Weather.SANDSTORM, Weather.HAIL]:
            for team in [self.t1, self.t2]:
                poke = team.active
                if not poke.is_fainted:
                    # Sandstorm doesn't hurt Rock, Ground, or Steel
                    if self.weather == Weather.SANDSTORM and not any(e.name in ["ROCK", "GROUND", "STEEL"] for e in poke.Elements):
                        poke.take_damage(max(1, poke.max_hp // 16))
                        print(f"[{poke.name} is buffeted by the sandstorm!]")
                        
        # Countdown the weather
        if self.weather != Weather.CLEAR:
            self.weather_turns -= 1
            if self.weather_turns <= 0:
                print(f"\n[The {self.weather.name.lower()} subsided.]")
                self.weather = Weather.CLEAR

        # Trigger Items and Abilities (like Leftovers)
        for team in [self.t1, self.t2]:
            if team.active.item:
                team.active.item.on_turn_end(self, team.active)
            if team.active.ability:
                team.active.ability.on_turn_end(self, team.active)

    def _phase4_replacements(self):
        """Handles faint replacements dynamically."""
        from core.ai import SmartAI 
        
        for team in [self.t1, self.t2]:
            if team.active.is_fainted and not team.is_wiped_out():
                # If it's an AI, let them pick a replacement instantly
                if "Player" not in team.name:
                    replacement_idx = SmartAI.choose_replacement(team)
                    team.switch(replacement_idx)
                # If it's the Player, we do NOTHING! 
                # The turn ends, React sees 0 HP, and forces the user to send a "switch" action for the next turn.
    def start_battle(self):
        if self.t1.active.ability:
            self.t1.active.ability.on_switch_in(self, self.t1.active)
        if self.t2.active.ability:
            self.t2.active.ability.on_switch_in(self, self.t2.active)