from utils.common import Element,Status
import math

class Pokemon:
    def __init__(self,name:str,level:int,Elements:list[Element],stats:dict):
        self.name=name
        self.level=level
        self.Elements=Elements

        self.max_hp =stats.get("hp",10)
        self.current_hp = self.max_hp
        self.attack=stats.get("attack",10)
        self.defense=stats.get("defense",10)
        self.sp_attack=stats.get("sp_attack",10)
        self.sp_defense=stats.get("sp_defense",10)
        self.speed=stats.get("speed",10)

        self.status = Status.NONE

    @property
    def is_fainted(self)->bool:
        return self.current_hp <= 0


    def take_damage(self,amount:int):
        self.current_hp = max(0,self.current_hp - amount )
        print(f"[{self.name}] took {amount}damage (HP:{self.current_hp/self.max_hp})")
        if self.is_fainted:
            print(f"[{self.name}] fainted")

    def apply_status(self,new_status: Status):
        if self.status == Status.NONE and new_status != Status.NONE:
            self.status =new_status
            print(f"[{self.name}] was inflicted with {new_status.name}")

class PokemonFactory:
    Pokedex = {
        "Gengar":{
            "Elements":[Element.GHOST,Element.POISON],
            "base_stats":{"hp":60,"attack":65,"defense":60,"sp_attack":130,"sp_defense":75,"speed":110}
        },
        "Snorlax":{
            "Elements":[Element.NORMAL],
            "base_stats":{"hp":160,"attack":110,"defense":65,"sp_attack":65,"sp_defense":110,"speed":30}
        },
    }
    @staticmethod 
    def create(name:str,level:int) -> Pokemon:
        if name not in PokemonFactory.Pokedex:
            raise ValueError(f"Pokemon {name}not in Pokedex!")
        
        data=PokemonFactory.Pokedex[name]
        base=data["base_stats"]

        calculated_stats={}

        calculated_stats["hp"]=math.floor(((2*base["hp"])*level)/100)+level+10

        for stat in ["attack","defense","sp_attack","sp_defense","speed"]:
            calculated_stats[stat]=math.floor(((2*base[stat])*level)/100)+5

        return Pokemon(
            name=name,
            level=level,
            Elements=data["Elements"],
            stats=calculated_stats
        )