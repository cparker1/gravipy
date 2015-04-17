__author__ = 'charles'

import logging
import numpy as np

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Coordinate(object):

    DIMENSIONS = 2

    @classmethod
    def get_distance_and_radius_vector(cls, CoordA, CoordB):
        radius_vector = CoordB.pos - CoordA.pos
        return np.linalg.norm(radius_vector), radius_vector

    @classmethod
    def get_empty_coord(cls):
        """
        returns an empty coordinate that
        matches the dimensions expected
        """
        return np.array([0 for _ in range(cls.DIMENSIONS)])

    @classmethod
    def validate_coordinate(cls, coord):
        if len(coord) != Coordinate.DIMENSIONS:
            log.error("dimensions must equal {}".format(Coordinate.DIMENSIONS))
            raise ValueError
        else:
            return np.array(coord)


    def __init__(self, pos, vel):
        self.pos = Coordinate.validate_coordinate(pos)
        self.vel = Coordinate.validate_coordinate(vel)
        self.acc = Coordinate.get_empty_coord()

    def update_pos(self, dt):
        log.debug("Initial pos {}".format(self.pos))
        self.pos = self.pos + dt*self.vel
        log.debug("Final pos {}".format(self.pos))

    def update_vel(self, acc, dt):
        log.debug("Initial vel {}".format(self.vel))
        self.vel = self.vel + dt*acc
        log.debug("Final vel {}".format(self.vel))

    def get_speed(self):
        return np.linalg.norm(self.vel)
