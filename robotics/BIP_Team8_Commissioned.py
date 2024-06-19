########################################
# 
#  @author Justus Kahlert (HSB)
#  Matrikelnummer: 5151051
#  
#  Contact: jkahlert@stud.hs-bremen.de
#  
#  Project BIP Embedded Systems For Mobile Robots
#  File: BIP_Team8_Commissioned.py
# 
#  @version 1.1
#  created         08/01/2024
#  last updated    12/01/2024 
# 
########################################


#------------------------------------------------
# Imports 
#------------------------------------------------
from machine import Pin, PWM, ADC, Timer
from time import sleep
from rotary_irq_esp import RotaryIRQ
import math
import time
from definitions import *



#------------------------------------------------
# Declarations
#------------------------------------------------
# Software-Variables
#-------------------------

# define points for the robot to start, pickup- and place the box
pStartPoint = "B4"
pPickupPoint = "A3"
pPlacePoint = "B3"

# counters
node_counter = 0        # index for the nodes in the calculated path
global_counter = 0      # global counter for main state machine
step_count = 0          # step counter for steps in motion sub-programs (follow_line or rotate)
overhead_counter = 0    # counter to terminate overhead-movement
move_over_counter = 0   # counter to terminate move_over-movement
move_back_counter = 0   # counter to terminate move_back-movement
follow_line_counter = 0 # counter to terminate follow_line-movement
line_counter = 0        # counter used to debounce the IR-sensor readings when turning the robot
far_counter = 0         # counter used to debounce the IR-sensor readings when detecting intersections

# counter for follow_line_state changes
follow_line_state_counter = 0
FOLLOW_LINE_STATE_COUNTER_MAX = 3

# kill-booleans to exit functions or program
bTerminate = False                      # terminate entire program
bExit_follow_line = False               # exit follow_line function
bExit_pose_robot_orientation = False    # exit pose_robot_orientation function
bExit_move_over = False                 # exit move_over function
bExit_move_back = False                 # exit move_back function

# boolean variables
bReturn = False             # robot is on return path
bFinalNode = False          # node is final node
bTurnRight = False          # set motor direction to turn right
bTurnLeft = False           # set motor directions to turn left
bObjectDetected = False     # object is detected


# empty variables
path = None
state = None
current_node = None
next_node = None
final_node = None
needed_orientation = None
current_orientation = None

# set debounce threshold for sensors
sensor_debounce_threshold = 3

# set values for motors
MAX_SPEED = 100  # Maximum speed
MAX_SPEED_LEFT = 73
MAX_SPEED_RIGHT =72
frequency = 5000  # PWM frequency

# set initial speed values to 0
leftSpeed = 0
rightSpeed = 0

# robot follow_line states
follow_line_states = ['forward', 'turn_right', 'turn_left', 'far_right', 'far_left', 'aligned', 'overhead']
follow_line_current_state = follow_line_states[0]  # Initial state

# Robot pose
x =  0          # x position
y = 0           # y position
phi = 6.28      # orientation
delta_t = 0.1
save_x = 0      # to save previous value
save_y = 0      # to save previous value
save_phi = 0    # to save previous value



#------------------------------------------------
# Initialize devices
#------------------------------------------------

# IR SENSOR
IR_SENSORS = [39, 36, 34, 35, 4]  # Blue, Yellow, Orange, Green, White (Cable Colours)
analog_pins = [ADC(Pin(IR)) for IR in IR_SENSORS]

# attenuate ADC to change the reference voltage to 3.3V
for pin in analog_pins:
    pin.atten(ADC.ATTN_11DB)

# ENCODERS (NOT USED)
encoder1 = RotaryIRQ(pin_num_clk=ENC1_A, 
              pin_num_dt=ENC1_B, 
              min_val=0, 
              max_val=10000, 
              reverse=False, 
              range_mode=RotaryIRQ.RANGE_WRAP)  # Right wheel encoder: 966 ppr
encoder2 = RotaryIRQ(pin_num_clk=ENC2_A, 
              pin_num_dt=ENC2_B, 
              min_val=0, 
              max_val=10000, 
              reverse=True, 
              range_mode=RotaryIRQ.RANGE_WRAP)  # Left wheel encoder: 968 ppr


# TOUCH SENSOR
TOUCHSW_PIN = 12  
touchsw = Pin(TOUCHSW_PIN, Pin.IN, Pin.PULL_UP)  # define touch switch pin with internal pull-up

# MAGNET
SOLENOID_PIN = 13  
MAGN_FREQUENCY = 15000  # PWM frequency for magnet
solenoid = PWM(Pin(SOLENOID_PIN), MAGN_FREQUENCY)  # define PWM for solenoid pin

# MOTORS
from dcmotor import L298 as DCMotor

# define pins for the left motor (ML_A and ML_B) as output pins
pin1 = Pin(ML_A, Pin.OUT)
pin2 = Pin(ML_B, Pin.OUT)
# define enable pin for the left motor and set its frequency
enable1 = PWM(Pin(ENABLE_L), frequency)
# define pins for the right motor (MR_A and MR_B) as output pins
pin3 = Pin(MR_A, Pin.OUT)
pin4 = Pin(MR_B, Pin.OUT)
# define enable pin for the right motor and set its frequency
enable2 = PWM(Pin(ENABLE_R), frequency)
# create DCMotor objects for the left and right motors using the defined pins and enable signal
# the last two parameters (0 and 1023) define range of the PWM signal
leftMotor = DCMotor(pin1, pin2, enable1, 0, 1023)
rightMotor = DCMotor(pin3, pin4, enable2, 0, 1023)



#------------------------------------------------
# Robot Localization Functions
#------------------------------------------------

def readIRSensors(analog_pins):
    '''
    Read the IR sensors using the AD converter and return a list with inverted values:
    white = 1; 4096 = black
    '''
    return [4096 - pin.read() for pin in analog_pins]






#------------------------------------------------
# A* Algorithm Implementation
#------------------------------------------------

# the class Node implements a node object for the A* algorithm
class Node:
    def __init__(self, name, x, y, angle):
        self.name = name  
        self.x = x  # x value of the node according to grid (see documentation)
        self.y = y  # Y value of the node according to grid (see documentation)
        self.angle = angle  # angle value of the node NOT USED
        self.connections = {}  # connections of node

