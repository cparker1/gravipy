__author__ = 'charles.andrew.parker@gmail.com'

from coordinate import Coordinate
from objects import body
import random
import logging
import numpy as np
import math
import itertools

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def generate_planet(base_star, radius, name):
    offset = base_star["pos"]
    angle = random.randrange(0, 360)
    angle = math.pi * angle / 180.0
    pos = np.array(offset) + radius * np.array([math.cos(angle),
                                                math.sin(angle),
                                                random.uniform(-math.pi / 24, math.pi / 24)])
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
    speed = 1.0 * math.sqrt(0.5 * parent["mass"] / dist)
    return speed * vel_norm


def generate_background_star_field(num_stars):
    star_list = []
    for _ in range(num_stars):
        args = {"pos": Coordinate.get_random_coordinate(10000000.0),
                "vel": Coordinate.get_empty_coord(),
                "radius": random.randrange(1, 3)}
        star_list.append(args)
    return star_list


class GravitySimulation(object):
    def __init__(self, planet_configs, sim_config):
        self.sim_config = sim_config
        self.planet_configs = planet_configs
        self.planets = set()
        self.background_stars = set()
        self.create_simulation(self.planet_configs, self.sim_config)
        self.planet_distances = {}
        self.update_distance_and_vectors_for_planets()
        self.BIG_G = sim_config["gravitational_constant"]
        self.DRAW_SOI = sim_config["draw_sphere_of_influence"]

    def set_planets(self, planets):
        """
        Provides an interface for saved data.  If you don't want
        to run the sumulation, just set the planets to a saved
        set
        """
        self.planets = planets

    def get_planet_simulation_state(self):
        return [p for p in self.planets]

    def create_simulation(self, planet_configs, sim_config):
        log.info("Creating simulation.")
        self.planets = set()
        if planet_configs is not None:
            for p in planet_configs:
                self.planets.add(body.Planet(**p))

        for s in generate_background_star_field(sim_config["num_bg_stars"]):
            self.background_stars.add(body.BackgroundStar(**s))

    def reset(self):
        self.create_simulation(self.planet_configs, self.sim_config)

    def update_distance_and_vectors_for_planets(self):
        """
        builds a dict of radius vectors between planets
        of format:
        {
            (p1, p2): distance from p1 to p2,
            (p1, p3): distance from p1 to p3,
            ...
            (p3, p4): distance from p3 to p4, etc.
        }
        """
        self.planet_distances = {}
        for a, b in itertools.combinations(self.planets, 2):
            dist, vect = Coordinate.get_distance_and_radius_vector(a.coord, b.coord)
            self.planet_distances[(a, b)] = (dist, vect)

    def update_positions(self, dt):
        for p in self.planets:
            p.coord.update_vel(dt)

    def update_velocities(self, dt):
        for p in self.planets:
            p.coord.update_pos(dt)

    def update_acceleration(self):
        dead_planets = set()
        for p in self.planets:
            p.coord.zero_acc()

        for planets, distances in self.planet_distances.items():
                a, b = planets
                dist, vect = distances

                acc = self.BIG_G * a.mass * b.mass * vect / dist ** 3

                a.coord.update_acc(acc/a.mass)
                b.coord.update_acc(-acc/b.mass)

                if dist < body.Planet.get_collision_distance(a, b):
                    dead_planets.add(body.Planet.handle_collision(a, b))

        self.delete_dead_planets(dead_planets)

    def delete_dead_planets(self, dead_planets):
        for p in dead_planets:
            self.planets.remove(p)

    def handle_event(self, event):
        pass

    def update_planets(self, dt):
        log.info("UPDATING DISTANCES AND RADIUS VECTORS")
        self.update_distance_and_vectors_for_planets()
        log.info("UPDATING FORCES/ACCELERATION")
        self.update_acceleration()
        log.info("UPDATING VELOCITIES")
        self.update_velocities(dt)
        log.info("UPDATING POSITIONS")
        self.update_positions(dt)

    def draw_background(self, surface, camera):
        log.info("Drawing Background")
        surface.fill((0, 0, 0))
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
            p.draw(surface, camera)

            if self.DRAW_SOI is True:
                p.draw_sphere_of_influence(surface, camera)

    def clear_planet_trails(self):
        for p in self.planets:
            p.clear_planet_trail()
