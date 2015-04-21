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


pygame.init()

# planets1 = game.generate_star_system_config("Sol", (1000, 1000), 1)
# planets2 = game.generate_star_system_config("Sol", (-8000, 1000), 2)
# planets3 = game.generate_star_system_config("Sol", (8000, 10000), 1)
# planets = planets1 + planets2 + planets3

planets = game.generate_star_system_config("Sol", (0, 0), 8)

sim = game.GravitySim(planets, config)
screen = pygame.display.set_mode(config["dimensions"])
clock = pygame.time.Clock()
clock.tick()
clock.get_time()

surface = pygame.Surface(config["dimensions"])

calculate_offset = False
permanent_offset = np.array([1680/2, 720/2])
temp_offset = np.array([0,0])
scale = 0.1
timestep = 1
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

        if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN:
            # scrolling up
            if event.button == 4:
                scale += 0.001
                timestep -= 0.1
            # scrolling down
            elif event.button == 5:
                scale -= 0.001
                timestep += 0.1

        if event.type == pygame.MOUSEBUTTONDOWN:
            calculate_offset = True
            start_mouse_down_offset = np.array(pygame.mouse.get_pos())

        if event.type == pygame.MOUSEBUTTONUP:
            calculate_offset = False
            permanent_offset += temp_offset
            temp_offset = np.array([0,0])

        if event.type == pygame.K_KP_PLUS:
            scale += 0.05

        if event.type == pygame.K_KP_MINUS:
            scale -= 0.05

    if calculate_offset is True:
        temp_offset = np.array(pygame.mouse.get_pos()) - start_mouse_down_offset

    screen.fill(black)
    surface.fill(black)
    sim.update_planets(timestep)
    sim.draw_planets(screen, permanent_offset + temp_offset, scale)
    pygame.display.flip()
    clock.tick(120)
