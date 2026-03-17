import random 
from core.pokemon import Pokemon

class BattleContext:

    def __init__(self,attacker:Pokemon,defender:Pokemon):
        self.attacker=attacker
        self.defender=defender

        self.weather="CLEAR"
        self.terrain="NORMAL"

class BattleEngine:
    def __init__(self,Player1:Pokemon,Player2:Pokemon):
        self.p1=Player1
        self.p2=Player2
        self.turn_count=1

    def determine_first_attacker(self)-> tuple[Pokemon,Pokemon]:
        if self.p1.speed > self.p2.speed:
            return self.p1,self.p2
        elif self.p2.speed > self.p1.speed:
            return self.p2,self.p1
        else :
            print(f"speed tie")
            return (self.p1,self.p2) if random.choice([True,False]) else (self.p2,self.p1)
        
    def excute_turn(self,p1_move,p2_move):
        print(f"\n>{'='*10} TURN {self.turn_count}{'='*10}")

        first,second,=self.determine_first_attacker()

        first_move =p1_move if first ==self.p1 else p2_move
        second_move =p2_move if first ==self.p2 else p1_move

        if not first.is_fainted:
            print(f"\n>{first.name} used{first_move.name}!")
            context = BattleContext(attacker=first,defender=second)
            first_move.excute(context)

        if not second.is_fainted:
            print(f"\n>{second.name} used{second_move.name}!")
            context = BattleContext(attacker=second,defender=first)
            second_move.excute(context)

        self.turn_count+=1
    
    def is_battle_over(self)->bool:
        return self.p1.is_fainted or self.p2.is_fainted
    
    def get_winner(self)->str:
        if self.p1.is_fainted and self.p2.is_fainted:
            return "It's a draw"
        elif self.p1.is_fainted:
            return f"{self.p2.name}wins!"
        elif self.p2.is_fainted:
            return f"{self.p1.name}wins!"
        return "battle is ongoing..."
    