# the class Graph implements a graph consisting of nodes and edges
# to use with the A* algorithm
class Graph:
    def __init__(self):
        self.nodes = {}  # store all nodes

    # add a new node with x, y, and angle values
    def add_node(self, name, x, y, angle):
        self.nodes[name] = Node(name, x, y, angle)  

    # get a node
    def get_node(self, name):
        return self.nodes.get(name, None)   
    
    # add an edge between two nodes
    def add_edge(self, node1, node2, cost):
        self.nodes[node1].connections[self.nodes[node2]] = cost
        self.nodes[node2].connections[self.nodes[node1]] = cost

    # return the cost of an edge between two nodes
    def get_cost(self, node1_name, node2_name):
        node1 = self.get_node(node1_name)
        node2 = self.get_node(node2_name)
        if node1 is not None and node2 is not None and node2 in node1.connections:
            return node1.connections[node2]
        else:
            return None
    
    # remove a node and all its connections
    def remove_node(self, name):
        if name in self.nodes:
            node = self.nodes[name]
            for connected_node in node.connections:
                del connected_node.connections[node]
            del self.nodes[name]

    # remove an edge between two nodes
    def remove_edge(self, node1, node2):
        if node1 in self.nodes and node2 in self.nodes:
            del self.nodes[node1].connections[self.nodes[node2]]
            del self.nodes[node2].connections[self.nodes[node1]]
    
    # A* algorithm to calculate shortest path
    def a_star(self, start, goal):
        open_list = {self.nodes[start]: 0}  # open list for A*
        came_from = {}  # stores which node a node was reached from
        cost_so_far = {self.nodes[start]: 0}  # stores the cost to reach a node

        while open_list:  # as long as there are still nodes in the open list
            current = min(open_list, key=open_list.get)  # select node with the lowest cost
            if current.name == goal:  # if the current node is the goal
                return self.reconstruct_path(came_from, self.nodes[start], self.nodes[goal])  # reconstruct path from start to goal

            del open_list[current]  # remove current node from open list

            for neighbor in current.connections:  # for each neighbor node of the current node
                new_cost = cost_so_far[current] + current.connections[neighbor]  # calculate new cost
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:  # if the neighbor has not been visited yet or the new cost is lower
                    cost_so_far[neighbor] = new_cost  # update cost
                    priority = new_cost  # set priority to new cost
                    open_list[neighbor] = priority  # add neighbor to open list
                    came_from[neighbor] = current  # store which node the neighbor was reached from

        return None  # if there is no path to the goal -> return None

    # reconstruct path
    def reconstruct_path(self, came_from, start, goal):
        current = goal  # start at goal node
        path = []  # list for the path
        while current != start:  # as long as the current node is not the start node
            path.append(current.name)  # add name of the current node to the path
            current = came_from[current]  # switch to the node from which the current node was reached
        path.append(start.name)  # add start node to the path
        path.reverse()  # reverse path
        return path  # return path




#------------------------------------------------
# Initialize Maze Data
#------------------------------------------------
    
# create graph object
graph = Graph()

node_dict = {
    "A1": (1, 7, 0),
    "A2": (2, 7, 0),
    "A3": (3, 7, 0),
    "A4": (4, 7, 0),
    
}

for node_name, node_data, in node_dict.items():
    graph.add_node(node_name, *node_data)

# add nodes
graph.add_node("A1", 1, 7, 0)
graph.add_node("A2", 2, 7, 0)
graph.add_node("A3", 3, 7, 0)
graph.add_node("A4", 4, 7, 0)

graph.add_node("B1", 6, 1, 0)
graph.add_node("B2", 7, 1, 0)
graph.add_node("B3", 8, 1, 0)
graph.add_node("B4", 9, 1, 0)

graph.add_node("C1", 1, 6, 0)
graph.add_node("C2", 2, 6, 0)
graph.add_node("C3", 3, 6, 0)
graph.add_node("C4", 4, 6, 0)

graph.add_node("D1", 6, 2, 0)
graph.add_node("D2", 7, 2, 0)
graph.add_node("D3", 8, 2, 0)
graph.add_node("D4", 9, 2, 0)

graph.add_node("E1", 1, 5, 0)
graph.add_node("E2", 1, 4, 0)
graph.add_node("E3", 1, 3, 0)
graph.add_node("E4", 1, 2, 0)

graph.add_node("F1", 5, 6, 0)
graph.add_node("F2", 5, 5, 0)
graph.add_node("F3", 5, 4, 0)
graph.add_node("F4", 5, 3, 0)
graph.add_node("F5", 5, 2, 0)

graph.add_node("G1", 9, 6, 0)
graph.add_node("G2", 9, 5, 0)
graph.add_node("G3", 9, 4, 0)
graph.add_node("G4", 9, 3, 0)

graph.add_node("A15", 1, 6, 0)


# define constant lengths for edges (weights)
# these values are taken qualitative from the simulation
# but work analog in the real environment (see documentation)
length_1 = 0.1
length_2 = 0.15
length_3 = 0.11
length_5 = 0.11
length_6 = 0.2
length_4 = (3 * length_5) + length_6


# add edges between nodes
graph.add_edge("A1", "C1", length_1)
graph.add_edge("A2", "C2", length_1)
graph.add_edge("A3", "C3", length_1)
graph.add_edge("A4", "C4", length_1)

graph.add_edge("B1", "D1", length_1)
graph.add_edge("B2", "D2", length_1)
graph.add_edge("B3", "D3", length_1)
graph.add_edge("B4", "D4", length_1)

graph.add_edge("C1", "C2", length_5)
graph.add_edge("C2", "C3", length_5)
graph.add_edge("C3", "C4", length_5)
graph.add_edge("C4", "F1", length_6)

graph.add_edge("D1", "D2", length_5)
graph.add_edge("D2", "D3", length_5)
graph.add_edge("D3", "D4", length_5)
graph.add_edge("D1", "F5", length_6)

# all other horizontal
graph.add_edge("E1", "F2", length_4)
graph.add_edge("E2", "F3", length_4)
graph.add_edge("E3", "F4", length_4)
graph.add_edge("E4", "F5", length_4)

