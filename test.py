import scene
from base_substances import Empty, Barrier
from extends import Alga, Vegetarian, Scavenger, Predator

sc = scene.Scene(scene.Debugger, (25,25), (Barrier, 1200), (Vegetarian, 300), (Scavenger, 260), (Predator, 150), (Alga, 1600), default=Empty)
# sc = scene.Scene((25,25), (Vegetarian, 3000), (Predator, 3000), default=Empty)
# graph = sc.scene["graph"]
# print("")
# print("0_0:  ", graph["0_0"])
# print("1_1:  ", graph["1_1"])
# print("21_19: ", graph["21_19"])

# print ("29_29: ", graph["29_29"])
# print(sc)

sc.run_scene(0.1)