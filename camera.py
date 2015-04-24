__author__ = 'charles.andrew.parker@gmail.com'

from coordinate import Coordinate
import numpy as np
import pygame
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Camera(object):
    """
    This is the object that represents the observer's position.
    """
    def __init__(self, pos, screen_dims):
        self.initial_pos = pos
        self.screen_dims = screen_dims
        self.coord = Coordinate(pos, vel=Coordinate.get_empty_coord())
        self.pitch = np.math.pi / 2
        self.yaw = np.math.pi / 2
        self.facing = None
        self.up = None
        self.right = None
        self.screen_diagonal = np.math.sqrt(screen_dims[0] ** 2 + screen_dims[1] ** 2) / 2
        self.field_of_view = np.math.pi / 3.0
        self.get_direction_vectors()

        self.zoom_rate = 200
        self.zoom_multiplier = 1.0
        self.degrees_per_turn = 5
        self.camera_is_moving = False
        self.initial_mouse_pos = None
        self.update_background = False

    def reset(self):
        """
        Placeholder.  For now I don't want the
        camera resetting when the reset command is
        received.
        """
        pass

    def get_direction_vectors(self):
        fx = np.math.sin(self.pitch) * np.math.cos(self.yaw)
        fy = np.math.sin(self.pitch) * np.math.sin(self.yaw)
        fz = np.math.cos(self.pitch)
        self.facing = np.array([fx, fy, fz])

        ux = np.math.sin(self.pitch - np.math.pi / 2) * np.math.cos(self.yaw)
        uy = np.math.sin(self.pitch - np.math.pi / 2) * np.math.sin(self.yaw)
        uz = np.math.cos(self.pitch - np.math.pi / 2)
        self.up = np.array([ux, uy, uz])

        rx = np.math.sin(np.math.pi / 2) * np.math.cos(self.yaw + np.math.pi / 2)
        ry = np.math.sin(np.math.pi / 2) * np.math.sin(self.yaw + np.math.pi / 2)
        rz = np.math.cos(np.math.pi / 2)
        self.right = np.array([rx, ry, rz])

        log.debug("Pitch: {}; Yaw: {}".format(self.pitch, self.yaw))
        log.debug("Facing: {}".format(self.facing))
        log.debug("Up    : {}".format(self.up))
        log.debug("Right : {}".format(self.right))

    def get_apparent_radius_and_draw_pos(self, target_coord, target_radius):
        log.debug("Camera Pos: {} Target Pos: {}".format(self.coord.pos, target_coord.pos))
        distance, vector_to_coord = Coordinate.get_distance_and_radius_vector(self.coord, target_coord)
        log.debug("Distance: {} Radius: {} Rad.Rad: {}".format(distance, vector_to_coord, vector_to_coord.dot(vector_to_coord)))
        face_dot_radius = np.dot(self.facing, vector_to_coord)
        log.debug("Face.radius: {}; distance: {}".format(face_dot_radius, distance))

        def clean_cos(cos_angle):
            return min(1,max(cos_angle,-1))

        log.debug("Face.radius / distance: {}".format(face_dot_radius / distance))
        apparent_angle = np.math.acos(clean_cos(face_dot_radius / distance))
        log.debug("Apparent angle away from center: {} [rad]".format(apparent_angle))

        log.debug("Target Radius: {} Rad/Distance: {}".format(target_radius, target_radius / distance))
        if target_radius < distance:
            apparent_solid_angle = np.math.asin((target_radius / distance))
        else:
            apparent_solid_angle = np.math.pi / 4
        log.debug("Apparent Solid Angle: {}".format(apparent_solid_angle))
        target_screen_radius = (apparent_solid_angle / self.field_of_view) * self.screen_diagonal
        log.debug("Target's Screen Radius: {}".format(target_screen_radius))
        if face_dot_radius < 0 or self.field_of_view < apparent_angle:
            log.debug("Object is not visible")
            return 0, None
        elif apparent_angle < np.math.pi / 180:
            log.debug("Moving object at {} with apparent angle < 1 degree to (0,0)".format(target_coord.pos))
            return target_screen_radius, np.array([(self.screen_dims[0] / 2), (self.screen_dims[1] / 2)])
        else:
            pos_scale = apparent_angle / self.field_of_view
            screen_position_radius = pos_scale * self.screen_diagonal
            projection = (vector_to_coord - ((face_dot_radius / distance) * vector_to_coord))
            projection_len = np.linalg.norm(projection)
            x = (self.screen_dims[0] / 2) + screen_position_radius * np.dot(projection, self.right) / projection_len
            y = (self.screen_dims[1] / 2) + 1.5 * screen_position_radius * np.dot(projection, self.up) / projection_len
            return target_screen_radius, np.round(np.array([x, y])).astype(int)

    def move_backward(self):
        self.update_background = True
        self.coord.pos -= self.zoom_multiplier * self.zoom_rate * self.facing
        self.zoom_multiplier += 0.05

    def move_forward(self):
        self.update_background = True
        self.coord.pos += self.zoom_multiplier * self.zoom_rate * self.facing
        if 1.0 < self.zoom_multiplier:
            self.zoom_multiplier -= 0.05

    def look_up(self):
        self.update_background = True
        self.pitch -= self.degrees_per_turn * np.math.pi / 180
        if self.pitch < 0:
            self.pitch = 0

    def look_down(self):
        self.update_background = True
        self.pitch += self.degrees_per_turn * np.math.pi / 180
        if np.math.pi < self.pitch:
            self.pitch = np.math.pi

    def look_left(self):
        self.update_background = True
        self.yaw -= self.degrees_per_turn * np.math.pi / 180
        if self.yaw < 0:
            self.yaw += 2 * np.math.pi

    def look_right(self):
        self.update_background = True
        self.yaw += self.degrees_per_turn * np.math.pi / 180
        if 2 * np.math.pi < self.yaw:
            self.yaw -= 2 * np.math.pi

    def need_upgrade_background(self):
        if self.update_background is True:
            self.update_background = False
            return True
        else:
            return False

    def update(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
            if event.button == 4:
                self.move_forward()
            elif event.button == 5:
                self.move_backward()

        # Handle Keyboard Inputs for turning
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.look_down()

            if event.key == pygame.K_s:
                self.look_up()

            if event.key == pygame.K_a:
                self.look_left()

            if event.key == pygame.K_d:
                self.look_right()



            self.get_direction_vectors()