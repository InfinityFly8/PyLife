import curses
import scene
from base_substances import Empty, Barrier
from extends import Alga, Vegetarian, Scavenger, Predator


table_len = 30, 30
objects = [
    (Barrier, 1200),
    (Vegetarian, 300),
    (Scavenger, 260),
    (Predator, 150), 
    (Alga, 1600)
]
sc = scene.Scene(scene.Debugger, table_len, *objects, default=Empty)
rend = scene.Render(0.03, sc)
curses.wrapper(rend.run_scene)