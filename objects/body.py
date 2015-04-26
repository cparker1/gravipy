__author__ = 'charles.andrew.parker@gmail.com'

import pygame
import numpy as np
import logging
from coordinate import Coordinate
import itertools

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Trail(object):
    def __init__(self, max_len_of_trail, snapshot_interval):
        self.counter = itertools.count()
        self.interval = snapshot_interval
        self.trail = []
        self.max_len_trail = max_len_of_trail

    def add_position_and_radius_to_trail(self, pos, radius):
        if self.counter.next() % self.interval == 0:
            self.trail.append((pos, radius))
        if self.max_len_trail < len(self.trail):
            self.trail.pop(0)

    def get_position_and_radius_trail(self):
        if len(self.trail) < self.max_len_trail:
            return None
        else:
            return self.trail

    def clear_trail(self):
        self.trail = []

class Planet(object):
    """
    Base class for all large objects with
    gravitational mass!
    """

    @classmethod
    def handle_collision(cls, a, b):
        if a.mass <= b.mass:
            b.collide(a)
            return a
        else:
            a.collide(b)
            return b

    @classmethod
    def get_collision_distance(cls, a, b):
        return a.get_radius() + b.get_radius()

    def __init__(self, **kwargs):
        self.args = kwargs
        self.name = kwargs["name"]
        self.coord = Coordinate(kwargs["pos"], kwargs["vel"])
        self.mass = kwargs["mass"]
        self.color = kwargs["color"]
        self.border = 0
        self.kinetic_energy = self.get_kinetic_energy()
        self.potential_energy = 0
        self.radius = 0
        self.get_radius(update=True)
        self.sphere_of_influence = 0
        self.get_sphere_of_influence(update=True)
        self.trail = Trail(40, 1)

    def get_distance_to_other_body(self, other):
        dist, vect = Coordinate.get_distance_and_radius_vector(self.coord, other.coord)
        return dist, vect

    def get_kinetic_energy(self):
        return 0.5 * self.mass * self.coord.get_speed() ** 2

    def get_potential_energy(self):
        return self.potential_energy

    def get_momentum(self):
        return self.mass * self.coord.vel

    def get_sphere_of_influence(self, update=False):
        if update is True:
            self.sphere_of_influence = (np.math.e ** 1) * np.math.sqrt(self.mass)
        return self.sphere_of_influence

    def get_radius(self, update=False):
        if update is True:
            self.radius = 2.0 * self.mass ** (1.0/3.0)
        return self.radius

    def collide(self, planet):
        self.coord.vel = (self.get_momentum() + planet.get_momentum())/(self.mass + planet.mass)
        self.mass += planet.mass
        self.get_radius(update=True)
        self.get_sphere_of_influence(update=True)

    def check_if_visible(self, apparent_radius):
        if apparent_radius < 1:
            return False
        else:
            return True

    def clear_planet_trail(self):
        self.trail.clear_trail()

    def draw(self, surface, camera):
        r, pos = camera.get_apparent_radius_and_draw_pos(self.coord, self.get_radius())
        if self.check_if_visible(r) is False:
            log.debug("Planet {} is too small to draw at this scale.".format(self.name))
            return False

        elif pos is not None:
            self.trail.add_position_and_radius_to_trail(pos, r)
            log.debug("Drawing circle: coord={}; radius={}; border={}".format(self.coord.pos,
                                                                              self.get_radius(),
                                                                              self.border))
            pygame.draw.circle(surface,
                               self.color,
                               pos,
                               np.round(r).astype(int),
                               self.border)
            trail = self.trail.get_position_and_radius_trail()
            if trail is not None:
                plist, _ = zip(*self.trail.get_position_and_radius_trail())
                pygame.draw.lines(surface,
                                  self.color,
                                  False,
                                  plist,
                                  1)

            return True

    def draw_sphere_of_influence(self, surface, camera):
        r, pos = camera.get_apparent_radius_and_draw_pos(self.coord, self.get_sphere_of_influence())
        if self.check_if_visible(r) is True and pos is not None:
            pygame.draw.circle(surface,
                               self.color,
                               pos,
                               np.round(r).astype(int),
                               1)


class BackgroundStar(object):

    def __init__(self, **kwargs):
        self.coord = Coordinate(kwargs["pos"], kwargs["vel"])
        self.radius = kwargs["radius"]
        self.color = (255, 255, 255)

    def draw(self, surface, camera):
        _, pos = camera.get_apparent_radius_and_draw_pos(self.coord, self.radius)
        if pos is not None:
            log.debug("Drawing background star: coord={}; radius={};".format(self.coord.pos, self.radius))
            pygame.draw.circle(surface,
                               self.color,
                               pos,
                               np.round(self.radius).astype(int),
                               0)
