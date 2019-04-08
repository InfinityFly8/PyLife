import os
import random
import time
import sys
import curses

class Debugger:
    def __init__(self):
        self.file = open("debuglog", "w")
        self.logstr = "{0} {1} {2} {3} {4} count: {5} life: {6} hunger: {7} pos: {8[0]} {8[1]} real:{9}\n"
        
    def write(self, elem, commit, target):
        gl_count = (str(elem.scene["count"]) + " - ").ljust(5)
        id = str(elem.id).ljust(11)
        kind = elem.__class__.__name__.ljust(10)
        make = commit.ljust(5).rjust(6)
        if target:
            target = " >>> " + str(target).ljust(9)
        else:
            target = " " * 14
        count = str(elem.count).ljust(4)
        life = str(elem.life).ljust(4)
        hunger = str(elem.hunger).ljust(4)
        pos = (elem.x, elem.y)
        # if commit != "birth":
        try:
            pos_id = elem.scene["place"][elem.x][elem.y].id
        except:
            pos_id = "None"
        if pos_id == elem.id:
            real = "self"
        else:
            real = pos_id
        # else:
        #     real = ""
        exp = self.logstr.format(gl_count, id, kind, make, target, count, life, hunger, pos, real)
        self.file.write(exp)


class Scene:
    def __init__(self, debugger, length, *elem_types, default):
        """ __init__: place table creating. 
        required arguments:
            debug: most be True or False
            length: tuple or list of integers. Table rows and columns count. Like a (150, 200)
            *elem_types: requred classes list and his chance form 10000. Like a (Predator, 100), (Barrier, 2000)
                         class
            default: named argument. Default type in table.
        """
        self.debugger = debugger() or None
        # place create
        self.scene = {}
        place = []
        graph = {}
        self.scene["place"] = place
        self.scene["graph"] = graph
        self.scene["count"] = 0
        for row in range(length[0]):
            place.append([None] * length[1])
            for column in range(length[1]):
                new_obj = None
                for elem in elem_types:
                    if elem[1] >= random.randint(1, 10000):
                        new_obj = elem[0](self.scene, (row, column), self.debugger)
                        break
                else:
                    new_obj = default(self.scene, (row, column), self.debugger)
                place[row][column] = new_obj
        
        # place graph create
        for curr_i, row in enumerate(place):
            # zone selection
            # x axis length
            if curr_i == 0:
                x = curr_i, curr_i + 1
            elif curr_i == len(place) - 1:
                x = curr_i - 1, curr_i
            else:
                x = curr_i - 1, curr_i + 1
            for curr_k, column in enumerate(row):
                # y axis length
                if curr_k == 0:
                    y = curr_k, curr_k + 1
                elif curr_k == len(place[curr_i]) - 1:
                    y = curr_k - 1, curr_k
                else:
                    y = curr_k - 1, curr_k + 1
                
                # neighbours check
                cell = "%d_%d" % (curr_i, curr_k)
                graph[cell] = []
                for zone_i, zone_row in enumerate(place[x[0]:x[1] + 1]):
                    zone_i += x[0]
                    for zone_k, zone_column in enumerate(zone_row[y[0]:y[1] + 1]):
                        zone_k += y[0]
                        if place[zone_i][zone_k] is not place[curr_i][curr_k]:
                            graph[cell].append((zone_i, zone_k))
        
    def life_in_place_check(self):
        results = []
        for row in self.scene["place"]:
            results.append(any(row))
        return any(results)
    
    def tact(self):
        self.scene["count"] += 1
        visited = []
        for i, row in enumerate(self.scene["place"]):
            for k, column in enumerate(row):
                if column not in visited:
                    # column.x = i
                    # column.y = k
                    column.tact()
                    visited.append(column)


class Render:
    colors = {}
    
    def __init__(self, render_speed, scene):
        self.scene_obj = scene
        self.render_speed = render_speed
    
    def render(self, stdscr):
        # size = stdscr.getmaxyx()
        bl = "||"
        bt = "=" * (len(self.scene_obj.scene["place"][0]) * 2 + len(bl) * 2)
        rows_start = 1 # ((size[0] - len(bt)) // 2 - 3)
        cols = 4
        rows = rows_start
        
        stdscr.clear()
        stdscr.addstr(1, len(bt) // 2 - 5 + rows_start, "{Step: " + str(self.scene_obj.scene["count"]) +  "}")
        stdscr.addstr(3, rows_start, bt)
        
        for row in self.scene_obj.scene["place"]:
            stdscr.addstr(cols, rows, bl)
            rows = rows_start + len(bl)
            for elem in row:
                if elem.symbol == " ":
                    color_index = 0
                elif str(elem.color) in self.colors:
                    color_index = self.colors[str(elem.color)]
                else:
                    curses.init_pair(elem.color + 7, elem.color, curses.COLOR_BLACK)
                    self.colors[str(elem.color)] = elem.color + 7
                    color_index = elem.color + 7
                    
                stdscr.addstr(cols, rows, elem.symbol, curses.color_pair(color_index) | elem.style)
                stdscr.addstr(cols + 1, rows, " ")
                rows += 2
                
            stdscr.addstr(cols, rows, bl)
            cols += 1
            rows = rows_start
        stdscr.addstr(cols, rows, bt)
        stdscr.refresh()
        
    def run_scene(self, stdscr):
        curses.curs_set(False)
        
        while self.scene_obj.life_in_place_check():
            self.scene_obj.tact()
            self.render(stdscr)
            time.sleep(self.render_speed)
