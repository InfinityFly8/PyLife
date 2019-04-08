import os
import sys
import json
import curses
import scene
from base_substances import Empty, Barrier
from extends import Alga, Vegetarian, Scavenger, Predator


class Main:
    def __init__(self):
        class_list = (Barrier, Vegetarian, Scavenger, Predator, Alga, Empty)
        try:
            file = open("settings.json")
            self.settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = {
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
            open("settings.json", "w").write(json.dumps(self.settings, indent=4))
        
            
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
        for cl in class_list:
            cl_val = self.settings["objects"].get(cl.__name__)
            if cl_val is not None:
                self.objects.append((cl, cl_val))
            elif cl.__name__ == self.settings["default"]:
                self.default = cl
                
    def clear(self):
        if sys.platform == "win32":
            print(os.popen("cls").read())
        else:
            print(os.popen("clear").read()) 
    
    def change_settings(self):
        print("Non implemented...")
    
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
            
            sc = scene.Scene(self.debugger, self.table_len, *self.objects, default=self.default)
            rend = scene.Render(0.03, sc)
            curses.wrapper(rend.run_scene)
            
            self.clear()
            print("#" * 20, "\n" * 2)
            print("Steps: ", str(sc.scene["count"]))
            print("All died. Game Over...")
            print("\n", "#" * 20)
        input("Press enter to exit...")

        
if __name__ == "__main__":
    main = Main()
    main.main()