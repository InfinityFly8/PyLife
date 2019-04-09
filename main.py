import os
import sys
import json
import curses
import scene
from base_substances import Empty, Barrier
from extends import Alga, Vegetarian, Scavenger, Predator


class Main:
    def __init__(self):
        self.class_list = (Barrier, Vegetarian, Scavenger, Predator, Alga, Empty)
        self.default_settings = {
              "debug": True,
              "speed": 0.01,
              "table_len": [30, 30],
              "default": "Empty",
              "objects": {
                "Barrier": 1200,
                "Vegetarian": 300,
                "Scavenger": 260,
                "Predator": 150,
                "Alga": 1600,
              }
            }
        try:
            file = open("settings.json")
            self.settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = self.default_settings
            open("settings.json", "w").write(json.dumps(self.settings, indent=4))
        self.load_settings()
        
    def load_settings(self):
        self.speed = float(self.settings["speed"])
        self.table_len = int(self.settings["table_len"][0]), int(self.settings["table_len"][1])
        
        # debugger enable or disable
        if self.settings["debug"]:
            self.debugger = scene.Debugger
        else:
            self.debugger = None
        
        # objects chances
        self.objects = []
        self.default = None
        for cl in self.class_list:
            cl_val = self.settings["objects"].get(cl.__name__)
            if cl_val is not None:
                self.objects.append((cl, cl_val))
            elif cl.__name__ == self.settings["default"]:
                self.default = cl
    
    def change_settings(self):
        print("\n  { Settings changing }  \n")     
        
        settings = ["speed", "table_len", "debug"] # self.settings.keys()
        
        while True:
            for i, sett in enumerate(settings):
                print("{0}:  {1}".format(i + 1, sett))
                
            choosed = (int(input("Select an item to change: ")) - 1)
            if choosed > 0 or choosed < len(settings):
                choosed_elem = settings[choosed]
            else:
                print("Out of range.")
                continue
            
            if choosed_elem == "speed":
                try:
                    value = float(input("speed (Set the new value. Recommended less than 0.3): "))
                    self.settings["speed"] = value
                except ValueError:
                    print("Value most be a float or integer. Like this: 0.02")
                    continue
                    
            elif choosed_elem == "table_len":
                try:
                    width = int(input("table width (Set the table width. Recommended roughly 30): "))
                    height = int(input("table height (Set the table height. Recommended roughly 30): "))
                    self.settings["table_len"] = [width, height]
                except ValueError:
                    print("Value most be an integer. Like this: 30")
                    continue
                    
            elif choosed_elem == "debug":
                val = input("Do you need to enable the debug logging? [y/n]: ")[0].lower()
                if val == "y":
                    self.settings["debug"] = True
                elif val == "n":
                    self.settings["debug"] = False
                else:
                    print("You most write y or n.")
                    continue
            else:
                pass
                    
            print("\n1: Write the changes to settings file")
            print("2: Set the default settings")
            print("3: Back to simulation")
            print("4: Back to settings")
            while True:
                comm = input(">>> ")
                if comm == "1":
                    open("settings.json", "w").write(json.dumps(self.settings, indent=4))
                elif comm == "2":
                    self.settings = self.default_settings
                elif comm == "3":
                    self.load_settings()
                    return None
                elif comm == "4":
                    break
                else:
                    print("Unknown command")
            
            
    def clear(self):
        if sys.platform == "win32":
            print(os.popen("cls").read())
        else:
            print(os.popen("clear").read()) 
    
    def main(self):
        self.clear() 
        print("Hello! It's a bacteriums simulator.")
        print("Please, enlarge your window.")
        while True:
            comm1 = input("\nDo you want to change a settings? [y/n]: ")[0].lower()
            if comm1 == "y":
                self.change_settings()
            else:
                break
        comm2 = input("Start the simulation? [y/n]: ")[0].lower()
        if comm2 == "y":
            try:
                sc = scene.Scene(self.debugger, self.table_len, *self.objects, default=self.default)
                rend = scene.Render(self.speed, sc)
                curses.wrapper(rend.run_scene)
                self.clear()
                print("#" * 20, "\n")
                print("Steps: ", str(sc.scene["count"]))
                print("All died. Game Over...")
                print("\n", "#" * 20, sep="")
            except curses.error:
                print("\n\nError:")
                print("Your window too small for this table size: {0[0]}x{0[1]}".format(self.table_len))
                print("Please, enlarge your window or lessen the table in settings")
            except KeyboardInterrupt:
                print("\n\nSimulation stopped\n")
        input("Press enter to exit...")

        
if __name__ == "__main__":
    main = Main()
    main.main()