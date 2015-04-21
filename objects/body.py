__author__ = 'charles.andrew.parker@gmail.com'

import pygame
import numpy as np
import logging
from coordinate import Coordinate
import itertools

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


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
            self.radius = 0.5 * self.mass ** (1.0/3.0)
        return self.radius

    def collide(self, planet):
        self.coord.vel = (self.get_momentum() + planet.get_momentum())/(self.mass + planet.mass)
        self.mass += planet.mass
        self.get_radius(update=True)
        self.get_sphere_of_influence(update=True)

    def draw(self, surface, offset):
        log.debug("Drawing circle: coord={}; radius={}; border={}".format(self.coord.pos,
                                                                          np.round(self.get_radius()).astype(int),
                                                                          self.border))
        if 0 != np.round(self.get_radius()).astype(int):
            pygame.draw.circle(surface,
                               self.color,
                               np.round(self.coord.pos).astype(int) + offset,
                               np.round(self.get_radius()).astype(int),
                               self.border)

    def draw_sphere_of_influence(self, surface, offset):
        if 0.0 != np.round(self.get_sphere_of_influence()).astype(int):
            pygame.draw.circle(surface,
                               self.color,
                               np.round(self.coord.pos).astype(int) + offset,
                               np.round(self.get_sphere_of_influence()).astype(int),
                               1)
