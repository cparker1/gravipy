__author__ = 'charles.andrew.parker@gmail.com'

import pygame
import game
import sys
import logging
import time
import os
import numpy as np

if not os.path.isdir('./log'):
    os.mkdir("./log")
log_dir = "./log/{}".format(time.asctime().replace(' ', '').replace(':', ''))
if not os.path.isdir(log_dir):
    os.mkdir(log_dir)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler("{}/run.log".format(log_dir))
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


config = {
    "dimensions": (1680, 900),
    "gravitational_constant": 0.1,
    "draw_sphere_of_influence": True
}

black = 0, 0, 0

VALUE = 0.02

sun = {"name": "SUN",
       "mass": 10000000.0,
       "pos": (1680/2, 900/2),
       "vel": (0.0, 0.0),
       "radius": 20,
       "color": (255, 255, 240)}

p1 = {"name": "Ee-Arth",
      "mass": 1000.0,
      "pos": (1580, 450),
      "vel": (VALUE, -VALUE),
      "color": (39, 227, 224)}

p2 = {"name": "Frieza Planet 419",
      "mass": 1000.0,
      "pos": (100, 450),
      "vel": (VALUE, VALUE),
      "color": (100, 130, 180)}

p3 = {"name": "Vegeta",
      "mass": 2000.0,
      "pos": (-2000, 200),
      "vel": (-VALUE, VALUE),
      "color": (100, 130, 180)}

p4 = {"name": "Namek",
      "mass": 5000.0,
      "pos": (1500, 700),
      "vel": (-VALUE, -VALUE),
      "color": (0, 255, 128)}

pygame.init()
game.get_velocity_for_circular_orbit(sun, p1)
game.get_velocity_for_circular_orbit(sun, p2)
game.get_velocity_for_circular_orbit(sun, p3)
game.get_velocity_for_circular_orbit(sun, p4)

planets = [sun, p1, p2, p3, p4]
sim = game.GravitySim(planets, config)
screen = pygame.display.set_mode(config["dimensions"])
clock = pygame.time.Clock()
clock.tick()
print clock.get_time()

surface = pygame.Surface(config["dimensions"])

calculate_offset = False
permanent_offset = np.array([0, 0])
temp_offset = np.array([0,0])
start_mouse_down_offset = np.array([0, 0])

while 1:
    for event in pygame.event.get():
        log.debug("Handling pygame event {}".format(event.type))
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYDOWN:
            log.debug("Handling KEYDOWN {}".format(event.key))
            if event.key == pygame.K_SPACE:
                log.info("Restarting simulation")
                sim.reset()

        if event.type == pygame.MOUSEBUTTONDOWN:
            calculate_offset = True
            start_mouse_down_offset = np.array(pygame.mouse.get_pos())

        if event.type == pygame.MOUSEBUTTONUP:
            calculate_offset = False
            permanent_offset += temp_offset
            temp_offset = np.array([0,0])

    if calculate_offset is True:
        temp_offset = np.array(pygame.mouse.get_pos()) - start_mouse_down_offset

    screen.fill(black)
    sim.update_planets(clock.get_time())
    sim.draw_planets(screen, permanent_offset + temp_offset)
    pygame.display.flip()
    clock.tick(120)
    print pygame.mouse.get_pos()

