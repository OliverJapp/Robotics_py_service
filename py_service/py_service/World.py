import os
import random
from pyrobosim_ros.ros_interface import WorldROSWrapper
from pyrobosim.planning.actions import TaskPlan, TaskAction
import rclpy
import numpy as np
from pyrobosim.core import Robot, World, WorldYamlLoader
from pyrobosim.navigation import ConstantVelocityExecutor, RRTPlanner
from pyrobosim.gui import start_gui
from pyrobosim.utils.general import get_data_folder
from pyrobosim.utils.pose import Pose

data_folder = get_data_folder()

def create_world():
    """Create a test world"""
    world = World()
    world.set_metadata(
        locations=os.path.join("/home/slane/ros2_ws/src/py_service/py_service/Location.yaml"),
        objects=os.path.join("/home/slane/ros2_ws/src/py_service/py_service/Object.yaml"),
    )

    Width = 10
    Height = 10

    r1coords = [(-Width-4, 0), (2, 0), (2, Height), (-Width-4, Height)]
    Warehouse = world.add_room(name="Warehouse", footprint=r1coords, wall_width=0.1, color=[0, 0, 0])

    dif = 3

    Shelves = []

    # Define shelves without associating graph nodes
    Shelves.append(world.add_location(
        name="Item_spawn", category="shelf", parent="Warehouse", pose=Pose(x=1, y=2, yaw=-np.pi / 1.0), color=[0, 0, 0]
    ))

    for j in range(2, Width, dif):
        for i in range(2, Height, dif):
            Shelves.append(world.add_location(
                category="shelf", parent="Warehouse", pose=Pose(x=-i, y=j, yaw=-np.pi / 1.0), color=[0, 0, 0]
            ))
    
    Shelves.append(world.add_location(
        name="Delivery", category="shelf", parent="Warehouse", pose=Pose(x=-Width-1, y=Height-2, yaw=-np.pi / 1.0), color=[0, 0, 0]
    ))

    return world, Shelves

def spawn_object(world, item_id, location):
    object = world.add_object(category=item_id, parent=location, pose=Pose(x=1, y=2, yaw=0.0))
    return object

def create_robot(world, name):
    planner_config = {
        "world": world,
        "bidirectional": True,
        "rrt_connect": True,
        "rrt_star": True,
        "collision_check_step_dist": 0.025,
        "max_connection_dist": 0.25,
        "max_nodes_sampled": 1000,
        "max_time": 2.0,
        "rewire_radius": 1.0,
        "compress_path": True
    }

    
    path_planner = RRTPlanner(**planner_config)
    robot = Robot(name=name, radius=0.1, color=[1, 0, 0], initial_battery_level=float("inf"), path_executor=ConstantVelocityExecutor(), path_planner=path_planner)
    
    return robot

def navigate(item, path):
    actions = [
    TaskAction(
        "navigate",
        source_location="Warehouse",
        target_location=path[0],
    ),]
    actions.append(TaskAction("detect", object=item),)
    actions.append(TaskAction("pick", object=item),)

    for i in range(len(path)-1):
        actions.append(
            TaskAction(
        "navigate",
        source_location=path[i],
        target_location=path[i+1],
    ),)
    actions.append(TaskAction("place", object=item),)
    plan = TaskPlan(actions=actions)

    #result, num_completed = robots[0].execute_plan(plan)
    return plan

def navigate_return(item, path):
    actions = []
    path = path[:-1]
    for i in range(len(path)-1):
        actions.append(
            TaskAction(
        "navigate",
        source_location=path[i],
        target_location=path[i+1],
    ),)
    plan = TaskPlan(actions=actions)

    #result, num_completed = robots[0].execute_plan(plan)
    return plan

def main():
    rclpy.init() 

    world, Shelves = create_world()
    for i in range(4):
        robot = create_robot(world, f"Taxi-Bot{i}")
        world.add_robot(robot, loc="Warehouse", pose=Pose(x=-0.5, y=i, yaw=-np.pi / 1.0))
    node = rclpy.create_node('pyrobosim_world_node')


    """


    Implement ROS: 1: Item spawn, 2: Navigate to goal using path, 3: Navigate to item_spawn / start location

    ros2 run py_service taxi "banana", [item_spawn, shelf1, shelf2, shelf5, shelf8, Delivery]
    
    
    """
    
    world_ros_wrapper = WorldROSWrapper(world)

    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(world_ros_wrapper) 

    os.environ['QT_QPA_PLATFORM'] = 'xcb'
    start_gui(world)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        world_ros_wrapper.destroy_node()
        rclpy.shutdown() 

if __name__ == "__main__":
    main()