graph.add_edge("F1", "G1", length_4)
graph.add_edge("F2", "G2", length_4)
graph.add_edge("F3", "G3", length_4)
graph.add_edge("F4", "G4", length_4)

# all other vertical
graph.add_edge("C1", "E1", length_2)
graph.add_edge("F1", "F2", length_2)
graph.add_edge("G1", "G2", length_2)

graph.add_edge("E1", "E2", length_3)
graph.add_edge("F2", "F3", length_3)
graph.add_edge("G2", "G3", length_3)

graph.add_edge("E2", "E3", length_3)
graph.add_edge("F3", "F4", length_3)
graph.add_edge("G3", "G4", length_3)

graph.add_edge("E3", "E4", length_2)
graph.add_edge("F4", "F5", length_2)
graph.add_edge("G4", "D4", length_2)

graph.add_edge("A4", "A15", length_2)



#------------------------------------------------
# Main-Program
#------------------------------------------------

#-------------------------
# Define Functions
#-------------------------


# the function follow_line moves it along a black line (using the IR-sensor)
# until it recognizes an intersection
def follow_line(current_node, next_node):
    global leftSpeed, rightSpeed, follow_line_current_state, follow_line_state_counter, bTerminate, step_count, overhead_counter, bTurnLeft, bTurnRight, MAX_SPEED_LEFT, MAX_SPEED_RIGHT, far_counter, touchsw, bObjectDetected
  
    # state machine for line follower -> move robot
    if follow_line_current_state == 'forward':
        
        # set speeds and motor-direction for forward movement
        bTurnRight = False
        bTurnLeft = False
        leftSpeed = 0.83* 72
        rightSpeed = 0.83* 72

        # adjust turns
        if line_right and not line_left:
            follow_line_current_state = 'turn_right'
            follow_line_state_counter = 0
        elif line_left and not line_right:
            follow_line_current_state = 'turn_left'
            follow_line_state_counter = 0
        
        # outer sensors in IR-sensor-array (1 & 5) are used to 
        # recognize intersection -> far counter as 
        # threshold to debounce them in case they trigger 
        # multiple times on the same line
        # if intersection is detected -> state = stop
        if line_far_left and far_counter > 330:
            follow_line_current_state = 'stop'
            follow_line_state_counter = 0
            far_counter = 0
        
        if line_far_right and far_counter > 330:
            follow_line_current_state = 'stop'
            follow_line_state_counter = 0
            far_counter = 0
        
        # if only center sensor = true -> robot is on path -> forward
        elif (line_center and not line_far_right and not line_far_left):
            follow_line_current_state = 'forward'
            follow_line_state_counter = 0


        # if touch-sensor triggers -> object detected!
        if touchsw.value() == True:
            bObjectDetected = True
            follow_line_current_state = 'stop'

            # stop motors
            leftSpeed = 0 
            rightSpeed = 0
            bTurnRight = False
            bTurnLeft = False
            leftMotor.forward(leftSpeed)
            rightMotor.forward(rightSpeed)
            
        
        
    # set speeds and motor-direction for right turn
    if follow_line_current_state == 'turn_right':
        leftSpeed = 1* MAX_SPEED_LEFT
        rightSpeed = 0.94* MAX_SPEED_LEFT
        bTurnRight = False
        bTurnLeft = True

        if follow_line_state_counter == FOLLOW_LINE_STATE_COUNTER_MAX:
            follow_line_current_state = 'forward'

    # set speeds and motor-direction for left turn
    if follow_line_current_state == 'turn_left':
        leftSpeed = 0.94* MAX_SPEED_LEFT
        rightSpeed = 1* MAX_SPEED_LEFT
        bTurnRight = True
        bTurnLeft = False

        if follow_line_state_counter == FOLLOW_LINE_STATE_COUNTER_MAX:
            follow_line_current_state = 'forward'    
     
    # overhead-state is used to continue robot-movement
    # even if all sensors = false
    # this case can happen even when robot is still on line
    # because of the spacing of the sensors
    # -> overhead counteracts this by moving a little bit further forward
    # if another sensor triggers again the movement continues, if not 
    # it will eventually stop
    if follow_line_current_state == 'overhead':
        
        # counter determines when overhead-distance is reached
        if overhead_counter < 100:
            overhead_counter += 1
            leftSpeed = MAX_SPEED_LEFT
            rightSpeed = MAX_SPEED_RIGHT
            bTurnRight = False
            bTurnLeft = False
            # if any sensor triggers again continue movement
            if (line_center or line_left or line_right):
                follow_line_current_state = 'forward'
        else:
            # otherwise reset counter and stop robot
            overhead_counter = 0
            follow_line_current_state = 'stop' 
        
        
    # set speeds and motor-direction for stop
    if follow_line_current_state == 'stop':
        
        leftSpeed = 0 
        rightSpeed = 0
        bTurnRight = False
        bTurnLeft = False
        follow_line_current_state = 'stop' # commissioning

        if follow_line_state_counter == FOLLOW_LINE_STATE_COUNTER_MAX:
            follow_line_current_state = 'stop'          

    # increment follow_line_state_counter
    follow_line_state_counter += 1
    print("Line-Follower-State:", follow_line_current_state)
    # print sensor values for commissioning
    print(sensor_values[0],sensor_values[1],sensor_values[2],sensor_values[3],sensor_values[4])
    

