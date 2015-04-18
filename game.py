__author__ = 'charles.andrew.parker@gmail.com'


from objects import body
import logging
import numpy as np

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def get_velocity_for_circular_orbit(parent, orbiter):
    radius = np.array(orbiter["pos"]) - np.array(parent["pos"])
    dist = np.linalg.norm(radius)

    vel_norm = np.cross(radius / dist, np.array([0, 0, 1]))
    speed = 1.3 * np.math.sqrt(body.Planet.BIG_G * parent["mass"] / dist)
    orbiter["vel"] = speed * vel_norm[:2]
    log.info("Setting {} circular orbit velocity to {}".format(orbiter["name"], orbiter["vel"]))


class GravitySim(object):
    big_g = 0
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

    def update_planets(self, dt):
        log.info("UPDATING POSITIONS")
        body.Planet.update_positions(dt, self.planets)
        log.info("UPDATING VELOCITY AND POTENTIAL ENERGY")
        body.Planet.update_velocity_and_potential(dt, self.planets)

    def draw_planets(self, surface):
        log.info("Drawing planets")
        for p in self.planets:
            log.debug("P {}".format(p.coord.pos))
            p.draw(surface)

        if GravitySim.draw_soi is True:
            for p in self.planets:
                p.draw_sphere_of_influence(surface)




