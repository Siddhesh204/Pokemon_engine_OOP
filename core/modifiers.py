
class Ability:
    def __init__(self, name: str):
        self.name = name

    # Hooks that the engine will call!
    def on_switch_in(self, engine, pokemon): pass
    def on_turn_end(self, engine, pokemon): pass

class Item:
    def __init__(self, name: str):
        self.name = name

    def on_turn_end(self, engine, pokemon): pass


class Intimidate(Ability):
    def __init__(self):
        super().__init__("Intimidate")

    def on_switch_in(self, engine, pokemon):
        print(f"\n[{pokemon.name}'s Intimidate!]")
        # Find the opponent
        opponent = engine.t2.active if pokemon in engine.t1.members else engine.t1.active
        
        if not opponent.is_fainted:
            opponent.change_stat("attack", -1)

class Leftovers(Item):
    def __init__(self):
        super().__init__("Leftovers")

    def on_turn_end(self, engine, pokemon):
        if not pokemon.is_fainted and pokemon.current_hp < pokemon.max_hp:
            heal_amount = max(1, pokemon.max_hp // 16)
            pokemon.current_hp = min(pokemon.max_hp, pokemon.current_hp + heal_amount)
            print(f"[{pokemon.name} restored a little HP using its Leftovers! (HP: {pokemon.current_hp}/{pokemon.max_hp})]")