# the function follow_line_norec moves it along a black line (using the IR-sensor)
# without recognizing intersections
# it is used to move the robot for a certain distance after it just 
# started from a note to prevent false triggering of sensors to detect new intersections
def follow_line_norec(current_node, next_node):
    global leftSpeed, rightSpeed, follow_line_current_state, follow_line_state_counter, step_count, overhead_counter, bTurnLeft, bTurnRight, MAX_SPEED_LEFT, MAX_SPEED_RIGHT, follow_line_counter
  
    # increment follow_line_counter
    follow_line_counter += 1
    # state machine for line follower -> move robot
    if follow_line_current_state == 'forward':
        
        # set speeds and motor-direction for forward movement
        bTurnRight = False
        bTurnLeft = False
        leftSpeed = 0.83* 72
        rightSpeed = 0.83* 72

        # adjust turns
        if line_right and not line_left:
            follow_line_current_state = 'turn_right'
            follow_line_state_counter = 0
        elif line_left and not line_right:
            follow_line_current_state = 'turn_left'
            follow_line_state_counter = 0
        
        # center -> forward
        elif (line_center and not line_far_right and not line_far_left):
            follow_line_current_state = 'forward'
            follow_line_state_counter = 0
        elif (not line_center and not line_far_right and not line_far_left):
            follow_line_current_state = 'forward'
            follow_line_state_counter = 0
            
        
    # set speeds and motor-direction for right turn
    if follow_line_current_state == 'turn_right':
        
        leftSpeed = 1* MAX_SPEED_LEFT
        rightSpeed = 0.94* MAX_SPEED_LEFT
        bTurnRight = False
        bTurnLeft = True

        if follow_line_state_counter == FOLLOW_LINE_STATE_COUNTER_MAX:
            follow_line_current_state = 'forward'

    # set speeds and motor-direction for left turn
    if follow_line_current_state == 'turn_left':
        
        leftSpeed = 0.94* MAX_SPEED_LEFT
        rightSpeed = 1* MAX_SPEED_LEFT
        bTurnRight = True
        bTurnLeft = False

        if follow_line_state_counter == FOLLOW_LINE_STATE_COUNTER_MAX:
            follow_line_current_state = 'forward'    
     
    # overhead-state is used to continue robot-movement
    # even if all sensors = false
    # this case can happen even when robot is still on line
    # because of the spacing of the sensors
    # -> overhead counteracts this by moving a little bit further forward
    # if another sensor triggers again the movement continues, if not 
    # it will eventually stop
    if follow_line_current_state == 'overhead':
        
        # counter determines when overhead-distance is reached
        if overhead_counter < 100:
            overhead_counter += 1
            leftSpeed = MAX_SPEED_LEFT
            rightSpeed = MAX_SPEED_RIGHT
            bTurnRight = False
            bTurnLeft = False
            # if any sensor triggers again continue movement
            if (line_center or line_left or line_right):
                follow_line_current_state = 'forward'
        else:
            # otherwise reset counter and stop robot
            overhead_counter = 0
            
    # no stop state in this function as it is always
    # followed up by the "real" follow_line function which
    # will stop the robot
            

    # increment follow_line_state_counter
    follow_line_state_counter += 1
    print("Line-Follower-State:", follow_line_current_state)
    # print sensor values for commissioning
    print(sensor_values[0],sensor_values[1],sensor_values[2],sensor_values[3],sensor_values[4])
      

# the function get_needed_orientation determines the needed
# orientation for the robot to get from the current node
# to the next node
# -> it utilizes the position data of the nodes
# every node has a x- and y-value (static numbers) 
# depending on its position on the grid (see documentation)
def get_needed_orientation(current_node, next_node):
    global path, needed_orientation

    # reset old value
    needed_orientation = None

    # get x- and y-values from current node 
    node = graph.get_node(current_node)
    if node is not None:
        print("Current", node.x, node.y)
        x_current = node.x
        y_current = node.y
    
    # get x- and y-values from next node 
    node = graph.get_node(next_node)
    if node is not None:
        print("Next", node.x, node.y)
        x_next = node.x
        y_next = node.y


    # IF SIMULATION: ATTENTION - X- & Y-Values from the grid are the other way around in WeBots
    # check if next turn is in x- or y-direction
        
    # if in y
    if x_next == x_current:
        # check if up or down
        if y_next > y_current:
            print("To Next Node -> MOVE UP")
            needed_orientation = "up"
        elif y_next < y_current:
            print("To Next Node -> MOVE DOWN")
            needed_orientation = "down"
            
    # if in X
    if y_next == y_current:
        # check if right or left
        if x_next > x_current:
            print("To Next Node -> MOVE RIGHT")
            needed_orientation = "right"
        elif x_next < x_current:
            print("To Next Node -> MOVE LEFT")
            needed_orientation = "left"

    # return value
    return needed_orientation


