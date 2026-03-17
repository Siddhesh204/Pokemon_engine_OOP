import os ,csv,ctypes,random,json
from enum import Enum ,auto
from abc import ABC ,abstractmethod 

class Weather(Enum):
    CLEAR = 0
    SUN = 1
    RAIN = 2
    SANDSTORM = 3
    HAIL = 4
    
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
    GROUND=auto()
    ROCK=auto()
    DARK=auto()
    FAIRY=auto()
    STEEL=auto()
    FLYING=auto()
    ICE=auto()
    DRAGON=auto()

class Status(Enum):
    NONE = 0
    BURN = 1
    POISON = 2
    PARALYZE = 3
    SLEEP = 4
    FREEZE = 5

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

def load_type_chart()->dict:
    chart={}
    engine_dir = os.path.dirname(os.path.dirname(__file__))
    filepath=os.path.join(engine_dir,'data','TYPE_CHART.json') 

    with open(filepath,'r')as file:
        raw_data=json.load(file)

    for attacker_str,defenders in raw_data.items():
        try:
            attacker_enum=Element[attacker_str]
            chart[attacker_enum]={}

            for defender_str,multiplier in defenders.items():
                defender_enum=Element[defender_str]
                chart[attacker_enum][defender_enum]=float(multiplier)
        except KeyError as e:
            print(f"Warning :Skipping unknown Element {e}in json")
    return chart 

    # with open(filepath,mode='r') as file:
        #disregard csv way :/
        # reader=csv.DictReader(file)
        # for row in reader:
        #     attacker_str=row['Attacker']
        #     attacker_enum=Element[attacker_str]
        #     chart[attacker_enum]={}

        #     for defender_str,multiplier in row.items():
        #         if defender_str != 'Attacker':
        #             defender_enum=Element[defender_str]
        #         chart[attacker_enum][defender_enum]= float(multiplier)
    # return chart
TYPE_CHART=load_type_chart()
def get_type_multiplier(attack_element:Element,defender_elements:list[Element])->float:
    multiplier=1.0
    if attack_element in TYPE_CHART:
        for def_element in defender_elements:
            multiplier*=TYPE_CHART[attack_element].get(def_element,1.0)
    return multiplier