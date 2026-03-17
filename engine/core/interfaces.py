from utils.common import ABC,abstractmethod 

class IEffect(ABC):
    @abstractmethod
    def apply(self,battle_context) -> None:
        "mutates the battle state"
        pass

class IAttempt(ABC):
    @abstractmethod
    def excute(self,battle_context) ->None:
        "Executes the attempt (rolls the accurarcy,applise the effect etc)"
        pass