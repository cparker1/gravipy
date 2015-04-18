__author__ = 'charles.andrew.parker@gmail.com'


import objects
import logging
import numpy as np

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def get_velocity_for_circular_orbit(parent, orbiter):
    radius = np.array(orbiter["pos"]) - np.array(parent["pos"])
    dist = np.linalg.norm(radius)

    vel_norm = np.cross(radius / dist, np.array([0, 0, 1]))
    speed = np.math.sqrt(0.10 * parent["mass"] / dist)
    orbiter["vel"] = speed * vel_norm[:2]


class GravitySim(object):
    big_g = 0
    draw_soi = False

    def __init__(self, planet_configs, config):
        self.planet_configs = planet_configs
        self.total_energy = 0
        self.create_simulation(self.planet_configs)
        GravitySim.big_g = config["gravitational_constant"]
        GravitySim.draw_soi = config["draw_sphere_of_influence"]

    def create_simulation(self, planet_configs):
        log.info("Creating simulation.")
        for p in planet_configs:
            objects.body.Planet(**p)
        initial_kinetic = objects.body.Planet.get_total_kinetic_energy()
        initial_potential = objects.body.Planet.calculate_initial_potential()
        self.total_energy = initial_kinetic + initial_potential
        log.info("Initial KE: {}, initial PE: {}, initial Total: {}".format(initial_kinetic,
                                                                            initial_potential,
                                                                            self.total_energy))

    def reset(self):
        objects.body.Planet.kill_planets()
        self.create_simulation(self.planet_configs)

    def update_planets(self, dt):
        log.info("UPDATING POSITIONS")
        objects.body.Planet.update_positions(dt)
        log.info("UPDATING VELOCITY AND POTENTIAL ENERGY")
        objects.body.Planet.update_velocity_and_potential(dt)
        log.info("SCALING KINETIC ENERGY")
        objects.body.Planet.scale_kinetic_energy_to_total_energy(self.total_energy)
        log.info("DELETING DEAD PLANETS")
        new_energy = objects.body.Planet.delete_dead_planets()
        if new_energy is not None:
            self.total_energy = new_energy

    def draw_planets(self, surface):
        log.info("Drawing planets")
        for p in objects.body.Planet.planets:
            log.debug("P {}".format(p.coord.pos))
            p.draw(surface)

        if GravitySim.draw_soi is True:
            for p in objects.body.Planet.planets:
                p.draw_sphere_of_influence(surface)




