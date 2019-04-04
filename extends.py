import random
import math
from colorama import init, Fore
from base_substances import Empty, Barrier, Food, Life, Animal
init()


class Meat(Food):
	pass

class Fresh(Meat):
    count = 0
    eat_cost = 30
    symbol = "@"
    color = Fore.LIGHTRED_EX
    

class Carrion(Meat):
	count = 0
	eat_cost = 7
	symbol = "%"
	color = Fore.RED

class Alga(Life, Food):
    speed = 0
    died = Empty
    eat_cost = 12
    repr_time = 6
    symbol = '+'
    count = 0
    color = Fore.GREEN

    def __init__(self, scene, pos, debugger=None, parent=None):
        Food.__init__(self, scene, pos, debugger, parent)
    def tact(self):
            
        # counter
        self.count += 1
        report = self.search(Empty)
        
        # reproduct
        if report["Empty"] and self.count >= self.repr_time:
            rand1 = random.choice(report["Empty"])
            rand2 = random.choice(report["Empty"])
            self.reproduct(rand1, rand2)


class Vegetarian(Animal, Life):
    life = 80
    hunger = 40
    hunger_mult = 2
    hunger_tact = 3
    hunger_stat = ((75, -4), (40, -2), (0, 2))
    count_stop = 200
    
    strength = 5
    eat_cost = 25
    repr_time = 21
    speed = 2
    died = Fresh
    can_eat = Alga
    color = Fore.CYAN
    
    def __init__(self, scene, pos, debug=None, parent=None):
        Animal.__init__(self, scene, pos, debug, parent)
    
    def tact(self):
        report = self.search(self.can_eat, Empty, Predator, Scavenger)
        self.hunger_manage()
        if report["Predator"] or report["Scavenger"] and self.life < 60:
            for_attack = report["Predator"] + report["Scavenger"]
            for target in for_attack:
                if not random.randint(0, 3):
                    self.attack(*target)
                
        if self.hunger > 50 and self.life < 70 and \
        report[self.can_eat.__name__] and \
        self.count % self.hunger_mult == 0:
            for_eat = random.choice(report[self.can_eat.__name__])
            self.eat(*for_eat)
        
        elif report["Empty"]:
            if self.life >= 65 and self.hunger <= 70 and self.count >= self.repr_time:
                rand1 = random.choice(report["Empty"])
                rand2 = random.choice(report["Empty"])
                self.reproduct(rand1, rand2)
            self.move(*random.choice(report["Empty"]))
        else:
            self.hunger += 10


class Scavenger(Animal, Life):
    hunger_mult = 4
    hunger_tact = 3
    hunger_stat = ((75, -2), (0, 1))
    count_stop = 300
    
    speed = 4
    eat_cost = 20
    repr_time = 27
    symbol = "&"
    strength = 12
    can_eat = Meat
    died = Carrion
    color = Fore.LIGHTMAGENTA_EX
    
    def __init__(self, scene, pos, debug=None, parent=None):
        Animal.__init__(self, scene, pos, debug, parent)
    
    def tact(self):
        self.hunger_manage()
        report = self.search(self.can_eat, Empty, Vegetarian, Predator, Alga)
        
        if self.hunger > 45 and self.life < 70:
            if report["Vegetarian"] or report["Predator"] * 2:
                for for_attack in report["Vegetarian"] + report["Predator"]:
                    self.attack(*for_attack)
                    
            if report[self.can_eat.__name__]:
                for_eat = random.choice(report[self.can_eat.__name__])
                self.eat(*for_eat)
                self.move(*for_eat)
            else:
                self.move(*random.choice(report["Empty"]))
                
        elif report["Predator"] and report["Empty"] and not random.randint(0,4):
            min = (0, (self.x, self.y))
            for empty in report["Empty"]:
                res = self.get_distance((self.x, self.y), empty)
                if res > min[0]:
                    min = (res, empty)
            if min[0] > 0:
                self.move(*min[1])
            
        elif report["Empty"]:
            if self.life >= 75 and self.hunger <= 55 \
            and self.count >= self.repr_time and not random.randint(0,2):
                rand1 = random.choice(report["Empty"])
                rand2 = random.choice(report["Empty"])
                self.reproduct(rand1, rand2)
                
            if report["Alga"] and not random.randint(0,3):
                self.move(*random.choice(report["Alga"]))
            else:
                self.move(*random.choice(report["Empty"]))
        else:
            self.hunger += 6


class Predator (Animal, Life):
    hunger_mult = 3
    hunger_tact = 2
    hunger_stat = ((60, -3),(0, 1))
    count_stop = 400
    
    life = 70
    hunger = 30
    speed = 3
    repr_time = 40
    symbol = "A"
    strength = 15
    can_eat = Animal
    died = Fresh
    color = Fore.LIGHTYELLOW_EX
    
    def __init__(self, scene, pos, debug, parent=None):
        Animal.__init__(self, scene, pos, debug, parent)
    
    def tact(self):
        self.hunger_manage()
        report = self.search(self.can_eat, Empty, Animal, Alga)
        
        if self.hunger > 55 and self.life < 65 and self.count % self.hunger_mult in [0, 1]:
            if report[self.can_eat.__name__]:
                for_eat = random.choice(report[self.can_eat.__name__])
                self.eat(*for_eat)
                self.move(*for_eat)
        
        elif report["Empty"]:
            if self.life >= 75 and self.hunger <= 50 and self.count >= self.repr_time:
                rand1 = random.choice(report["Empty"])
                rand2 = random.choice(report["Empty"])
                self.reproduct(rand1, rand2)
            if report["Alga"] and not random.randint(0,3):
                self.move(*random.choice(report["Alga"]))
            else:
                self.move(*random.choice(report["Empty"]))
        else:
            self.hunger += 5

    
    
    