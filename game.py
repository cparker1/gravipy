__author__ = 'charles.andrew.parker@gmail.com'


import objects
import logging
from coordinate import Coordinate

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class GravitySim(object):
    big_g = 0
    draw_soi = False

    def __init__(self, planet_configs, config):
        for p in planet_configs:
            objects.body.Planet(**p)
        GravitySim.big_g = config["gravitational_constant"]
        GravitySim.draw_soi = config["draw_sphere_of_influence"]
        self.initial_potential = objects.body.Planet.calculate_initial_potential()
        self.initial_kinetic = objects.body.Planet.get_total_kinetic_energy()
        self.total_energy = self.initial_kinetic + self.initial_potential
        log.info("Initial KE: {}, initial PE: {}, initial Total: {}".format(self.initial_kinetic,
                                                                            self.initial_potential,
                                                                            self.total_energy))

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