# the function pose_robot_orientation() rotates the robot based on a given current- and needed-position
# the positions can either be "up", "down", "left" or "right"
# at first the current and needed position get compared to learn what kind
# of rotation is needed
# if the needed orientation is reached the function call is terminated
# by setting the bExit_pose_robot_orientation boolean = True
# 
# there are 16 possible turn cases:
# rotate 0 degrees: 1) up -> up, 2) left -> left, 3) down -> down, 4) right -> right
# rotate 90 degrees: 5) up -> left, 6) up -> right, 7) left -> up, 8) right -> up, 9) down -> left, 10) down -> right, 11) left -> down, 12) right -> down
# rotate 180 degrees: 13) up -> down, 14) down -> up, 15) left -> right, 16) right -> left
#
# every turn utilizes the "line_counter"-variable to debounce the IR-sensor
# -> sometimes it triggers randomly which causes the turn to stop
# this way it has to be positive for a certain time to make sure it actually reached a black line
def pose_robot_orientation():
    global step_count, leftSpeed, rightSpeed, line_left, line_right, needed_orientation, bExit_pose_robot_orientation, bTurnRight, bTurnLeft, current_orientation, follow_line_current_state, line_counter, far_counter
    print("Step Count:", step_count)
    
    # first check if current and needed position are identical -> no rotation required
    # case 1:
    if (current_orientation == "up" and needed_orientation == "up"):
        bExit_pose_robot_orientation = True
    # case 2:
    if (current_orientation == "left" and needed_orientation == "left"):
        bExit_pose_robot_orientation = True
    # case 3:
    if (current_orientation == "down" and needed_orientation == "down"):
        bExit_pose_robot_orientation = True
    # case 4:
    if (current_orientation == "right" and needed_orientation == "right"):
        bExit_pose_robot_orientation = True
    
    # case 5:
    # if current position is up and needed position is left -> turn robot left 90 degrees
    # use IR-sensor to detect next black line and stop turn accordingly
    if (current_orientation == "up" and needed_orientation == "left"):
        # turn left
        print("TURNING LEFT")
        if line_left:
            # increase line_counter for debouncing
            line_counter += 1
        # turn robot 
        if line_counter < 3:
            # set speeds and direction for motors
            leftSpeed =  0.83 * MAX_SPEED_LEFT
            rightSpeed =  0.83 * MAX_SPEED_RIGHT
            bTurnRight = False
            bTurnLeft = True
        # stop turn if line is reached
        elif line_counter >= 3:
            print("LEFT TURN DONE")
            # update current orientation
            current_orientation = "left"
            print("Current Orientation:", current_orientation)
            #stop motors
            leftSpeed = 0
            rightSpeed = 0
            bTurnRight = False
            bTurnLeft = False
            # terminate function call with exit boolean and reset variables for next movement
            bExit_pose_robot_orientation = True
            follow_line_current_state = 'forward'
            far_counter = 0
    
    # case 6:
    # if current position is up and needed position is right -> turn robot right 90 degrees
    # use IR-sensor to detect next black line and stop turn accordingly
    if (current_orientation == "up" and needed_orientation == "right"):
        # turn right
        print("TURNING RIGHT")
        if line_right:
            # increase line_counter for debouncing
            line_counter += 1
        if line_counter < 3:
            print("debug turn")
            # set speeds and direction for motors
            leftSpeed =  0.83 * MAX_SPEED_LEFT
            rightSpeed =  0.83 * MAX_SPEED_RIGHT
            bTurnRight = True
            bTurnLeft = False
        # stop turn if line is reached
        elif line_counter >= 3:
            print("RIGHT TURN DONE")
            # update current orientation
            current_orientation = "right"
            print("Current Orientation:", current_orientation)
            #stop motors
            leftSpeed = 0
            rightSpeed = 0
            bTurnRight = False
            bTurnLeft = False
            # terminate function call with exit boolean and reset variables for next movement
            bExit_pose_robot_orientation = True
            follow_line_current_state = 'forward'
            far_counter = 0
    
    # case 7:
    # if current position is left and needed position is up -> turn robot right 90 degrees
    # use IR-sensor to detect next black line and stop turn accordingly
    if (current_orientation == "left" and needed_orientation == "up"):
        # turn right
        print("TURNING RIGHT")
        if line_right:
            # increase line_counter for debouncing
            line_counter += 1
        if line_counter < 3:
            print("debug turn")
            # set speeds and direction for motors
            leftSpeed =  0.83 * MAX_SPEED_LEFT
            rightSpeed =  0.83 * MAX_SPEED_RIGHT
            bTurnRight = True
            bTurnLeft = False
        # stop turn if line is reached
        elif line_counter >= 3:
            print("RIGHT TURN DONE")
            # update current orientation
            current_orientation = "up"
            print("Current Orientation:", current_orientation)
            #stop motors
            leftSpeed = 0
            rightSpeed = 0
            bTurnRight = False
            bTurnLeft = False
            # terminate function call with exit boolean and reset variables for next movement
            bExit_pose_robot_orientation = True
            follow_line_current_state = 'forward'
            far_counter = 0
    
    # case 8:
    # if current position is right and needed position is up -> turn robot left 90 degrees
    # use IR-sensor to detect next black line and stop turn accordingly
    if (current_orientation == "right" and needed_orientation == "up"):
        # turn left
        print("TURNING LEFT")
        if line_left:
            # increase line_counter for debouncing
            line_counter += 1
        # turn robot 
        if line_counter < 3:
            # set speeds and direction for motors
            leftSpeed =  0.83 * MAX_SPEED_LEFT
            rightSpeed =  0.83 * MAX_SPEED_RIGHT
            bTurnRight = False
            bTurnLeft = True
        # stop turn if line is reached
        elif line_counter >= 3:
            print("LEFT TURN DONE")
            # update current orientation
            current_orientation = "up"
            print("Current Orientation:", current_orientation)
            #stop motors
            leftSpeed = 0
            rightSpeed = 0
            bTurnRight = False
            bTurnLeft = False
            # terminate function call with exit boolean and reset variables for next movement
            bExit_pose_robot_orientation = True
            follow_line_current_state = 'forward'
            far_counter = 0

    # case 9:
    # if current position is down and needed position is left -> turn robot right 90 degrees
    # use IR-sensor to detect next black line and stop turn accordingly
    if (current_orientation == "down" and needed_orientation == "left"):
        # turn right
        print("TURNING RIGHT")
        if line_right:
            # increase line_counter for debouncing
            line_counter += 1
        if line_counter < 3:
            print("debug turn")
            # set speeds and direction for motors
            leftSpeed =  0.83 * MAX_SPEED_LEFT
            rightSpeed =  0.83 * MAX_SPEED_RIGHT
            bTurnRight = True
            bTurnLeft = False
        # stop turn if line is reached
        elif line_counter >= 3:
            print("RIGHT TURN DONE")
            # update current orientation
            current_orientation = "left"
            print("Current Orientation:", current_orientation)
            #stop motors
            leftSpeed = 0
            rightSpeed = 0
            bTurnRight = False
            bTurnLeft = False
            # terminate function call with exit boolean and reset variables for next movement
            bExit_pose_robot_orientation = True
            follow_line_current_state = 'forward'
            far_counter = 0

    # case 10:
    # if current position is down and needed position is right -> turn robot left 90 degrees
    # use IR-sensor to detect next black line and stop turn accordingly
    if (current_orientation == "down" and needed_orientation == "right"):
        # turn left
        print("TURNING LEFT")
        if line_left:
            # increase line_counter for debouncing
            line_counter += 1
        # turn robot 
        if line_counter < 3:
            # set speeds and direction for motors
            leftSpeed =  0.83 * MAX_SPEED_LEFT
            rightSpeed =  0.83 * MAX_SPEED_RIGHT
            bTurnRight = False
            bTurnLeft = True
        # stop turn if line is reached
        elif line_counter >= 3:
            print("LEFT TURN DONE")
            # update current orientation
            current_orientation = "right"
            print("Current Orientation:", current_orientation)
            #stop motors
            leftSpeed = 0
            rightSpeed = 0
            bTurnRight = False
            bTurnLeft = False
            # terminate function call with exit boolean and reset variables for next movement
            bExit_pose_robot_orientation = True
            follow_line_current_state = 'forward'
            far_counter = 0

    # case 11:
    # if current position is left and needed position is down -> turn robot left 90 degrees
    # use IR-sensor to detect next black line and stop turn accordingly
    if (current_orientation == "left" and needed_orientation == "down"):
        # turn left
        print("TURNING LEFT")
        if line_left:
            # increase line_counter for debouncing
            line_counter += 1
        # turn robot 
        if line_counter < 3:
            # set speeds and direction for motors
            leftSpeed =  0.83 * MAX_SPEED_LEFT
            rightSpeed =  0.83 * MAX_SPEED_RIGHT
            bTurnRight = False
            bTurnLeft = True
        # stop turn if line is reached
        elif line_counter >= 3:
            print("LEFT TURN DONE")
            # update current orientation
            current_orientation = "down"
            print("Current Orientation:", current_orientation)
            #stop motors
            leftSpeed = 0
            rightSpeed = 0
            bTurnRight = False
            bTurnLeft = False
            # terminate function call with exit boolean and reset variables for next movement
            bExit_pose_robot_orientation = True
            follow_line_current_state = 'forward'
            far_counter = 0

    # case 12:
    # if current position is right and needed position is down -> turn robot right 90 degrees
    # use IR-sensor to detect next black line and stop turn accordingly
    if (current_orientation == "right" and needed_orientation == "down"):
        # turn right
        print("TURNING RIGHT")
        if line_right:
            # increase line_counter for debouncing
            line_counter += 1
        if line_counter < 3:
            print("debug turn")
            # set speeds and direction for motors
            leftSpeed =  0.83 * MAX_SPEED_LEFT
            rightSpeed =  0.83 * MAX_SPEED_RIGHT
            bTurnRight = True
            bTurnLeft = False
        # stop turn if line is reached
        elif line_counter >= 3:
            print("RIGHT TURN DONE")
            # update current orientation
            current_orientation = "down"
            print("Current Orientation:", current_orientation)
            #stop motors
            leftSpeed = 0
            rightSpeed = 0
            bTurnRight = False
            bTurnLeft = False
            # terminate function call with exit boolean and reset variables for next movement
            bExit_pose_robot_orientation = True
            follow_line_current_state = 'forward'
            far_counter = 0

    # case 13:
    # if current position is up and needed position is down -> turn robot right 180 degrees
    # use IR-sensor to detect next black line and stop turn accordingly
    if (current_orientation == "up" and needed_orientation == "down"):
        # turn right
        print("TURNING RIGHT")
        if line_right:
            # increase line_counter for debouncing
            line_counter += 1
        if line_counter < 3:
            print("debug turn")
            # set speeds and direction for motors
            leftSpeed =  0.83 * MAX_SPEED_LEFT
            rightSpeed =  0.83 * MAX_SPEED_RIGHT
            bTurnRight = True
            bTurnLeft = False
        # stop turn if line is reached
        elif line_counter >= 3:
            print("RIGHT TURN DONE")
            # update current orientation
            current_orientation = "down"
            print("Current Orientation:", current_orientation)
            #stop motors
            leftSpeed = 0
            rightSpeed = 0
            bTurnRight = False
            bTurnLeft = False
            # terminate function call with exit boolean and reset variables for next movement
            bExit_pose_robot_orientation = True
            follow_line_current_state = 'forward'
            far_counter = 0

    # case 14:
    # if current position is down and needed position is up -> turn robot right 180 degrees
    # use IR-sensor to detect next black line and stop turn accordingly
    if (current_orientation == "down" and needed_orientation == "up"):
        # turn right
        print("TURNING RIGHT")
        if line_right:
            # increase line_counter for debouncing
            line_counter += 1
        if line_counter < 3:
            print("debug turn")
            # set speeds and direction for motors
            leftSpeed =  0.83 * MAX_SPEED_LEFT
            rightSpeed =  0.83 * MAX_SPEED_RIGHT
            bTurnRight = True
            bTurnLeft = False
        # stop turn if line is reached
        elif line_counter >= 3:
            print("RIGHT TURN DONE")
            # update current orientation
            current_orientation = "up"
            print("Current Orientation:", current_orientation)
            #stop motors
            leftSpeed = 0
            rightSpeed = 0
            bTurnRight = False
            bTurnLeft = False
            # terminate function call with exit boolean and reset variables for next movement
            bExit_pose_robot_orientation = True
            follow_line_current_state = 'forward'
            far_counter = 0

    # case 15:
    # if current position is left and needed position is right -> turn robot right 180 degrees
    # use IR-sensor to detect next black line and stop turn accordingly
    if (current_orientation == "left" and needed_orientation == "right"):
        # turn right
        print("TURNING RIGHT")
        if line_right:
            # increase line_counter for debouncing
            line_counter += 1
        if line_counter < 3:
            print("debug turn")
            # set speeds and direction for motors
            leftSpeed =  0.83 * MAX_SPEED_LEFT
            rightSpeed =  0.83 * MAX_SPEED_RIGHT
            bTurnRight = True
            bTurnLeft = False
        # stop turn if line is reached
        elif line_counter >= 3:
            print("RIGHT TURN DONE")
            # update current orientation
            current_orientation = "right"
            print("Current Orientation:", current_orientation)
            #stop motors
            leftSpeed = 0
            rightSpeed = 0
            bTurnRight = False
            bTurnLeft = False
            # terminate function call with exit boolean and reset variables for next movement
            bExit_pose_robot_orientation = True
            follow_line_current_state = 'forward'
            far_counter = 0

    # case 16:
    # if current position is right and needed position is left -> turn robot right 180 degrees
    # use IR-sensor to detect next black line and stop turn accordingly
    if (current_orientation == "right" and needed_orientation == "left"):
        # turn right
        print("TURNING RIGHT")
        if line_right:
            # increase line_counter for debouncing
            line_counter += 1
        if line_counter < 3:
            print("debug turn")
            # set speeds and direction for motors
            leftSpeed =  0.83 * MAX_SPEED_LEFT
            rightSpeed =  0.83 * MAX_SPEED_RIGHT
            bTurnRight = True
            bTurnLeft = False
        # stop turn if line is reached
        elif line_counter >= 3:
            print("RIGHT TURN DONE")
            # update current orientation
            current_orientation = "left"
            print("Current Orientation:", current_orientation)
            #stop motors
            leftSpeed = 0
            rightSpeed = 0
            bTurnRight = False
            bTurnLeft = False
            # terminate function call with exit boolean and reset variables for next movement
            bExit_pose_robot_orientation = True
            follow_line_current_state = 'forward'
            far_counter = 0




