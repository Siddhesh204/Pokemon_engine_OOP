import random,json,os
from core.effects import FormulaDamage
from core.interfaces import IAttempt,IEffect
from utils.common import Element, Category
from core.effects import ApplyStatusEffect,SetWeatherEffect,Status,Weather

class ClassicAttempt:
    def __init__(self, accuracy: int, on_hit_effect):
        self.accuracy = accuracy
        self.on_hit_effect = on_hit_effect

    def apply(self, context):
        # 1. Check Accuracy
        if self.accuracy >= 100 or random.randint(1, 100) <= self.accuracy:
            # 2. Apply the effect! (Make sure this says .apply)
            self.on_hit_effect.apply(context)
        else:
            print(f"> {context.attacker.name}'s attack missed!")

class ComboAttempt:
    def __init__(self, accuracy: int, min_hits: int, max_hits: int, per_hit_effect):
        self.accuracy = accuracy
        self.min_hits = min_hits
        self.max_hits = max_hits
        self.per_hit_effect = per_hit_effect

    def apply(self, context):
        # 1. Check Accuracy
        if self.accuracy >= 100 or random.randint(1, 100) <= self.accuracy:
            hits = random.randint(self.min_hits, self.max_hits)
            
            # 2. Hit multiple times!
            for i in range(hits):
                # Stop hitting if the defender faints mid-combo
                if context.defender.is_fainted:
                    break
                self.per_hit_effect.apply(context)
                
            print(f"> Hit {hits} time(s)!")
        else:
            print(f"> {context.attacker.name}'s attack missed!")

class Move:
    # Add priority: int = 0 right here at the end of the parameters!
    def __init__(self, name: str, element: Element, attempt, pp: int, priority: int = 0):
        self.name = name
        self.element = element
        self.attempt = attempt
        self.max_pp = pp
        self.pp = pp
        self.priority = priority  # And save it as an attribute here!

    def excute(self, context) -> None:
        if self.pp <= 0:
            print(f"But there is no PP left for {self.name}!")
            return
            
        self.pp -= 1
        self.attempt.apply(context) # Make sure this matches your attempt method!

class MoveFactory:
    _moves_cache = None

    @classmethod
    def load_moves(cls):
        if cls._moves_cache is None:
            engine_dir = os.path.dirname(os.path.dirname(__file__))
            filepath = os.path.join(engine_dir, 'data', 'moves.json')
            with open(filepath, 'r') as file:
                cls._moves_cache = json.load(file)
        return cls._moves_cache

    
    @staticmethod
    def create(name: str) -> Move:
        moves_db = MoveFactory.load_moves()
        if name not in moves_db:
            raise ValueError(f"Move '{name}' not found in moves.json!")

        data = moves_db[name]
        element = Element[data["element"]]
        priority = data.get("priority", 0) # Defaults to 0 for normal moves
        
        # Import all necessary effects cleanly at the top of the method
        from core.effects import FormulaDamage, ApplyStatusEffect, SetWeatherEffect, StatChangeEffect

        # --- 1. PURE STATUS CONDITIONS (e.g., Thunder Wave) ---
        if data["type"] == "status":
            status_enum = Status[data["status"]]
            effect = ApplyStatusEffect(status_enum)
            attempt = ClassicAttempt(accuracy=data["accuracy"], on_hit_effect=effect)
            
        # --- 2. WEATHER EFFECTS (e.g., Rain Dance) ---
        elif data["type"] == "weather":
            weather_enum = Weather[data["weather"]]
            effect = SetWeatherEffect(weather_enum)
            attempt = ClassicAttempt(accuracy=data["accuracy"], on_hit_effect=effect)

        # --- 3. STAT CHANGES (e.g., Swords Dance) ---
        elif data["type"] == "stat_change":
            effect = StatChangeEffect(
                stat_name=data["stat_name"],
                amount=data["amount"],
                target_self=data.get("target_self", False)
            )
            attempt = ClassicAttempt(accuracy=data["accuracy"], on_hit_effect=effect)
            
        # --- 4. DAMAGE MOVES (Classic or Combo) ---
        elif data["type"] in ["classic", "combo"]:
            category = Category[data["category"]]
            effect = FormulaDamage(power=data["power"], category=category, move_element=element)
            
            if data["type"] == "classic":
                attempt = ClassicAttempt(accuracy=data["accuracy"], on_hit_effect=effect)
            elif data["type"] == "combo":
                attempt = ComboAttempt(
                    accuracy=data["accuracy"], 
                    min_hits=data["min_hits"], 
                    max_hits=data["max_hits"], 
                    per_hit_effect=effect
                )
        
        # --- 5. ERROR CATCHER ---
        else:
            raise ValueError(f"Unknown move type: {data['type']}")

        # Return the final equipped Move object
        return Move(
            name=name, 
            element=element, 
            attempt=attempt, 
            pp=data["pp"], 
            priority=priority
        )