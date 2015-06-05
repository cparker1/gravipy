__author__ = 'charles.andrew.parker@gmail.com'

from utils import clean_filename
import logging
import time
import os
import numpy as np
from camera import Camera
import game
import simulation
import simfileplayer
import cPickle as pickle
import copy
import zipfile

logs_directory = '/tmp/gravipy_log' or os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log')

if os.path.exists(logs_directory) and not os.path.isdir(logs_directory):
    raise IOError("Log directory choice is not a real directory!")
current_log = os.path.join(logs_directory, clean_filename(time.asctime()))
os.makedirs(current_log, mode=0744)


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler(os.path.join(current_log, 'run.log'))
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
ch.setFormatter(formatter)

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)
log.addHandler(ch)

game.log.addHandler(ch)
game.log.addHandler(fh)

game.body.log.addHandler(ch)
game.body.log.addHandler(fh)


Camera.log.addHandler(ch)
Camera.log.addHandler(fh)

config = {
    "dimensions": (1680, 900),
    "gravitational_constant": 0.5,
    "draw_sphere_of_influence": False,
    "num_bg_stars": 250,
    "enable_movement": False}

planets1 = simulation.generate_star_system_config("Sol", (0, 0, 0), 5)
planets2 = simulation.generate_star_system_config("Sol", (-15000, 1000, 0), 5)
planets3 = simulation.generate_star_system_config("Sol", (8000, -10000, 4000), 5)
planets4 = simulation.generate_star_system_config("Sol", (-8000, 1000, 8000), 5)
planets5 = simulation.generate_star_system_config("Sol", (4000, -4000, 4000), 1)

planets = planets1 + planets2 + planets3 + planets4 + planets5
# planets = planets1

sim = simulation.GravitySimulation(planets, config)
cam = Camera(np.array([0, -5000, 300]), config["dimensions"])

if __name__ == "__main__":
    if os.path.isdir("recordings") is False:
        os.mkdir("recordings")

    with open("recordings/test2.rec", "w") as f:
        states = [None for _ in range(0, 1500)]
        for _ in range(0, 1500):
            if _ % 15 == 0:
                print _ / 15
            sim.update_planets(1)
            states[_] = pickle.dumps(sim.get_planet_simulation_state())
        pickle.dump(states, f)

    with open("recordings/test2.rec", "r") as f:
        states = pickle.load(f)

    with zipfile.ZipFile('recordings/test2.zip', 'w', zipfile.ZIP_DEFLATED) as myzip:
        myzip.write('recordings/test2.rec')


