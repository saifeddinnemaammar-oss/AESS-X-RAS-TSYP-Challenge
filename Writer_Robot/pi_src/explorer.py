"""
Frontier-based exploration logic.
"""
import math
import numpy as np
import logging

class FrontierExplorer:
    def __init__(self, width_m=20, height_m=20, resolution_m=0.05):
        self.resolution = resolution_m
        self.width = int(width_m / resolution_m)
        self.height = int(height_m / resolution_m)
        # -1: unknown, 0: free, 100: obstacle
        self.grid = np.full((self.height, self.width), -1, dtype=np.int8)
        self.origin_x = self.width // 2
        self.origin_y = self.height // 2
        
        self.current_pose = (0.0, 0.0, 0.0)
        self.frontiers = []

    def world_to_grid(self, x, y):
        gx = int(x / self.resolution) + self.origin_x
        gy = int(y / self.resolution) + self.origin_y
        return gx, gy

    def grid_to_world(self, gx, gy):
        x = (gx - self.origin_x) * self.resolution
        y = (gy - self.origin_y) * self.resolution
        return x, y

    def update_grid(self, lidar_scan, robot_pose):
        """
        lidar_scan: list of (angle_rad, distance_m)
        robot_pose: (x_m, y_m, theta_rad)
        """
        self.current_pose = robot_pose
        rx, ry, rtheta = robot_pose
        rgx, rgy = self.world_to_grid(rx, ry)

        if 0 <= rgx < self.width and 0 <= rgy < self.height:
            self.grid[rgy, rgx] = 0

        # Simplified ray endpoint marking
        for angle, dist in lidar_scan:
            if dist < 0.1:
                continue
            world_angle = rtheta + angle
            hx = rx + dist * math.cos(world_angle)
            hy = ry + dist * math.sin(world_angle)
            hgx, hgy = self.world_to_grid(hx, hy)
            if 0 <= hgx < self.width and 0 <= hgy < self.height:
                self.grid[hgy, hgx] = 100
        
        self.find_frontiers()

    def find_frontiers(self):
        # Placeholder for actual Canny edge detection / clustering
        self.frontiers = [(self.current_pose[0] + 1.0, self.current_pose[1])]

    def select_target(self):
        if not self.frontiers:
            return (self.current_pose[0], self.current_pose[1])
        return self.frontiers[0]

    def get_next_waypoint(self):
        tx, ty = self.select_target()
        dx = tx - self.current_pose[0]
        dy = ty - self.current_pose[1]
        heading = math.atan2(dy, dx)
        return tx, ty, heading

    def is_exploration_complete(self):
        return False
