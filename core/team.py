# core/team.py
import json,os
from core.pokemon import Pokemon ,PokemonFactory
from core.moves import MoveFactory
import  core.modifiers as mods

class Team:
    def __init__(self, name: str):
        self.name = name
        self.members: list[Pokemon] = []
        self.active_index = 0
        
    def add_pokemon(self, pokemon: Pokemon):
        
        if len(self.members) < 6:
            self.members.append(pokemon)
        else:
            print(f"{self.name}'s team is already full!")

    @property
    def active(self) -> Pokemon:
        
        return self.members[self.active_index]

    def set_lead(self, index: int):
        if 0 <= index < len(self.members) and not self.members[index].is_fainted:
            self.active_index = index
            print(f"{self.name} will lead with {self.active.name}!")

    def switch(self, index: int):
        if 0 <= index < len(self.members) and not self.members[index].is_fainted:
            if not self.active.is_fainted:
                print(f"{self.name} withdrew {self.active.name}!")
            self.active_index = index
            print(f"{self.name} sent out {self.active.name}!")
        else:
            print("Invalid switch!")

    def is_wiped_out(self) -> bool:
        return all(p.is_fainted for p in self.members)

    def get_available_indices(self) -> list[int]:
        return [i for i, p in enumerate(self.members) if not p.is_fainted and i != self.active_index]

    def get_team_preview_json(self) -> str:
        team_data = []
        for p in self.members:
            team_data.append({
                "name": p.name,
                "level": p.level,
                "hp_percent": round((p.current_hp / p.max_hp) * 100, 1),
                "is_fainted": p.is_fainted,
                "moves": [m.name for m in p.moves],
                "elements": [e.name for e in p.Elements]
            })
        return json.dumps({"team_name": self.name, "roster": team_data}, indent=4)
    @staticmethod
    def _instantiate_modifier(modifier_name: str):
        """
        Reusable Sub-Method 1: Dynamic Reflection.
        Safely searches modifiers.py for a class matching the string and instantiates it.
        """
        if not modifier_name or modifier_name == "None":
            return None
            
        modifier_class = getattr(mods, modifier_name, None)
        if modifier_class:
            return modifier_class()
            
        print(f"Warning: Modifier '{modifier_name}' not found in modifiers.py!")
        return None

    @classmethod
    def _build_pokemon_from_dict(cls, p_data: dict):
        """
        Reusable Sub-Method 2: Object Mapping.
        Converts a raw dictionary into a fully equipped Pokemon object.
        Highly useful if we ever pull Pokemon data from a web API or database later!
        """
        pokemon = PokemonFactory.create(p_data["name"], level=p_data.get("level", 50))
        pokemon.moves = [MoveFactory.create(m_name) for m_name in p_data.get("moves", [])]
        
        # Use our sleek reflection helper
        pokemon.ability = cls._instantiate_modifier(p_data.get("ability", "None"))
        pokemon.item = cls._instantiate_modifier(p_data.get("item", "None"))
        
        return pokemon

    @classmethod
    def load_from_json(cls, filename: str) -> 'Team':
        """
        Main Method: File I/O and Team Assembly.
        It is now completely stripped of parsing logic and reads like plain English.
        """
        engine_dir = os.path.dirname(os.path.dirname(__file__))
        filepath = os.path.join(engine_dir, 'data', filename)
        
        with open(filepath, 'r') as file:
            data = json.load(file)
            
        team = cls(data.get("team_name", "Unknown Team"))
        
        for p_data in data.get("members", []):
            pokemon = cls._build_pokemon_from_dict(p_data)
            team.add_pokemon(pokemon)
            
        return team