# the move_over function is used to position the robot 
# correctly on the intersection
# when the robot recognizes the intersection in the follow_line function it stops
# at this point the wheels are not in the middle of the intersection 
# -> move the robot forward a specific distance so the wheels are in the middle
# of the intersection to enable it to turn around in a smooths circle around its middle-point
def move_over():
    global bExit_move_over, leftSpeed, rightSpeed, move_over_counter, bTurnLeft, bTurnRight

    # move_over_counter is used to stop robot after set distance
    if move_over_counter < 60:
        bTurnRight = False
        bTurnLeft = False
        leftSpeed = 0.97 * MAX_SPEED_LEFT
        rightSpeed = 0.97 * MAX_SPEED_RIGHT
    else:
        leftSpeed = 0
        rightSpeed = 0
        bExit_move_over = True


# the move_back function is used to move the robot back a specific distance
def move_back():
    global bExit_move_back, leftSpeed, rightSpeed, move_back_counter, bTurnLeft, bTurnRight

    # move_back_counter is used to stop robot after set distance
    if move_back_counter < 60:
        bTurnRight = True
        bTurnLeft = True
        leftSpeed = MAX_SPEED_LEFT
        rightSpeed = MAX_SPEED_RIGHT
    else:
        leftSpeed = 0
        rightSpeed = 0
        bExit_move_back = True
        
    

