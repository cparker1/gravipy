__author__ = 'charles.andrew.parker@gmail.com'


from objects import body
import logging
import numpy as np
import itertools
from coordinate import Coordinate
import random

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def generate_planet(base_star, radius, name):
    offset = base_star["pos"]
    angle = random.randrange(0, 360)
    angle = np.math.pi * angle / 180.0
    pos = np.array(offset) + radius * np.array([np.math.cos(angle), np.math.sin(angle), 0])
    vel = base_star["vel"] + get_velocity_for_circular_orbit(base_star, pos)
    mass = random.randrange(10000, 300000)

    def rand_clr():
        return random.randrange(0, 255)

    color = (rand_clr(), rand_clr(), rand_clr())

    return {"name": name,
            "pos": pos,
            "mass": mass,
            "color": color,
            "vel": vel}


def generate_star_system_config(base_name, offset, num_planets):
    star = {
        "name": base_name,
        "mass": random.randrange(1000000, 8000000),
        "pos": offset,
        "color": (255, 255, 190),
        "vel": (0, 0, 0)}

    planet_list = [star]
    for r in range(num_planets):
        new_planet = generate_planet(star,
                                     1000 * (r + 1),
                                     "{}-{}".format(star["name"], r+1))
        planet_list.append(new_planet)

    return planet_list


def get_velocity_for_circular_orbit(parent, pos):
    radius = np.array(pos) - np.array(parent["pos"])
    dist = np.linalg.norm(radius)

    vel_norm = np.cross(radius / dist, np.array([0, 0, 1]))
    speed = 1.3 * np.math.sqrt(0.005 * parent["mass"] / dist)
    return speed * vel_norm


def generate_background_star_field(num_stars):
    star_list = []
    for _ in range(num_stars):
        args = {"pos": Coordinate.get_random_coordinate(100000, 200000),
                "vel": Coordinate.get_empty_coord(),
                "radius": random.randrange(1, 3)}
        star_list.append(args)
    return star_list

class GravitySim(object):
    BIG_G = 0.005
    draw_soi = False

    def __init__(self, planet_configs, sim_config):
        self.sim_config = sim_config
        self.planet_configs = planet_configs
        self.planets = set()
        self.background_stars = set()
        self.total_energy = 0
        self.create_simulation(self.planet_configs, self.sim_config)
        GravitySim.big_g = sim_config["gravitational_constant"]
        GravitySim.draw_soi = sim_config["draw_sphere_of_influence"]

    def create_simulation(self, planet_configs, sim_config):
        log.info("Creating simulation.")
        self.planets = set()
        for p in planet_configs:
            self.planets.add(body.Planet(**p))

        for s in generate_background_star_field(sim_config["num_bg_stars"]):
            self.background_stars.add(body.BackgroundStar(**s))

    def reset(self):
        self.create_simulation(self.planet_configs, self.sim_config)

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

    def draw_background(self, surface, camera):
        log.info("Drawing Background")
        for p in self.background_stars:
            log.debug("P {}".format(p.coord.pos))
            p.draw(surface, camera)

    def draw_planets(self, surface, camera):
        log.info("Drawing planets")

        # build ordered list
        ordered_list = []
        for p in self.planets:
            dist, _ = Coordinate.get_distance_and_radius_vector(camera.coord, p.coord)
            ordered_list.append((p, dist))

        for p, d in sorted(ordered_list, key=lambda ele: ele[1], reverse=True):
            log.warning("D {}".format(d))
            p.draw(surface, camera)

            if GravitySim.draw_soi is True:
                p.draw_sphere_of_influence(surface, camera)

