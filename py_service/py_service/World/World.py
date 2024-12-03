#!/usr/bin/env python3

"""
Example showing how to build a world and use it with pyrobosim,
additionally starting up a ROS interface.
"""
import os
import random
from pyrobosim.planning.actions import TaskPlan
from pyrobosim.utils import search_graph
import rclpy
import threading
import numpy as np
from pyrobosim.planning.actions import TaskAction
from pyrobosim.core import Robot, World, WorldYamlLoader
from pyrobosim.navigation import ConstantVelocityExecutor, RRTPlanner
from pyrobosim.gui import start_gui
from pyrobosim.utils.general import get_data_folder
from pyrobosim.utils.pose import Pose
from WarehousePathing import Graph 
import pyrobosim


data_folder = get_data_folder()


def create_world():
    """Create a test world"""
    world = World()
    world.set_metadata(
        locations=os.path.join("/home/slane/pyrobosim/World/Location.yaml"),
        objects=os.path.join("/home/slane/pyrobosim/World/Object.yaml"),
    )
    Width = 10
    Height = 10



    # Set the location and object metadata
    # Add rooms
    #graph = world.graph_node_from_entity(Graph(Height, Width))
    r1coords = [(-Width, 0),
                (2, 0),
                (2, Width),
                (-Width, Height)]

    r2coords = [(2, 0),
                (5, 0),
                (5, 5),
                (2, 5)]
    
    r3coords = [(2, Height-5),
                (5, Height-5),
                (5, Height),
                (2, Height)]
                
    Warehouse = world.add_room(
                name="Warehouse", footprint=r1coords, wall_width=0.1, color=[0, 0, 0]
            )
    
    
    
    dif = 3
    Nav_points = []
    Shelves = []

    Nav_points.append(world.add_location(
                category="Nav_point", parent="Warehouse", pose=Pose(x=-0.5, y=0.5, yaw=-np.pi / 1.0), color = [0, 0, 0]
            ))
    
    Nav_points.append(world.add_location(
                category="Nav_point", parent="Warehouse", pose=Pose(x=-0.5, y=Height-3.5, yaw=-np.pi / 1.0), color = [0, 0, 0]
            ))
    
    Shelves.append(world.add_location(
                category="shelf", parent="Warehouse", pose=Pose(x=1, y=0.5, yaw=-np.pi / 1.0), color = [0, 0, 0]
            ))
    

    for i in range(2, Width, dif):
        for j in range(2, Height, dif):
            Shelves.append(world.add_location(
                category="shelf", parent="Warehouse", pose=Pose(x=-i, y=j, yaw=-np.pi / 1.0), color = [0, 0, 0]
            ))
            Nav_points.append(world.add_location(
                category="Nav_point", parent="Warehouse", pose=Pose(x=-i-dif/2, y=j-dif/2, yaw=-np.pi / 1.0), color = [0, 0, 0]
            ))
        

    planner_config = {
        "world": world,
        "bidirectional": True,
        "rrt_connect": False,
        "rrt_star": True,
        "collision_check_step_dist": 0.025,
        "max_connection_dist": 1.5,
        "rewire_radius": 1.5,
        "compress_path": False,
    }            
    path_planner = RRTPlanner(**planner_config)
    robots = []    
    
    #for i in range(Width//dif):

    robots.append(Robot(name="Taxi_bot", radius=0.1, color = [1, 0, 0], initial_battery_level = float("inf"), path_executor=ConstantVelocityExecutor(), path_planner=path_planner,))
        #robots[i].name = f"Taxi_bot{i}"
    world.add_robot(robots[0], loc="Warehouse", pose=Pose(x=-0.5, y=1, yaw=-np.pi / 1.0))
    world.add_object(category="banana", parent=Shelves[0], pose=Pose(x=1, y=0.5, yaw=0.0))

    
    actions = [
    TaskAction(
        "navigate",
        source_location="Warehouse",
        target_location="shelf0",
    ),
    TaskAction("detect", object="banana"),
    TaskAction("pick", object="banana"),
    TaskAction(
        "navigate",
        source_location="shelf0",
        target_location="shelf8",
    ),
    TaskAction("place", object="banana"),
    ]

    plan = TaskPlan(actions=actions)
    result, num_completed = robots[0].execute_plan(plan)


    return world


def create_ros_node():
    """Initializes ROS node"""
    rclpy.init()
    # Set the world
    world = create_world()

    return world


if __name__ == "__main__":
    world = create_ros_node()

    # Start GUI in main thread
    start_gui(world)