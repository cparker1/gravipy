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
        self.projection_plane_distance = self.screen_diagonal / np.math.atan(self.field_of_view)
        self.get_direction_vectors()

        self.zoom_rate = 200
        self.zoom_multiplier = 1.0
        self.degrees_per_turn = 5
        self.camera_is_moving = False
        self.initial_mouse_pos = None
        self.update_background = False

        self.key_mappings = {
            pygame.K_DOWN: self.look_down,
            pygame.K_UP: self.look_up,
            pygame.K_LEFT: self.look_left,
            pygame.K_RIGHT: self.look_right,
            pygame.K_a: self.strafe_left,
            pygame.K_d: self.strafe_right,
            pygame.K_w: self.move_forward,
            pygame.K_s: self.move_backward,
            pygame.K_z: self.move_up,
            pygame.K_x: self.move_down
            }

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

        log.debug("Pitch: {} [rad]; Yaw: {} [rad]".format(self.pitch, self.yaw))
        log.debug("Facing: {} [unitless]".format(self.facing))
        log.debug("Up    : {} [unitless]".format(self.up))
        log.debug("Right : {} [unitless]".format(self.right))

    def get_apparent_radius_and_draw_pos(self, target_coord, target_radius):

        # If the target is not visible, return no radius and no position
        def not_visible():
            return 0, None

        # Ensure the arc cos gets a value between [-1, 1]
        def clean_cos(cos_angle):
            return min(1,max(cos_angle,-1))

        # Calculate the vector that points from the camera to the target
        log.debug("Camera Pos: {} [m]; Target Pos: {} [m]".format(self.coord.pos, target_coord.pos))
        distance, vector_to_coord = Coordinate.get_distance_and_radius_vector(self.coord, target_coord)
        log.debug("Distance: {} Radius: {}".format(distance, vector_to_coord))

        # Calculate the component of the target vector that is parallel to the facing vector
        face_dot_radius = np.dot(self.facing, vector_to_coord)
        log.debug("Face.radius: {} [m**2]; distance: {} [m]".format(face_dot_radius, distance))

        # If the facing vector dotted with the target vector is negative,
        # the target is behind the camera.  Return to save time.
        if face_dot_radius < 0:
            return not_visible()

        # Calculate the apparent angular distance from the facing vector
        # to the target vector
        apparent_angle = np.math.acos(clean_cos(face_dot_radius / distance))
        log.debug("Apparent angle away from center: {} [rad]".format(apparent_angle))

        # Return if the target is outside the field of view
        if self.field_of_view < apparent_angle:
            return not_visible()

        # Calculate the apparent size of the target object
        log.debug("Target Radius: {} [m]".format(target_radius))
        if target_radius < distance:
            apparent_solid_angle = np.math.asin((target_radius / distance)) / 2
        else:
            apparent_solid_angle = np.math.pi / 3.0

        # Determine the apparent size of the target object
        log.debug("Apparent Solid Angle: {} [rad]".format(apparent_solid_angle))
        apparent_target_radius = (apparent_solid_angle / self.field_of_view) * self.screen_diagonal
        log.debug("Target's Screen Radius: {}".format(apparent_target_radius))

        # If we've made it this far, calculate the position of the target
        vector_scale = self.projection_plane_distance / face_dot_radius
        projection = vector_scale * (vector_to_coord - ((face_dot_radius / distance) * self.facing))
        x = (self.screen_dims[0] / 2) + np.dot(projection, self.right)
        y = (self.screen_dims[1] / 2) + np.dot(projection, self.up)

        return apparent_target_radius, np.round(np.array([x, y])).astype(int)

    def move_backward(self):
        self.update_background = True
        self.coord.pos -= self.zoom_multiplier * self.zoom_rate * self.facing

    def move_forward(self):
        self.update_background = True
        self.coord.pos += self.zoom_multiplier * self.zoom_rate * self.facing

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

    def move_up(self):
        self.update_background = True
        self.coord.pos -= self.zoom_multiplier * self.zoom_rate * self.up

    def move_down(self):
        self.update_background = True
        self.coord.pos += self.zoom_multiplier * self.zoom_rate * self.up

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

    def strafe_left(self):
        self.update_background = True
        self.coord.pos -= self.zoom_multiplier * self.zoom_rate * self.right

    def strafe_right(self):
        self.update_background = True
        self.coord.pos += self.zoom_multiplier * self.zoom_rate * self.right

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
            if event.key in self.key_mappings.keys():
                self.key_mappings[event.key]()

            self.get_direction_vectors()