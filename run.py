__author__ = 'charles.andrew.parker@gmail.com'

import pygame
import game
import sys
import logging
import time
import os

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

game.log.addHandler(ch)
game.objects.body.log.addHandler(ch)
game.objects.coordinate.log.addHandler(ch)

game.log.addHandler(fh)
game.objects.body.log.addHandler(fh)
game.objects.coordinate.log.addHandler(fh)

config = {
    "dimensions": (640, 800),
    "gravitational_constant": 0.1,
    "draw_sphere_of_influence": True
}

black = 0, 0, 0

VALUE = 0.02

sun = {"name": "SUN",
       "mass": 100.0,
       "pos": (300, 300),
       "vel": (0.0, 0.0),
       "radius": 20,
       "color": (120, 130, 140)}

p1 = {"name": "Ee-Arth",
      "mass": 10.0,
      "pos": (400, 600),
      "vel": (VALUE, -VALUE),
      "color": (120, 130, 140)}

p2 = {"name": "Frieza Planet 419",
      "mass": 10.0,
      "pos": (100, 400),
      "vel": (VALUE, VALUE),
      "color": (100, 130, 180)}

p3 = {"name": "Vegeta",
      "mass": 10.0,
      "pos": (200, 200),
      "vel": (-VALUE, VALUE),
      "color": (100, 130, 180)}

p4 = {"name": "Namek",
      "mass": 10.0,
      "pos": (400, 200),
      "vel": (-VALUE, -VALUE),
      "color": (100, 130, 180)}

pygame.init()
planets = [sun, p1, p2, p3, p4]
sim = game.GravitySim(planets, config)
screen = pygame.display.set_mode(config["dimensions"])
clock = pygame.time.Clock()
clock.tick()
print clock.get_time()

surface = pygame.Surface(config["dimensions"])


while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(black)
    sim.update_planets(clock.get_time())
    sim.draw_planets(screen)
    pygame.display.flip()
    clock.tick(240)
