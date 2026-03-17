import random
import ctypes
import os
from enum import Enum ,auto
from abc import ABC ,abstractmethod 

class Element(Enum):
    NORMAL=auto()
    FIRE=auto()
    WATER=auto()
    GRASS=auto()
    ELECTRIC=auto()
    FIGHTING=auto()
    GHOST=auto()
    PSYCHIC=auto()
    POISON=auto()
    BUG=auto()

class Status(Enum):
    NONE=auto()
    PARALYZED=auto()
    BURNED=auto()
    POISONED=auto()
    FREEZE=auto()
    SLEEP=auto()

class Category(Enum):
    PHYSICAL=auto()
    SPECIAL=auto()
    STATUS=auto()

def Load_math_Engine():
    lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','c.math','engine_math.so'))

    try:
        engine = ctypes.CDLL(lib_path)

        engine.calculate_damage.argtypes =[ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_double]
        engine.calculate_damage.restype = ctypes.c_double
        return engine
    except OSError:
        print(f"Warning :C math Engine not found at {lib_path}.Please compile it ")
        return None
math_engine =Load_math_Engine()