import math
import random
from collections import deque
import curses
# from colorama import init, Fore
# init()


class Empty:
    """Base class. Empty cell.
    """
    symbol = " "
    color = curses.COLOR_WHITE
    style = 0
    life = 0
    hunger = 0
    speed = 0
    count = 0
    
    def __init__(self, scene, pos, debugger, parent=None):
        self.scene = scene
        self.x = pos[0]
        self.y = pos[1]
        self.id = random.randint(10000, 999999999)
        if debugger is not None and bool(self):
            self.debugger = debugger
            self.debugger.write(self, "birth", str(parent))
        else:
            self.debugger = None
        
    def set_current_position(self):
        for i, row in enumerate(self.scene["place"]):
             for k, column in enumerate(row):
                  if column is self:
                      self.x = i
                      self.y = k
                      return None
        
    def __bool__(self):
        return False
    
    def tact(self):
        self.count += 1


class Food(Empty):
    symbol = "^"
    eat_cost = 5
    def tact(self):
        self.count += 1
        if self.count > 60:
            obj = Empty(self.scene, (self.x, self.y), self.debugger)
            self.scene["place"][self.x][self.y] = obj
    def die(self, *args):
        pass


class Barrier(Empty):
    """Base class for non-movable cells like a stones and animals.
    """
    symbol = "#"
    color = curses.COLOR_BLACK
    style = curses.A_DIM

class Life(Empty):
    count = 0
    repr_time = 10
    def __init__(self, *c):
        raise TypeError()
    
    def get_distance(self, tar1, tar2):
        return math.sqrt(abs(tar1[0] - tar2[0]) ** 2 + abs(tar1[0] - tar2[1]) ** 2) 
        
    def die(self, repr_eat=None, id=None):
        
        if repr_eat is None: 
            die_mod = "died"
            died = self.died
        elif repr_eat:
            die_mod = "repr"
            died = Empty
        else:
            die_mod = "destr"
            died = Empty
        class_name = self.__class__.__name__
        # self.set_current_position()
        # print(self.id, self.__class__.__name__, self.scene["place"][self.x][self.y] is self, )
        self.scene["place"][self.x][self.y] = died(self.scene, (self.x, self.y), self.debugger)
        if self.debugger is not None:
            self.debugger.write(self, die_mod, str(id))
        
    def search(self, *search_classes, target=None):
        """*search_types: set a parent classes here""" 
        
        queue = deque()
        report = {}
        
        if target is None:
            curr_pos = "%s_%s" % (self.x, self.y)
            stages = 8 ** (self.speed if self.speed > 0 else 1)
        else:
            curr_pos = "%s_%s" % (target[0], target[1])
            stages = 8
        visited = {}
        
        # report keys and values init
        for search_class in search_classes: 
            report[search_class.__name__] = []
        #start queue  
        queue += self.scene["graph"][curr_pos]
        
        while queue:
            inx = queue.popleft()
            exp = "%s_%s" % (inx[0], inx[1])
            if exp in visited.values():
                continue
            
            elem = self.scene["place"][inx[0]][inx[1]]
            
            for src_class in search_classes:
                if isinstance(elem, src_class):
                    report[src_class.__name__].append(inx)
                    # break
                    
            stages -= 1
            if stages:
                nlist = self.scene["graph"][exp]
                for n in nlist:
                    visited[n] = exp       
        return report
        
    
    def reproduct(self, tar1, tar2):
        if tar1 == tar2:
            return False
           
        if self.count >= self.repr_time:
            target1 = self.scene["place"][tar1[0]][tar1[1]]
            target2 = self.scene["place"][tar2[0]][tar2[1]]
            # plants can reproduct to food zone
            if isinstance(self, Food):
                rules = (Barrier,)
            else:
                rules = (Barrier, Food)
            if  not isinstance(target1, rules) \
            and not isinstance(target2, rules):
                sfclass = self.__class__
                self.scene["place"][tar1[0]][tar1[1]] = sfclass(self.scene, (tar1[0], tar1[1]), self.debugger, self.id)
                self.scene["place"][tar2[0]][tar2[1]] = sfclass(self.scene, (tar2[0], tar2[1]), self.debugger, self.id)
                self.die(True)
                
                
class Animal(Barrier):
    """Parent class Animal. Can to move
    """
    # life preferences
    count = 0
    life = 100
    hunger = 0
    move_cost = 2
    hunger_mult = 3
    hunger_tact = 2
    hunger_stat = ((70, -3), (40, -1), (0, 1),)
    count_stop = 200
    repr_time = 10
    repr_stat = (70, 30)
    
    #other functions preferences
    died = Food
    can_eat = Food
    strength = 10
    symbol = "$"
    color = curses.COLOR_CYAN
    style = 0
    speed = 1
    under = None
    report = None
    eat_cost = 20
    
    def __bool__(self):
        return True   
            
    def move(self, tar_x, tar_y):
        if tar_x == self.x and tar_y == self.y:
            return
        target = self.scene["place"][tar_x][tar_y]
        if not isinstance(target, (Barrier,)):
            temp = self.under if self.under is not None else Empty(self.scene, (self.x, self.y), self.debugger, self.id)
            self.under = target
            self.scene["place"][tar_x][tar_y] = self
            self.scene["place"][self.x][self.y] = temp
            self.x = tar_x
            self.y = tar_y
            self.hunger += self.move_cost
            # print(self.id, self.__class__.__name__, self.scene["place"][tar_x][tar_y] is self)
            if self.debugger is not None:
                self.debugger.write(self, "move", "%s_%s" % (tar_x, tar_y))

    def eat(self, tar_x, tar_y):
        if tar_x == self.x and tar_y == self.y:
            return
        target = self.scene["place"][tar_x][tar_y]
        
        if isinstance(target, self.can_eat) \
        and not isinstance(target, self.__class__):
            
            self.hunger -= target.eat_cost * 1.5
            self.life += target.eat_cost
            
            self.scene["place"][tar_x][tar_y] = Empty(self.scene, (tar_x, tar_y), self.debugger)
            target.die(False, self.id)
            self.move(tar_x, tar_y)
            
            if self.debugger is not None:
                self.debugger.write(self, "eat", target.id)
            return True
        return False
        
    def hunger_manage(self):
        self.count += 1
        # if self.under:
        #     self.under.tact()
        if self.count % self.hunger_mult == 0:
            self.hunger += self.hunger_tact
        
        for limit, cost in self.hunger_stat:
            if self.hunger >= limit:
                self.life += cost
                break
        
        if self.life < 1 or self.count > self.count_stop:
            self.die()
        if self.life > 100:
            self.life = 100
        elif self.life < -1:
            self.life = -1
        if self.hunger > 100:
            self.hunger = 100
            
    def tact(self):
        self.life()
        self.hunger += random.randint(1, 5)
        if self.hunger > 60:
            self.life -= 4
        if self.life < 1:
            self.die()
            
    def attack(self, tar_x, tar_y):
        target = self.scene["place"][tar_x][tar_y]
        target.life -= self.strength
        if self.debugger:
            self.debugger.write(self, "attack", target.id)
        target.attacked(self.id)
        
    def attacked(self, id):
        if self.debugger:
            self.debugger.write(self, "strike", id)
        if self.life < 1:
            self.die()