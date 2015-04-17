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

    # [N*m/kg**2]
    BIG_G = 0.05
    planets = []

    @classmethod
    def calculate_initial_potential(cls):
        for a, b in itertools.permutations(cls.planets, 2):
            dist, vect = Coordinate.get_distance_and_radius_vector(a.coord, b.coord)
            a.potential_energy += -cls.BIG_G * b.mass / dist
            b.potential_energy += -cls.BIG_G * a.mass / dist

        return cls.get_total_potential_energy()

    @classmethod
    def get_total_potential_energy(cls):
        ret_val = 0
        for p in cls.planets:
            ret_val += p.get_potential_energy()
        return ret_val

    @classmethod
    def get_total_kinetic_energy(cls):
        ret_val = 0
        for p in cls.planets:
            ret_val += p.get_kinetic_energy()
        return ret_val

    @classmethod
    def update_position(cls, dt):
        for p in cls.planets:
            p.coord.update_pos(dt)

    @classmethod
    def update_velocity_and_potential(cls, dt):
        for p in cls.planets:
            p.potential_energy = 0
        for a, b in itertools.permutations(cls.planets, 2):
            dist, vect = Coordinate.get_distance_and_radius_vector(a.coord, b.coord)
            force = cls.BIG_G * a.mass * b.mass * vect / dist ** 3

            a.coord.update_vel(force / a.mass, dt)
            b.coord.update_vel(-force / b.mass, dt)

            a.potential_energy += -cls.BIG_G * b.mass / dist
            b.potential_energy += -cls.BIG_G * a.mass / dist

            if dist < 1.5 * (a.radius + b.radius):
                a.coord.vel *= -1
                b.coord.vel *= -1

    @classmethod
    def scale_kinetic_energy_to_total_energy(cls, energy):
        new_pe = cls.get_total_potential_energy()
        new_ke = energy - new_pe
        ke_scaler = new_ke / cls.get_total_kinetic_energy()
        log.info("Current total energy: {}".format(energy))
        log.info("PE: {}; KE: {}; scale: {}".format(new_pe, new_ke, ke_scaler))
        for p in cls.planets:
            p.scale_speed_to_kinetic_energy(ke_scaler)
        log.info("New total energy: {}".format(new_pe + cls.get_total_kinetic_energy()))

    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.coord = Coordinate(kwargs["pos"], kwargs["vel"])
        self.mass = kwargs["mass"]
        self.radius = kwargs["radius"]
        self.color = kwargs["color"]
        self.border = 1
        self.kinetic_energy = self.get_kinetic_energy()
        self.potential_energy = 0
        Planet.planets.append(self)

    def get_kinetic_energy(self):
        return 0.5 * self.mass * self.coord.get_speed() ** 2

    def get_potential_energy(self):
        return self.potential_energy

    def scale_speed_to_kinetic_energy(self, ratio):
        log.info("{}: Scaling speed with ratio {}".format(self.name, ratio))
        log.info("{}: Current vel is {}".format(self.name, self.coord.vel))
        self.coord.vel *= ratio
        log.info("{}: New vel is {}".format(self.name, self.coord.vel))

    def draw(self, surface):
        log.debug("Drawing circle: coord={}; border={}".format(self.coord.pos, self.border))
        return pygame.draw.circle(surface,
                                  self.color,
                                  np.round(self.coord.pos).astype(int),
                                  self.radius,
                                  self.border)
