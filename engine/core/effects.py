from core.interfaces import IEffect
from utils.common import math_engine,Status,Category

class FormulaDamage(IEffect):
    def __init__(self,power:int,category:Category,type_modifier:float=1.0):
        self.power=power
        self.category=category
        self.type_modifier =type_modifier

    def apply(self, context):
        if self.category == Category.PHYSICAL:
            atk_stat=context.attacker.attack
            def_stat=context.defender.defense
        if self.category == Category.SPECIAL:
            atk_stat=context.attacker.sp_attack
            def_stat=context.defender.sp_defense
        else:
            return
        
        if math_engine:
            damage=math_engine.calculate_damage(
                context.attacker.level,
                self.power,
                atk_stat,
                def_stat,
                self.type_modifier
            )
        else:
            base_calc=((2.0*context.attacker.level)/5.0)+2.0
            stat_ratio=atk_stat/def_stat
            raw_damage=((base_calc*self.power*stat_ratio)/50.0)+2.0
            damage =raw_damage*self.type_modifier

        final_damage=int(damage)
        context.defender.take_damage(final_damage)

class ApplyStatus(IEffect):
    def __init__(self,status:Status):
        self.status =status

    def apply(self, context) -> None:
        context.defender.apply_status(self.status)
        