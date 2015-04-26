__author__ = 'charles.andrew.parker@gmail.com'

import pygame
import game
import sys
import logging
import time
import os
import numpy as np
import camera
from utils import clean_filename

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

camera.log.addHandler(ch)
camera.log.addHandler(fh)

config = {
    "dimensions": (1680, 900),
    "gravitational_constant": 0.1,
    "draw_sphere_of_influence": False,
    "num_bg_stars": 150,
    "enable_movement": False}

black = 0, 0, 0


pygame.init()

planets1 = game.generate_star_system_config("Sol", (1000, 1000, -4000), 1)
planets2 = game.generate_star_system_config("Sol", (-15000, 1000, 0), 2)
planets3 = game.generate_star_system_config("Sol", (8000, -10000, 4000), 1)
planets4 = game.generate_star_system_config("Sol", (-8000, 1000, 8000), 1)
planets5 = game.generate_star_system_config("Sol", (4000, -4000, 4000), 1)
planets = planets1 + planets2 + planets3 + planets4 + planets5

planets2 = game.generate_star_system_config("Sol", (10, 10, 0), 5)

sim = game.GravitySimulation(planets2, config)
cam = camera.Camera(np.array([0, -5000, 300]), config["dimensions"])
screen = pygame.display.set_mode(config["dimensions"])
background = pygame.Surface(config["dimensions"])

background.fill(black)
sim.draw_background(background, cam)

pause = True
textcolor = 128, 128, 64
font = pygame.font.Font(None, 48)
pause_image = font.render("PRESS 'P' '<' or '>' TO UNPAUSE", True, textcolor, black)


timestep = 1
timewarp_value = 1
max_timewarp = 8
arrow_size = 64, 64
timewarp_arrow_color = 96, 64, 96
timewarp_image_bgcolor = 255, 196, 255
arrow_image = pygame.Surface(arrow_size)
arrow_image.fill(timewarp_image_bgcolor)
pygame.draw.polygon(arrow_image, timewarp_arrow_color, [(8, 8), (56, 32), (8, 56)])

def get_timewarp_image():
    image_size = timewarp_value * arrow_size[0], arrow_size[1]
    image = pygame.Surface(image_size)

    for n in range(timewarp_value):
        image.blit(arrow_image, (n*arrow_size[0], 0))

    return image


timewarp_image = get_timewarp_image()


pygame.mixer.init()
music = pygame.mixer.Sound(file="./sound/spheric_lounge_books_of_mantra.ogg")
music.play()


pause = True
textcolor = 128, 128, 64
font = pygame.font.Font(None, 48)
pause_image = font.render("PRESS 'P' '<' or '>' TO UNPAUSE", True, textcolor, black)

clock = pygame.time.Clock()
clock.tick()
clock.get_time()


while 1:
    for event in pygame.event.get():
        log.debug("Handling pygame event {}".format(event.type))
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                log.info("Restarting simulation")
                sim.reset()
                cam.reset()

            if event.key == pygame.K_p:
                pause = not pause

            if event.key == pygame.K_COMMA:
                if 0 < timewarp_value:
                    timewarp_value -= 1
                    pause = False
                    timewarp_image = get_timewarp_image()
                if timewarp_value == 0:
                    pause = True

            if event.key == pygame.K_PERIOD:
                if timewarp_value < max_timewarp:
                    timewarp_value += 1
                    pause = False
                    timewarp_image = get_timewarp_image()

            if event.key == pygame.K_F12:
                pygame.display.toggle_fullscreen()

        sim.handle_event(event)

        cam.handle_event(event)
        if cam.need_upgrade_background() is True:
            background.fill(black)
            sim.draw_background(background, cam)


    screen.fill(black)
    screen.blit(background, (0, 0))

    if pause is False:
        sim.update_planets(2 ** (timewarp_value - 1))
        screen.blit(timewarp_image, (100, 800))
    else:
        screen.blit(pause_image, (100, 100))

    sim.update_sim(cam)
    sim.draw_planets(screen, cam)
    pygame.display.flip()

    clock.tick(30)
