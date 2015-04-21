__author__ = 'charles.andrew.parker@gmail.com'


from objects import body
import logging
import numpy as np
import itertools
from coordinate import Coordinate

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def get_velocity_for_circular_orbit(parent, orbiter):
    radius = np.array(orbiter["pos"]) - np.array(parent["pos"])
    dist = np.linalg.norm(radius)

    vel_norm = np.cross(radius / dist, np.array([0, 0, 1]))
    speed = 1.3 * np.math.sqrt(0.005 * parent["mass"] / dist)
    orbiter["vel"] = speed * vel_norm[:2]
    log.info("Setting {} circular orbit velocity to {}".format(orbiter["name"], orbiter["vel"]))


class GravitySim(object):
    BIG_G = 0.005
    draw_soi = False

    def __init__(self, planet_configs, config):
        self.planet_configs = planet_configs
        self.planets = set()
        self.total_energy = 0
        self.create_simulation(self.planet_configs)
        GravitySim.big_g = config["gravitational_constant"]
        GravitySim.draw_soi = config["draw_sphere_of_influence"]

    def create_simulation(self, planet_configs):
        log.info("Creating simulation.")
        self.planets = set()
        for p in planet_configs:
            self.planets.add(body.Planet(**p))

    def reset(self):
        self.create_simulation(self.planet_configs)

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
            dist, vect = a.get_distance_to_other_body(b)
            force = cls.BIG_G * a.mass * b.mass * vect / dist ** 3

            mutual_potential = -cls.BIG_G * a.mass * b.mass / dist
            a.potential_energy += mutual_potential / a.mass
            b.potential_energy += mutual_potential / b.mass

            a.coord.update_vel(force / a.mass, dt)
            b.coord.update_vel(-force / b.mass, dt)

            if dist < body.Planet.get_collision_distance(a, b):
                dead_planets.add(body.Planet.handle_collision(a, b))

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

    def update_planets(self, dt):
        log.info("UPDATING POSITIONS")
        self.update_positions(dt, self.planets)
        log.info("UPDATING VELOCITY AND POTENTIAL ENERGY")
        self.update_velocity_and_potential(dt, self.planets)

    def draw_planets(self, surface, offset):
        log.info("Drawing planets")
        for p in self.planets:
            log.debug("P {}".format(p.coord.pos))
            p.draw(surface, offset)

        if GravitySim.draw_soi is True:
            for p in self.planets:
                p.draw_sphere_of_influence(surface, offset)

