__author__ = 'charles.andrew.parker@gmail.com'


from objects import body
import logging
import itertools
from coordinate import Coordinate
from camera import Camera
import pygame
import simulation
import time

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TimeWarp(object):

    arrow_size = 64, 64
    timewarp_arrow_color = 96, 64, 96
    timewarp_image_bgcolor = 255, 196, 255

    arrow_image = pygame.Surface(arrow_size)
    arrow_image.fill(timewarp_image_bgcolor)
    pygame.draw.polygon(arrow_image, timewarp_arrow_color, [(8, 8), (56, 32), (8, 56)])

    pause_image = pygame.Surface(arrow_size)
    pause_image.fill(timewarp_image_bgcolor)
    pygame.draw.rect(pause_image, timewarp_arrow_color, (8, 8, 56, 34))

    @classmethod
    def build_timewarp_image(cls, timewarp_num):
        if timewarp_num == 0:
            return TimeWarp.pause_image

        else:
            image_size = timewarp_num * cls.arrow_size[0], cls.arrow_size[1]
            image = pygame.Surface(image_size)
            for n in range(timewarp_num):
                image.blit(cls.arrow_image, (n * cls.arrow_size[0], 0))

            return image

    def __init__(self, base_timestep, max_timewarp):
        self.timewarp_value = 1
        self.timestep = base_timestep
        self.max_timewarp = max_timewarp
        self.images = [TimeWarp.build_timewarp_image(n) for n in range(0, max_timewarp)]
        self.paused = False

    def get_timewarp_image(self):
        return self.images[self.timewarp_value]

    def increment_timewarp(self):
        if self.timewarp_value < self.max_timewarp - 1:
            self.timewarp_value += 1
            self.set_pause(pause=False)

    def decrement_timewarp(self):
        if 1 < self.timewarp_value:
            self.timewarp_value -= 1
        else:
            self.set_pause(pause=True)

    def set_pause(self, pause=True, toggle=False):
        if toggle is True:
            self.paused = not self.paused
        else:
            self.paused = pause

    def get_timestep(self):
        return self.timestep ** self.timewarp_value


class GravitySimulationSystem(object):
    def __init__(self, planet_configs, sim_config):
        self.sim = simulation.GravitySimulation(planet_configs, sim_config)
        self.time_handler = TimeWarp(1.3, 8)
        self.saved_background = pygame.Surface(sim_config["dimensions"])
        self.update_background = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.sim.reset()

            if event.key == pygame.K_p:
                self.time_handler.set_pause(toggle=True)

            if event.key == pygame.K_COMMA:
                self.time_handler.decrement_timewarp()

            if event.key == pygame.K_PERIOD:
                self.time_handler.increment_timewarp()

        if event.type == Camera.CAMERAEVENT and event.movement == Camera.CAMERAMOVED:
            self.sim.clear_planet_trails()

        if event.type == Camera.CAMERAEVENT and event.movement == Camera.CAMERATURNED:
            self.update_background = True

    def draw_background(self, surface, camera):
        log.info("Drawing Background")
        if self.update_background:
            self.sim.draw_background(surface, camera)
            self.saved_background.blit(surface, (0, 0))
            self.update_background = False
        else:
            surface.blit(self.saved_background, (0, 0))

    def draw_planets(self, surface, camera):
        log.info("Drawing planets")
        self.sim.draw_planets(surface, camera)

    def draw_timewarp_image(self, surface):
        log.info("Drawing timewarp image")
        surface.blit(self.time_handler.get_timewarp_image(), (100, 800))

    def step(self):
        if self.time_handler.paused is False:
            self.sim.update_planets(self.time_handler.get_timestep())

    def draw(self, surface, camera):
        self.draw_background(surface, camera)
        self.draw_planets(surface, camera)
        self.draw_timewarp_image(surface)