#-------------------------
# Main State-Machine
#-------------------------

# state0 calculates the path for the robot to navigate the maze
# it will be called in 3 cases:
# 1. beginning of the program -> calculate path from start-point to pickup-point
# 2. after box is picked up -> calculate path from pickup-point to place-point
# 3. if obstacle is detected -> calculate path from current-node to either pickup-point or place-point
# to find newest shortest path from its current position while avoiding the path that is blocked
def state0():
    global state, path, bReturn, node_counter, pStartPoint, pPickupPoint, pPlacePoint, bObjectDetected
    print("Step 0 -> Define Start- And Endpoint -> Calculate Shortest Path")
    

    # define start- and endpoint
    print("Start Point:", pStartPoint)
    print("Pick-Up Point:", pPickupPoint)
    print("Place Point:", pPlacePoint)

    # calculate path
    # case 1. beginning of the program -> calculate path from start-point to pickup-point
    if bReturn == False:
        path = graph.a_star(pStartPoint, pPickupPoint)
    # case 2. after box is picked up -> calculate path from pickup-point to place-point
    if bReturn == True:
            path = graph.a_star(pPickupPoint, pPlacePoint)
    # case 3. if obstacle is detected -> calculate path from current-node to either pickup-point or place-point
    # to find newest shortest path from its current position while avoiding the path that is blocked
    if bObjectDetected == True:
        if bReturn == False:
            path = graph.a_star(current_node, pPickupPoint)
        if bReturn == True:
                path = graph.a_star(current_node, pPlacePoint)
        bObjectDetected = False

    # print calculated path and its length
    print("Calculated Path", path, "Path Length", len(path))
    
    # next go to state1 to load current and next node
    state = state1


# state1 loads the current node and next node from the path-list
# in variables to access their data
def state1():
    global state, path, node_counter, current_node, next_node, bReturn, bFinalNode, bObjectDetected, final_node
    print("Step 1 -> Load Current And Next Node")


    # increase node_counter to iterate through nodes in path-list
    node_counter += 1
    
    # if more than 1 node is left robot is on path -> load current and next node
    if node_counter < (len(path)):

        # if object on the way detected (next node is not final)
        if bObjectDetected == True:
            # go to state6 to avoid object
            state = state6

        # else continue on path
        else:
            current_node = path[node_counter -1]
            next_node = path[node_counter]
            print(f"Current Node: {current_node}, Next Node: {next_node}")

            # robot is on path -> move to next node
            state = state2
    else:
        # robot reached final node
        # -> determine if on way to pickup-point or place-point
        if bReturn == False:
            print("Pickup-Point Reached!")
            bFinalNode = True
            bReturn = True
            
            # load final_node
            final_node = path[node_counter]

            # next go to state10 to pickup box
            state = state10
        else:
            print("Place-Point Reached!")
            bFinalNode = True

            # next go to state11 to place box
            state = state11
    

# state2 gets the current and needed orientation of the robot
def state2():
    global state, needed_orientation, current_orientation, line_counter
    print("Step 2 -> Get Current And Needed Orientation")

    print("Current Orientation:", current_orientation)
    
    # call function to get needed orientation
    needed_orientation = get_needed_orientation(current_node, next_node)
    print("Needed Orientation:", needed_orientation)
    
    # reset line_counter used to debounce intersection detection
    line_counter = 0

    # next go to state3 to rotate robot
    state = state3
    

# state3 rotates the robot from its current orientation
# to the needed orientation
def state3():
    global state, needed_orientation, current_orientation, current_node, next_node
    print("Step 3 -> Position (Rotate) Robot To Next Node")

    print("Needed Orientation:", needed_orientation)
    print("Current Orientation:", current_orientation)
    print("Current Node:", current_node)
    print("Next Node:", next_node)

    
    # if function not terminated -> rotate robot with pose_robot_orientation()
    if bExit_pose_robot_orientation == False:
        print("Rotating Robot..")
        pose_robot_orientation()
    else:
        print("Robot Rotated!")

        # next go to state4 to follow the line to next node or obstacle
        state = state4


