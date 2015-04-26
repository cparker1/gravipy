__author__ = 'charles.andrew.parker@gmail.com'

from coordinate import Coordinate
import numpy as np
import pygame
import logging
import math

class Camera(object):
    """
    This is the object that represents the observer's position.
    """

    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    CAMERAEVENT = pygame.USEREVENT
    CAMERAMOVED = 0
    CAMERATURNED = 1

    def __init__(self, pos, screen_dims):
        self.initial_pos = pos
        self.screen_dims = screen_dims
        self.displacement = Coordinate(pos, vel=Coordinate.get_empty_coord())
        self.origin = Coordinate(Coordinate.get_empty_coord(), Coordinate.get_empty_coord())
        self.displacement = Coordinate(Coordinate.get_empty_coord(), Coordinate.get_empty_coord())
        self.pitch = math.pi / 2
        self.yaw = math.pi / 2
        self.facing = None
        self.up = None
        self.right = None
        self.screen_diagonal = math.sqrt(screen_dims[0] ** 2 + screen_dims[1] ** 2) / 2
        self.field_of_view = math.pi / 3.0
        self.projection_plane_distance = self.screen_diagonal / math.atan(self.field_of_view)
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

    @property
    def coord(self):
        return Coordinate(self.origin.pos + self.displacement.pos, self.origin.vel + self.displacement.vel)

    def reset(self):
        """
        Placeholder.  For now I don't want the
        camera resetting when the reset command is
        received.
        """
        pass

    @staticmethod
    def clean_cos(acos_arg):
        """
        Rails the passed in argument between [-1, 1]
        """
        return min(1,max(acos_arg,-1))

    def get_direction_vectors(self):
        fx = math.sin(self.pitch) * math.cos(self.yaw)
        fy = math.sin(self.pitch) * math.sin(self.yaw)
        fz = math.cos(self.pitch)
        self.facing = np.array([fx, fy, fz])

        ux = math.sin(self.pitch - math.pi / 2) * math.cos(self.yaw)
        uy = math.sin(self.pitch - math.pi / 2) * math.sin(self.yaw)
        uz = math.cos(self.pitch - math.pi / 2)
        self.up = np.array([ux, uy, uz])

        rx = math.sin(math.pi / 2) * math.cos(self.yaw + math.pi / 2)
        ry = math.sin(math.pi / 2) * math.sin(self.yaw + math.pi / 2)
        rz = math.cos(math.pi / 2)
        self.right = np.array([rx, ry, rz])

        Camera.log.debug("Pitch: {} [rad]; Yaw: {} [rad]".format(self.pitch, self.yaw))
        Camera.log.debug("Facing: {} [unitless]".format(self.facing))
        Camera.log.debug("Up    : {} [unitless]".format(self.up))
        Camera.log.debug("Right : {} [unitless]".format(self.right))

    def point_towards_target(self, target_coord):
        Camera.log.debug("Facing target coordinate {}".format(target_coord.pos))
        coord = Coordinate(self.origin.pos + self.displacement.pos, self.origin.vel + self.displacement.vel)
        distance, target_vector = Coordinate.get_distance_and_radius_vector(coord, target_coord)
        normalized_vector = target_vector / distance
        pitch = math.acos(Camera.clean_cos(normalized_vector[2]))
        yaw = math.acos(Camera.clean_cos(normalized_vector[0] / math.sin(pitch)))
        self.pitch = pitch
        self.yaw = yaw
        Camera.log.debug("New Pitch, Yaw = {}, {}".format(self.pitch, self.yaw))
        self.get_direction_vectors()
        self.update_background = True

    def set_origin(self, coord):
        Camera.log.debug("Setting origin to {}".format(coord.pos))
        self.origin.pos = coord.pos + np.array([0, 500, 0])

    def camera_has_moved(self):
        event = pygame.event.Event(Camera.CAMERAEVENT, movement=Camera.CAMERAMOVED)
        pygame.event.post(event)

    def camera_has_turned(self):
        event = pygame.event.Event(Camera.CAMERAEVENT, movement=Camera.CAMERATURNED)
        pygame.event.post(event)

    def get_apparent_radius_and_draw_pos(self, target_coord, target_radius):

        # If the target is not visible, return no radius and no position
        def not_visible():
            return 0, None

        # Calculate the vector that points from the camera to the target
        coord = Coordinate(self.origin.pos + self.displacement.pos, self.origin.vel + self.displacement.vel)
        Camera.log.debug("Camera Pos: {} [m]; Target Pos: {} [m]".format(coord.pos, target_coord.pos))
        distance, vector_to_coord = Coordinate.get_distance_and_radius_vector(coord, target_coord)
        Camera.log.debug("Distance: {} Radius: {}".format(distance, vector_to_coord))

        # Calculate the component of the target vector that is parallel to the facing vector
        face_dot_radius = np.dot(self.facing, vector_to_coord)
        Camera.log.debug("Face.radius: {} [m**2]; distance: {} [m]".format(face_dot_radius, distance))

        # If the facing vector dotted with the target vector is negative,
        # the target is behind the camera.  Return to save time.
        if face_dot_radius < 0:
            return not_visible()

        # Calculate the apparent angular distance from the facing vector
        # to the target vector
        apparent_angle = math.acos(Camera.clean_cos(face_dot_radius / distance))
        Camera.log.debug("Apparent angle away from center: {} [rad]".format(apparent_angle))

        # Return if the target is outside the field of view
        if self.field_of_view < apparent_angle:
            return not_visible()

        # Calculate the apparent size of the target object
        Camera.log.debug("Target Radius: {} [m]".format(target_radius))
        if target_radius < distance:
            apparent_solid_angle = math.asin((target_radius / distance))
        else:
            apparent_solid_angle = math.pi / 3.0

        # Determine the apparent size of the target object
        Camera.log.debug("Apparent Solid Angle: {} [rad]".format(apparent_solid_angle))
        apparent_target_radius = (apparent_solid_angle / self.field_of_view) * self.screen_diagonal
        Camera.log.debug("Target's Screen Radius: {}".format(apparent_target_radius))

        # If we've made it this far, calculate the position of the target
        vector_scale = self.projection_plane_distance / face_dot_radius
        projection = vector_scale * (vector_to_coord - ((face_dot_radius / distance) * self.facing))
        x = (self.screen_dims[0] / 2) + np.dot(projection, self.right)
        y = (self.screen_dims[1] / 2) + np.dot(projection, self.up)

        return apparent_target_radius, np.round(np.array([x, y])).astype(int)

    def move_backward(self):
        self.camera_has_moved()
        self.displacement.pos -= self.zoom_multiplier * self.zoom_rate * self.facing

    def move_forward(self):
        self.camera_has_moved()
        self.displacement.pos += self.zoom_multiplier * self.zoom_rate * self.facing

    def look_up(self):
        self.camera_has_moved()
        self.camera_has_turned()
        self.pitch -= self.degrees_per_turn * math.pi / 180
        if self.pitch < 0:
            self.pitch = 0

    def look_down(self):
        self.camera_has_moved()
        self.camera_has_turned()
        self.pitch += self.degrees_per_turn * math.pi / 180
        if math.pi < self.pitch:
            self.pitch = math.pi

    def move_up(self):
        self.camera_has_moved()
        self.displacement.pos -= self.zoom_multiplier * self.zoom_rate * self.up

    def move_down(self):
        self.camera_has_moved()
        self.displacement.pos += self.zoom_multiplier * self.zoom_rate * self.up

    def look_left(self):
        self.camera_has_moved()
        self.camera_has_turned()
        self.yaw -= self.degrees_per_turn * math.pi / 180
        if self.yaw < 0:
            self.yaw += 2 * math.pi

    def look_right(self):
        self.camera_has_moved()
        self.camera_has_turned()
        self.yaw += self.degrees_per_turn * math.pi / 180
        if 2 * math.pi < self.yaw:
            self.yaw -= 2 * math.pi

    def strafe_left(self):
        self.camera_has_moved()
        self.displacement.pos -= self.zoom_multiplier * self.zoom_rate * self.right

    def strafe_right(self):
        self.camera_has_moved()
        self.displacement.pos += self.zoom_multiplier * self.zoom_rate * self.right

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