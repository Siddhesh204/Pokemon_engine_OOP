from utils.common import Element,Status
import math,os,json,random
from typing import Any
from utils.common import Element, Status

class Pokemon:
    def __init__(self, name: str, level: int, Elements: list[Element], stats: dict):
        self.name = name
        self.level = level
        self.Elements = Elements
        self.moves = []

        self.max_hp = stats.get("hp", 10)
        self.current_hp = self.max_hp
        self.attack = stats.get("attack", 10)
        self.defense = stats.get("defense", 10)
        self.sp_attack = stats.get("sp_attack", 10)
        self.sp_defense = stats.get("sp_defense", 10)
        self.speed = stats.get("speed", 10)
        self.status_turns = 0
        self.ability:Any = None
        self.item:Any = None
        self.status = Status.NONE

        self.stat_stages = {
            "attack": 0, "defense": 0, "sp_attack": 0, "sp_defense": 0, "speed": 0
        }

    @property
    def is_fainted(self) -> bool:
        return self.current_hp <= 0

    def take_damage(self, amount: int):
        self.current_hp = max(0, self.current_hp - amount)
        print(f"[{self.name}] took {amount} damage (HP: {self.current_hp}/{self.max_hp})")
        if self.is_fainted:
            print(f"[{self.name}] fainted!")

    def apply_status(self, new_status: Status):
        if self.status == Status.NONE and new_status != Status.NONE:
            self.status = new_status
            print(f"[{self.name}] was inflicted with {new_status.name}!")
            
            # Sleep lasts for 1 to 3 turns
            if new_status == Status.SLEEP:
                self.status_turns = random.randint(1, 3)

    def change_stat(self, stat_name: str, amount: int):
        current = self.stat_stages[stat_name]
        new_stage = max(-6, min(6, current + amount))
        if current != new_stage:
            self.stat_stages[stat_name] = new_stage
            direction = "rose" if amount > 0 else "fell"
            print(f"[{self.name}]'s {stat_name} {direction}!")
        else:
            print(f"[{self.name}]'s {stat_name} won't go any {'higher' if amount > 0 else 'lower'}!")

    def get_stat(self, stat_name: str) -> int:
        base_stat = getattr(self, stat_name)
        stage = self.stat_stages[stat_name]
        numerator = 2 + max(0, stage)
        denominator = 2 + max(0, -stage)
        
        calc_stat = int(base_stat * (numerator / denominator))
        
        # Burn halves physical attack. Paralyze halves speed.
        if self.status == Status.BURN and stat_name == "attack":
            calc_stat = int(calc_stat / 2)
        elif self.status == Status.PARALYZE and stat_name == "speed":
            calc_stat = int(calc_stat / 2)
            
        return calc_stat

    def can_attack(self) -> bool:
        """Returns False if a status condition prevents the Pokemon from moving."""
        if self.status == Status.PARALYZE:
            if random.randint(1, 100) <= 25:
                print(f"[{self.name}] is fully paralyzed and can't move!")
                return False
        
        elif self.status == Status.FREEZE:
            # 20% chance to thaw each turn
            if random.randint(1, 100) <= 20:
                print(f"[{self.name}] thawed out!")
                self.status = Status.NONE
            else:
                print(f"[{self.name}] is frozen solid!")
                return False
                
        elif self.status == Status.SLEEP:
            if self.status_turns <= 0:
                print(f"[{self.name}] woke up!")
                self.status = Status.NONE
            else:
                self.status_turns -= 1
                print(f"[{self.name}] is fast asleep.")
                return False
                
        return True

    def apply_end_of_turn_effects(self):
        """Handles Burn and Poison damage."""
        if self.is_fainted: 
            return
            
        if self.status == Status.BURN:
            damage = max(1, self.max_hp // 16)
            print(f"[{self.name}] was hurt by its burn!")
            self.take_damage(damage)
            
        elif self.status == Status.POISON:
            damage = max(1, self.max_hp // 8)
            print(f"[{self.name}] was hurt by poison!")
            self.take_damage(damage)
    def has_usable_moves(self) -> bool:
        return any(move.pp > 0 for move in self.moves)
            
class PokemonFactory:
    _pokedex_cache = None  # Cache so we don't read the hard drive every time
 
    @classmethod
    def load_pokedex(cls):
        if cls._pokedex_cache is None:
            filepath = os.path.join(os.path.dirname(__file__), '..', 'data', 'pokedex.json')
            with open(filepath, 'r') as file:
                cls._pokedex_cache = json.load(file)
        return cls._pokedex_cache

    @staticmethod 
    def create(name:str,level:int) -> Pokemon:
        pokedex = PokemonFactory.load_pokedex()
        if name not in pokedex:
            raise ValueError(f"Pokemon {name}not in Pokedex!")
        
        data=pokedex[name]
        base=data["base_stats"]

        element_enums = [Element[e] for e in data["elements"]]
        calculated_stats={}

        calculated_stats["hp"]=math.floor(((2*base["hp"])*level)/100)+level+10

        for stat in ["attack","defense","sp_attack","sp_defense","speed"]:
            calculated_stats[stat]=math.floor(((2*base[stat])*level)/100)+5

        return Pokemon(
            name=name,
            level=level,
            Elements=element_enums,
            stats=calculated_stats
        )
