__author__ = 'charles.andrew.parker@gmail.com'

import pygame
import game
import sys
import logging
import time
import os
import numpy as np
import camera

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

camera.log.addHandler(ch)
camera.log.addHandler(fh)

config = {
    "dimensions": (1680, 900),
    "gravitational_constant": 0.1,
    "draw_sphere_of_influence": False,
    "num_bg_stars": 150}

black = 0, 0, 0


pygame.init()

# planets1 = game.generate_star_system_config("Sol", (1000, 1000, 0), 1)
# planets2 = game.generate_star_system_config("Sol", (-8000, 1000, 0), 2)
# planets3 = game.generate_star_system_config("Sol", (8000, 10000, 0), 1)
# planets = planets1 + planets2 + planets3

planets = game.generate_star_system_config("Sol", (10, 10, 0), 5)

sim = game.GravitySim(planets, config)
screen = pygame.display.set_mode(config["dimensions"])
background = pygame.Surface(config["dimensions"])
clock = pygame.time.Clock()
clock.tick()
clock.get_time()

cam = camera.Camera(np.array([2000, 0, 300]), config["dimensions"])
timestep = 5

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
                cam.reset()

        cam.handle_event(event)
        if cam.need_upgrade_background() is True:
            background.fill(black)
            sim.draw_background(background, cam)

    cam.update()
    sim.update_planets(timestep)

    screen.fill(black)
    screen.blit(background, (0, 0))
    sim.draw_planets(screen, cam)
    pygame.display.flip()

    clock.tick(30)
