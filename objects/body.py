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
    BIG_G = 0.00005

    @classmethod
    def calculate_initial_potential(cls, planets):
        for a, b in itertools.permutations(planets, 2):
            dist, vect = Coordinate.get_distance_and_radius_vector(a.coord, b.coord)
            a.potential_energy += -cls.BIG_G * b.mass / dist
            b.potential_energy += -cls.BIG_G * a.mass / dist

        return cls.get_total_potential_energy(planets)

    @classmethod
    def get_total_potential_energy(cls, planets):
        ret_val = 0
        for p in planets:
            ret_val += p.get_potential_energy()
        return ret_val

    @classmethod
    def get_total_kinetic_energy(cls, planets):
        ret_val = 0
        for p in planets:
            ret_val += p.get_kinetic_energy()
        return ret_val

    @classmethod
    def update_positions(cls, dt, planets):
        for p in planets:
            p.coord.update_pos(dt)

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

    @classmethod
    def update_velocity_and_potential(cls, dt, planets):
        dead_planets = set()
        initial_kinetic = cls.get_total_kinetic_energy(planets)
        # reset potential energy.  it needs to be recalculated
        for p in planets:
            p.potential_energy = 0

        # apply gravity due to each body.  handle colisions
        # (collision handling needs dist, so we recycle it here)
        # TODO: things like distance should be handled in self.planets
        # TODO: so that it only has to be calculated once.
        for a, b in itertools.permutations(planets, 2):
            dist, vect = Coordinate.get_distance_and_radius_vector(a.coord, b.coord)
            force = cls.BIG_G * a.mass * b.mass * vect / dist ** 3

            mutual_potential = -cls.BIG_G * a.mass * b.mass / dist
            a.potential_energy += mutual_potential / a.mass
            b.potential_energy += mutual_potential / b.mass

            if b.check_if_planet_in_influence(dist, a):
                a.coord.update_vel(force / a.mass, dt)
            if a.check_if_planet_in_influence(dist, b):
                b.coord.update_vel(-force / b.mass, dt)

            if dist < cls.get_collision_distance(a, b):
                dead_planets.add(cls.handle_collision(a, b))

        if 0 < len(dead_planets):
            cls.delete_dead_planets(planets, dead_planets)

        new_potential_energy = cls.get_total_potential_energy(planets)

        return initial_kinetic, new_potential_energy

    @classmethod
    def delete_dead_planets(cls, planets, dead_planets):
        for p in dead_planets:
            log.warning("REMOVING PLANET {}".format(p.name))
            planets.remove(p)

    @classmethod
    def scale_kinetic_energy_to_total_energy(cls, energy, planets):
        new_pe = cls.get_total_potential_energy(planets)
        new_ke = energy - new_pe
        ke_scaler = new_ke / cls.get_total_kinetic_energy(planets)
        log.info("Current total energy: {}".format(energy))
        log.info("PE: {}; KE: {}; scale: {}".format(new_pe, new_ke, ke_scaler))
        for p in planets:
            p.scale_speed_to_kinetic_energy(ke_scaler)
        log.info("New total energy: {}".format(new_pe + cls.get_total_kinetic_energy(planets)))

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

    def get_kinetic_energy(self):
        return 0.5 * self.mass * self.coord.get_speed() ** 2

    def get_potential_energy(self):
        return self.potential_energy

    def get_momentum(self):
        return self.mass * self.coord.vel

    def get_sphere_of_influence(self, update=False):
        if update is True:
            self.sphere_of_influence = (np.math.e ** (1.0/2.0)) * np.math.sqrt(Planet.BIG_G * self.mass)
        return self.sphere_of_influence

    def get_radius(self, update=False):
        if update is True:
            self.radius = 1.0 * self.mass ** (1.0/3.0)
        return self.radius

    def check_if_planet_in_influence(self, dist, planet):
        return True
        # TODO Do I need to be doing this?
        if dist - planet.get_radius() < self.get_sphere_of_influence():
            return True
        else:
            return False

    def collide(self, planet):
        self.coord.vel = (self.get_momentum() + planet.get_momentum())/(self.mass + planet.mass)
        self.mass += planet.mass
        self.get_radius(update=True)
        self.get_sphere_of_influence(update=True)

    def scale_speed_to_kinetic_energy(self, ratio):
        log.info("{}: Scaling speed with ratio {}".format(self.name, ratio))
        log.info("{}: Current vel is {}".format(self.name, self.coord.vel))
        self.coord.vel *= ratio
        log.info("{}: New vel is {}".format(self.name, self.coord.vel))

    def draw(self, surface):
        log.debug("Drawing circle: coord={}; radius={}; border={}".format(self.coord.pos,
                                                                          np.round(self.get_radius()).astype(int),
                                                                          self.border))
        if 0 != np.round(self.get_radius()).astype(int):
            pygame.draw.circle(surface,
                               self.color,
                               np.round(self.coord.pos).astype(int),
                               np.round(self.get_radius()).astype(int),
                               self.border)

    def draw_sphere_of_influence(self, surface):
        if 0.0 != np.round(self.get_sphere_of_influence()).astype(int):
            pygame.draw.circle(surface,
                               self.color,
                               np.round(self.coord.pos).astype(int),
                               np.round(self.get_sphere_of_influence()).astype(int),
                               1)
