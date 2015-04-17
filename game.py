__author__ = 'charles.andrew.parker@gmail.com'


import objects
import logging
from coordinate import Coordinate

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class GravitySim(object):
    big_g = 0

    def __init__(self, planet_configs, config):
        for p in planet_configs:
            objects.body.Planet(**p)
        GravitySim.big_g = config["gravitational_constant"]
        self.initial_potential = objects.body.Planet.calculate_initial_potential()
        self.initial_kinetic = objects.body.Planet.get_total_kinetic_energy()
        self.total_energy = self.initial_kinetic + self.initial_potential
        log.info("Initial KE: {}, initial PE: {}, initial Total: {}".format(self.initial_kinetic,
                                                                            self.initial_potential,
                                                                            self.total_energy))

    def update_planets(self, dt):
        log.info("UPDATING POSITIONS")
        objects.body.Planet.update_position(dt)
        log.info("UPDATING VELOCITY AND POTENTIAL ENERGY")
        objects.body.Planet.update_velocity_and_potential(dt)
        log.info("SCALING KINETIC ENERGY")
        objects.body.Planet.scale_kinetic_energy_to_total_energy(self.total_energy)

    def draw_planets(self, surface):
        log.info("Drawing planets")
        for p in objects.body.Planet.planets:
            log.debug("P {}".format(p.coord.pos))
            p.draw(surface)
