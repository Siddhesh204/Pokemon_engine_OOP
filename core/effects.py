import random
from core.interfaces import IEffect
from utils.common import math_engine, Status, Category, get_type_multiplier, Element, Weather

class FormulaDamage(IEffect):
    def __init__(self, power: int, category: Category, move_element: Element):
        self.power = power
        self.category = category
        self.move_element = move_element

    def apply(self, context):
        active_power = self.power
        
        # 1. WEATHER MODIFIERS (Changes active_power before the big math!)
        if context.engine.weather == Weather.RAIN:
            if self.move_element == Element.WATER:
                active_power = int(active_power * 1.5)
            elif self.move_element == Element.FIRE:
                active_power = int(active_power * 0.5)
                
        elif context.engine.weather == Weather.SUN:
            if self.move_element == Element.FIRE:
                active_power = int(active_power * 1.5)
            elif self.move_element == Element.WATER:
                active_power = int(active_power * 0.5)

        # 2. GRAB STATS
        if self.category == Category.PHYSICAL:
            atk_stat = context.attacker.get_stat("attack")
            def_stat = context.defender.get_stat("defense")
        elif self.category == Category.SPECIAL:
            atk_stat = context.attacker.get_stat("sp_attack")
            def_stat = context.defender.get_stat("sp_defense")
        else:
            return

        # 3. TYPE MULTIPLIERS
        stab = 1.5 if self.move_element in context.attacker.Elements else 1.0
        effectiveness = get_type_multiplier(self.move_element, context.defender.Elements)
        
        if effectiveness == 0.0:
            print(f"It doesn't affect {context.defender.name}...")
            return
        elif effectiveness > 1.0:
            print(f"It's super effective against {context.defender.name}!")
        elif effectiveness < 1.0:
            print(f"It's not very effective against {context.defender.name}!")

        roll = random.randint(85, 100) / 100.0
        final_modifier = stab * effectiveness * roll

        # 4. DAMAGE CALCULATION
        if math_engine:
            damage = math_engine.calculate_damage(
                context.attacker.level,
                active_power,  # Make sure we use the weather-modified power here!
                atk_stat,
                def_stat,
                final_modifier
            )
        else:
            base_calc = ((2.0 * context.attacker.level) / 5.0) + 2.0
            stat_ratio = atk_stat / def_stat
            raw_damage = ((base_calc * active_power * stat_ratio) / 50.0) + 2.0
            damage = raw_damage * final_modifier

        final_damage = int(damage)
        context.defender.take_damage(final_damage)

class ApplyStatusEffect(IEffect):
    def __init__(self, status_to_apply: Status):
        self.status_to_apply = status_to_apply

    def apply(self, context) -> None:
        if context.defender.status == Status.NONE:
            context.defender.apply_status(self.status_to_apply)
        else:
            print(f"But it failed! {context.defender.name} already has a status condition.")

class SetWeatherEffect(IEffect):
    def __init__(self, weather_to_set: Weather):
        self.weather_to_set = weather_to_set

    def apply(self, context) -> None:
        if context.engine.weather != self.weather_to_set:
            context.engine.set_weather(self.weather_to_set)
        else:
            print("But it failed! The weather is already like this.")

class StatChangeEffect(IEffect):
    def __init__(self, stat_name: str, amount: int, target_self: bool = False) -> None:
        self.stat_name = stat_name
        self.amount = amount
        self.target_self = target_self

    def apply(self, context):
        target = context.attacker if self.target_self else context.defender
        target.change_stat(self.stat_name, self.amount)