# state4 moves the robot on the line until it detects an intersection
# or object
def state4():
    global state, step_count, save_x, save_y, follow_line_current_state, bExit_pose_robot_orientation, follow_line_counter, far_counter, bObjectDetected
    print("Step 4 -> Follow Line To Next Node")
    
    # if robot just left prior intersection (node)
    # go a certain distance without looking to recognize
    # the next intersection with follow_line_norec()

    # increase far counter to terminate after certain distance
    far_counter += 1

    # reset exit-boolean for pose_robot_orientation()
    bExit_pose_robot_orientation = False
    if follow_line_counter < 150:
        # move robot away from intersection
        print("Follow Line NoRec")
        follow_line_norec(current_node, next_node)
        # error handling for stop-state
        if follow_line_current_state == 'stop':
             follow_line_current_state = 'forward'
    
    # move robot to next intersection
    else:
        follow_line(current_node, next_node)
    
    # if robot stopped -> check if intersection or object is detected
    if follow_line_current_state == 'stop':
        # if object detected -> call state1 to check if on final node
        # and box has to be picked up or object on path has been detected
        if bObjectDetected == True:
            print("Object Detected!")
            state = state1
            # reset follow_line_counter
            follow_line_counter = 0
        
        # otherwise intersection is detected
        else:
            print("End Of Line Reached!")
            # save current x- and y-values
            save_x = x
            save_y = y
            # next go to state5 to move robot to center of intersection
            state = state5
            # reset follow_line_counter
            follow_line_counter = 0
        
        #reset step_count
        step_count = 0


# state5 moves the robot to the center of the intersection after it is detected
def state5():
    global state, path, bExit_move_over, move_over_counter, node_counter, current_node, next_node
    print("Step 5 -> Moving Robot To Center Of Intersection")
    
    # call move_over function to move robot
    move_over()
    
    # increment move_over_counter to keep track of distance
    move_over_counter += 1
    
     # if function terminated -> delete last node from path-list
    if bExit_move_over == True:
        print("Calculated Path Before:", path, "Path Length:", len(path))
        # if not final node
        if node_counter > 0:
            print("Current Node Before:", current_node)
            print("Next Node Before:", next_node)
            # delete node
            path.pop(node_counter - 1)  
            # decrease node_counter
            node_counter = node_counter - 1
            print("Calculated Path Current:", path, "Path Length", len(path))
            
        # next go to state 1 to load new current and next node and continue
        state = state1

        # reset exit-boolean for move_over()
        bExit_move_over = False
        # reset move_over_counter
        move_over_counter = 0
        

# state6 moves back the robot after an object is detected
def state6(current_node):
    global state, move_back_counter, bExit_move_back

    if not bExit_move_back:
        move_back()
    else:
        move_back_counter = 0
        bExit_move_back = False
        state = state7
    

# state7 gets the current and needed orientation for the 180 degree turn
def state7():
    global state, needed_orientation, current_orientation, line_counter
    print("Step 7 -> Get Current And Needed Orientation For 180 Degree Turn After Obstacle")

    print("Current Orientation:", current_orientation)
    
    # call function to get needed orientation with inversed arguments
    needed_orientation = get_needed_orientation(next_node, current_node)
    print("Needed Orientation:", needed_orientation)
    
    # reset line_counter used to debounce intersection detection
    line_counter = 0

    # next go to state8 to rotate robot for 180 degrees
    state = state8


# state8 rotates the robot from its current orientation
# to the needed orientation (special case 180 degrees)
def state8():
    global state, needed_orientation, current_orientation, current_node, next_node, bBoxPicked
    print("Step 8 -> Position (Rotate) Robot 180 Degrees")

    print("Needed Orientation:", needed_orientation)
    print("Current Orientation:", current_orientation)

    
    # if function not terminated -> rotate robot with pose_robot_orientation()
    if bExit_pose_robot_orientation == False:
        print("Rotating Robot..")
        pose_robot_orientation()
    else:
        print("Robot Rotated!")

        # if the robot comes from picking up the box
        # -> go to state0 and start way to place point
        if bBoxPicked == True:
            state = state0
        else:
            # else object was on the way -> go to state9 to delete blocked edge
            state = state9


# state9 deletes the blocked edge from the graph dataset
def state9():
    global state, graph, current_node, next_node

    # delete blocked edge from graph dataset
    graph.remove_edge(current_node, next_node)

    # next go to state0 to recalculate new path and continue
    state = state0


# state10 picks up the box, gets new orientation values for the robot
def state10():
    global state, bBoxPicked, solenoid, final_node, line_counter, bReturn

    # activate magnet to pick up box
    solenoid.duty(1000)

    # get current and needed orientation for 180 degree turn
    print("Current Orientation:", current_orientation)
    
    # call function to get needed orientation with inversed arguments
    needed_orientation = get_needed_orientation(final_node, current_node)
    print("Needed Orientation:", needed_orientation)
    
    # reset line_counter used to debounce intersection detection
    line_counter = 0

    # set boolean for box picked and return
    bBoxPicked = True
    bReturn = True

    # next go to state8 to rotate robot for 180 degress
    state = state8


# state11 places the box
def state11():
    global state, solenoid

    # deactivate magnet to place the box
    solenoid.duty(0)

    # next go to state99 to terminate program
    state = state99


# state99 terminates the program
def state99():
    global state, bTerminate

    # set bTerminate boolean to end program
    bTerminate = True


# the update function updates the main-state-machine
def update():
    global state
    state()




# set the initial state
state = state0
# set the initial orientation
current_orientation = "up"

# set initial duty-cycle for magnet
solenoid.duty(0)

# initialize global_counter
global_counter = 0

#------------------------------------------------
# Main Loop
#------------------------------------------------

while global_counter < 150 and not bTerminate: # counter used for commissioning -> gets reset below for real usage
    
    # Update sensor readings
    sensor_values = readIRSensors(analog_pins)
    
    global_counter = 0 # ibn
    #global_counter = global_counter + 1 # ibn
        
    # Process sensor data
    line_right = sensor_values[1] > 1300
    line_left = sensor_values[3] > 1000
    line_far_right = sensor_values[0] > 1000
    line_far_left = sensor_values[4] > 1000
    line_center = sensor_values[2] > 1300

    # update the main-state-machine
    update()
    
    # update motor speeds and directions
    if bTurnRight == False and bTurnLeft == False:
        leftMotor.forward(leftSpeed)
        rightMotor.forward(rightSpeed)
    elif bTurnRight == True and bTurnLeft == False:
        leftMotor.forward(leftSpeed)
        rightMotor.backwards(rightSpeed)
    elif bTurnRight == False and bTurnLeft == True:
        leftMotor.backwards(leftSpeed)
        rightMotor.forward(rightSpeed)
    elif bTurnRight == True and bTurnLeft == True:
        leftMotor.backwards(leftSpeed)
        rightMotor.backwards(rightSpeed)
            

