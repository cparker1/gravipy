__author__ = 'charles.andrew.parker@gmail.com'

import pygame
import game
import sys
import logging
import time
import os
import numpy as np
from camera import Camera
from utils import clean_filename
import simulation

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

black = 0, 0, 0

pygame.init()

planets1 = simulation.generate_star_system_config("Sol", (0, 0, 0), 5)
# planets2 = simulation.generate_star_system_config("Sol", (-15000, 1000, 0), 2)
# planets3 = simulation.generate_star_system_config("Sol", (8000, -10000, 4000), 1)
# planets4 = simulation.generate_star_system_config("Sol", (-8000, 1000, 8000), 3)
# planets5 = simulation.generate_star_system_config("Sol", (4000, -4000, 4000), 1)
# planets = planets1 + planets2 + planets3 + planets4 + planets5
planets = planets1

planets2 = simulation.generate_star_system_config("Sol", (10, 10, 0), 5)

sim = game.GravitySimulationSystem(planets, config)
cam = Camera(np.array([0, -5000, 300]), config["dimensions"])
screen = pygame.display.set_mode(config["dimensions"])
background = pygame.Surface(config["dimensions"])

background.fill(black)
sim.draw_background(background, cam)

pygame.mixer.init()
music = pygame.mixer.Sound("./sound/spheric_lounge_books_of_mantra.ogg")
music.play()


clock = pygame.time.Clock()
clock.tick()
clock.get_time()

pygame.key.set_repeat(10, 10)

while 1:
    screen.fill(black)

    for event in pygame.event.get():
        log.debug("Handling pygame event {}".format(event.type))
        if event.type == pygame.QUIT:
            sys.exit()

        cam.handle_event(event)
        if event.type == Camera.CAMERAEVENT and event.movement == Camera.CAMERATURNED:
            sim.draw_background(background, cam)

        sim.handle_event(event)


    screen.blit(background, (0, 0))

    sim.step()
    sim.draw(screen, cam)
    pygame.display.flip()

    clock.tick(30)
