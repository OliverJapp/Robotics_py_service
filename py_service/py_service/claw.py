import math
import sys
import rclpy
from rclpy.node import Node
from new_interfaces.srv import JobBoardC

class Claw(Node):
    def __init__(self, name):
        super().__init__('claw_service')
        #Service for hive to send the shelf location
        self.srv = self.create_service(JobBoardC, f'pickItem_claw{name}', self.pickClaw_callback)
        self.srv = self.create_service(JobBoardC, f'takeFromTaxi{name}', self.pickFromTaxi_callback)
        angle = 90
        self.name = name
        self.arm1Angle = angle
        self.arm2Angle = angle
        self.baseAngle = angle
        self.gripAngle = angle
        self.x = 0
        self.y = 0
        self.z = angle
        self.location = [self.x, self.y, self.z]
        self.open = True
        self.full = False
        self.shelf_location = None
        self.item = None
        #create lists for each item operation
        self.get = []
        self.put = []

    #Communication between taxi and claw to pick and get the items
    #should check if given items match ones in array 
    def pickFromTaxi_callback(self, request, response):
        response.sum = self.location
        self.get_logger().info('Incoming request\n items:%s name:%s location:%s %s' % (request.item, request.name, request.location, response.sum))
        return response

    #REcieve the shelf location
    def pickClaw_callback(self, request, response):
        response.sum = self.location
        self.get_logger().info('Incoming request\n items:%s name:%s location:%s %s' % (request.item, request.name, request.location, response.sum))
        #create a list for each item operation
        order = []
        order.append(request.item)
        order.append(request.location)
        if request.name == 'get':
            self.get.append(order)
            print("get", order)
        else:
            self.put.append(order)
            print("put", order)
        return response

    def moveToAngle(self, targetx, targety, targetz):
        b = math.atan2((targety-self.y),(targetx-self.x))
        l = math.sqrt(pow((targetx-self.x), 2)+pow((targety-self.y),2))
        h = math.sqrt(pow(l, 2)+ pow((targetz - self.z), 2))
        phi = math.atan((targetz-self.z)/l)
        theta = math.acos((h/2)/5000) 
        a1 = phi + theta
        a2 = phi - theta
        self.baseAngle = b
        self.arm1Angle = a1
        self.arm2Angle = a2
        self.setLocation([targetx, targety, targetz])
        print(b, a1, a2)
        return (self.location)

    def movement(self, target):
        targetX = target[0]
        targetY = target[1]
        targetZ = target[2]
        self.openClaw()
        if self.location != target:
            self.moveToAngle(targetX, targetY, targetZ)


    def setLocation(self, location):
        self.location = location

    def recieve(self, item, location):
        self.movement(location)
        location = self.get()
        self.movement(location)
        self.put()
        return 0
    
    def get(self):
        self.closeClaw()
        #loc = hive.getShelfLocation()
        return loc
    
    def put(self):
        self.openClaw()
    
    
    def openClaw(self):
        self.open = True
        return 0
    
    def closeClaw(self):
        if self.open == True:
            self.open = False
            self.full = True
        return 0
def main():
    rclpy.init()
    name = sys.argv[1]
    claw = Claw(name)
    rclpy.spin(claw)
    rclpy.shutdown()
#claw.movement([4, 10, 0])
'''import pyrobosim as prs
import numpy as np

class Claw():

    def __init__(self):
        robot = prs.robots.Robot(
            name = "robot_arm",
            base_type = "differential",
        )

        arm = prs.robots.RobotArm(
            name = "arm",
            num_joints = 3,
            joint_limits = np.radians([[-90, 90], [-90, 90], [-90, 90]]),
        )

        robot.add_arm(arm)

        grabber = prs.robots.RobotGripper(name = "grabber")
        robot.add_gripper(grabber, parent_link="link2")

        return robot

def create_word():
    word = prs.simulation.SimulationWorld()
    robot = Claw()
    word.add_robot(robot)
    world.add_object(prs.world.Object(name="block", pose=(1.0,0.5, 0)))
    return word

if __name__ == "__main__":
    word = create_word()
    viewer = prs.visualizer.PyGameViewer(word)
    viewer.run()'''
