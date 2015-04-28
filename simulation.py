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
    speed = 1.3 * math.sqrt(0.5 * parent["mass"] / dist)
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
    BIG_G = 0.5
    DRAW_SOI = False

    def __init__(self, planet_configs, sim_config):
        self.sim_config = sim_config
        self.planet_configs = planet_configs
        self.planets = set()
        self.background_stars = set()
        self.total_energy = 0
        self.create_simulation(self.planet_configs, self.sim_config)
        self._planets = itertools.cycle(self.planets)
        GravitySimulation.BIG_G = sim_config["gravitational_constant"]
        GravitySimulation.DRAW_SOI = sim_config["draw_sphere_of_influence"]

    def does_this_planet_exist(self, planet):
        return planet in self.planets()

    @property
    def planet_to_follow(self):
        return self.planets_to_follow[self.following_idx][1]

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
    def get_distance_and_vectors_for_planets(cls, planets):
        """
        Builds a dictionary of radius vectors between planets
        of format:
        {
            p1 : {
                p2: (distance to p2, vector to p2),
                p3: (distance to p3, vector to p3)
            },
            p2 : {
                p1: (distance to p1, vector to p1),
                p3: (distance to p3, vector to p3)
            }
            etc..
        }
        """
        return_dict = dict([(p, {}) for p in planets])
        for a, b in itertools.permutations(planets, 2):
            dist, vect = a.get_distance_to_other_body(b)
            return_dict[a][b] = (dist, vect)
            return_dict[b][a] = (dist, -vect)

        return return_dict

    @classmethod
    def update_positions(cls, dt, planets):
        for p in planets:
            p.coord.update_vel(dt)

    @classmethod
    def update_velocities(cls, dt, planets):
        for p in planets:
            p.coord.update_pos(dt)

    @classmethod
    def update_acceleration(cls, dt, planets):
        dead_planets = set()
        planet_distances = cls.get_distance_and_vectors_for_planets(planets)

        for a, influencing_planets in planet_distances.items():
            new_acc_of_a = Coordinate.get_empty_coord()

            for p, p_info in influencing_planets.items():
                new_acc_of_a += cls.BIG_G * p.mass * p_info[1] / p_info[0] ** 3

                if p_info[0] < body.Planet.get_collision_distance(a, p):
                    dead_planets.add(body.Planet.handle_collision(a, b))

            a.coord.set_acc(new_acc_of_a)

        cls.delete_dead_planets(planets, dead_planets)

    @classmethod
    def delete_dead_planets(cls, planets, dead_planets):
        for p in dead_planets:
            planets.remove(p)

    def handle_event(self, event):
        pass

    def update_planets(self, dt):
        log.info("UPDATING POSITIONS")
        self.update_positions(dt, self.planets)
        log.info("UPDATING FORCES/ACCELERATION")
        self.update_acceleration(dt, self.planets)
        log.info("UPDATING VELOCITIES")
        self.update_velocities(dt, self.planets)

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
            p.draw(surface, camera)

            if GravitySimulation.DRAW_SOI is True:
                p.draw_sphere_of_influence(surface, camera)

    def clear_planet_trails(self):
        for p in self.planets:
            p.clear_planet_trail()
