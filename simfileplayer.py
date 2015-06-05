__author__ = 'charles.andrew.parker@gmail.com'


from objects import body
import logging
import itertools
from coordinate import Coordinate
from camera import Camera
import pygame
import simulation
import cPickle as pickle

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class FrameWarp(object):

    arrow_size = 64, 64
    framewarp_arrow_color = 96, 64, 96
    framewarp_image_bgcolor = 255, 196, 255

    arrow_image = pygame.Surface(arrow_size)
    arrow_image.fill(framewarp_image_bgcolor)
    pygame.draw.polygon(arrow_image, framewarp_arrow_color, [(8, 8), (56, 32), (8, 56)])

    pause_image = pygame.Surface(arrow_size)
    pause_image.fill(framewarp_image_bgcolor)
    pygame.draw.rect(pause_image, framewarp_arrow_color, (8, 8, 56, 34))

    @classmethod
    def build_timewarp_image(cls, timewarp_num):
        if timewarp_num == 0:
            return FrameWarp.pause_image

        else:
            image_size = timewarp_num * cls.arrow_size[0], cls.arrow_size[1]
            image = pygame.Surface(image_size)
            for n in range(timewarp_num):
                image.blit(cls.arrow_image, (n * cls.arrow_size[0], 0))

            return image

    def __init__(self, frames, max_timewarp):
        self.frames = [pickle.loads(f) for f in frames]
        self.num_frames = len(frames)
        self.frame_index = 0
        self.timewarp_value = 1
        self.max_timewarp = max_timewarp
        self.images = [FrameWarp.build_timewarp_image(n) for n in range(0, max_timewarp)]

    def get_timewarp_image(self):
        return self.images[self.timewarp_value]

    def increment_timewarp(self):
        if self.timewarp_value < self.max_timewarp - 1:
            self.timewarp_value += 1

    def decrement_timewarp(self):
        if -1 * self.max_timewarp + 1 < self.timewarp_value:
            self.timewarp_value -= 1

    def next_frame(self):
        self.frame_index += self.timewarp_value
        if self.frame_index < 0:
            self.frame_index += self.num_frames
        elif self.num_frames <= self.frame_index:
            self.frame_index -= self.num_frames

    def get_frame(self):
        self.next_frame()
        return self.frames[self.frame_index]


class GravitySimulationPlayer(object):
    def __init__(self, savefile_path, sim_config):
        with open(savefile_path, "r") as f:
            frames = pickle.load(f)
            self.time_handler = FrameWarp(frames, 8)

        self.sim = simulation.GravitySimulation(planet_configs=None, sim_config=sim_config)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.sim.reset()

            if event.key == pygame.K_p:
                self.time_handler.timewarp_value = 0

            if event.key == pygame.K_COMMA:
                self.time_handler.decrement_timewarp()

            if event.key == pygame.K_PERIOD:
                self.time_handler.increment_timewarp()

        if event.type == Camera.CAMERAEVENT and event.movement == Camera.CAMERAMOVED:
            self.sim.clear_planet_trails()

    def draw_background(self, surface, camera):
        log.info("Drawing Background")
        self.sim.draw_background(surface, camera)

    def draw_planets(self, surface, camera):
        log.info("Drawing planets")
        self.sim.draw_planets(surface, camera)

    def draw_timewarp_image(self, surface):
        log.info("Drawing timewarp image")
        surface.blit(self.time_handler.get_timewarp_image(), (100, 800))

    def step(self):
        planets = self.time_handler.get_frame()
        self.sim.set_planets(planets)

    def draw(self, surface, camera):
        self.draw_background(surface, camera)
        self.draw_planets(surface, camera)
        self.draw_timewarp_image(surface)

