import random
from core.interfaces import IAttempt,IEffect
from utils.common import Element

class ClassicAttempt(IAttempt):
    def __init__(self,accuracy:int,on_hit_effect:IEffect):
        self.accuracy=accuracy
        self.on_hit_effect=on_hit_effect

    def excute(self, context):
        if random.randint(1,100)<=self.accuracy:
            self.on_hit_effect.apply(context)
        else:
            print(f"...but it missed")
        
class ComboAttempt(IAttempt):
    def __init__(self,accuracy:int,min_hits:int,max_hits:int,per_hit_effect:IEffect):
        self.accuracy=accuracy
        self.min_hits=min_hits
        self.max_hits=max_hits
        self.per_hit_effect=per_hit_effect
    
    def excute(self, context):
        if random.randint(1,100)<=self.accuracy:
            hits=random.randint(self.min_hits,self.max_hits)
            print(f"its a multi-hit move")

            for _ in range(hits):
                if context.defender.is_fainted:
                    break
                self.per_hit_effect.apply(context)
        else:
            print(f"...but it missed")

class Move:
    def __init__(self,name:str,element:Element,attempt:IAttempt):
        self.name=name
        self.element=element
        self.attempt=attempt

    def excute(self,context)->None:
        self.attempt.excute(context)