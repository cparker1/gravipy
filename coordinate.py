__author__ = 'charles'

import logging
import numpy as np
import random
import math

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Coordinate(object):

    DIMENSIONS = 3

    @classmethod
    def get_distance_and_radius_vector(cls, CoordA, CoordB):
        radius_vector = (1.0) * (CoordB.pos - CoordA.pos)
        return np.sqrt(radius_vector.dot(radius_vector)), radius_vector

    @classmethod
    def get_empty_coord(cls):
        """
        returns an empty coordinate that
        matches the dimensions expected
        """
        return np.array([0 for _ in range(cls.DIMENSIONS)])

    @classmethod
    def get_random_coordinate(cls, radius_from_zero):
        pitch = random.sample(np.arange(1 * math.pi / 8, 7 * math.pi / 8, math.pi/180), 1)[0]
        yaw = random.sample(np.arange(0, 2 * math.pi, math.pi/180), 1)[0]
        x = radius_from_zero * math.sin(pitch) * math.cos(yaw)
        y = radius_from_zero * math.sin(pitch) * math.sin(yaw)
        z = radius_from_zero * math.cos(pitch)
        return np.array([x, y, z])

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
        log.debug("Initial pos {}; vel {}".format(self.pos, self.vel))
        self.pos = self.pos + dt * self.vel
        log.debug("Final pos {}".format(self.pos))

    def update_vel(self, dt):
        log.debug("Initial vel {}".format(self.vel))
        self.vel = self.vel + dt * self.acc
        log.debug("Final vel {}".format(self.vel))

    def set_acc(self, acc):
        log.debug("Changing acceleration to {}".format(acc))
        self.acc = acc

    def get_speed(self):
        return np.sqrt(self.vel.dot(self.vel))
