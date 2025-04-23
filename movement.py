import logging
import time
from threading import Event

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils.power_switch import PowerSwitch

from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

from cflib.positioning.motion_commander import MotionCommander

import cv2
import balls

URI = [
    "",
    "radio://0/80/2M/E7E7E7E701",
    "radio://0/80/2M/E7E7E7E702",
    "radio://0/80/2M/E7E7E7E703",
    "radio://0/90/2M/E7E7E7E704",
    "radio://0/90/2M/E7E7E7E705",
    "radio://0/90/2M/E7E7E7E706",
    "radio://0/100/2M/E7E7E7E707",
    "radio://0/100/2M/E7E7E7E708",
    "radio://0/100/2M/E7E7E7E709",
]

# URI to the Crazyflie to connect to
uri = URI[7]  # TODO: change the uri based on your crazyflie number
'''
1: radio://0/80/2M/E7E7E7E701
2: radio://0/80/2M/E7E7E7E702
3: radio://0/80/2M/E7E7E7E703
4: radio://0/90/2M/E7E7E7E704
5: radio://0/90/2M/E7E7E7E705
6: radio://0/90/2M/E7E7E7E706
7: radio://0/100/2M/E7E7E7E707
8: radio://0/100/2M/E7E7E7E708
9: radio://0/100/2M/E7E7E7E709
'''

deck_attached_event = Event()


def simple_connect():
    # Test connection. You can use this function to check whether you can connect to crazyflie
    print("Yeah, I'm connected! :D")
    time.sleep(3)
    print("Now I will disconnect :'(")


logging.basicConfig(level=logging.ERROR)


def read_parameter(scf, logconf):
    # TODO: read roll, pitch, yaw information from the crazyflie and print them in the terminal

    # Parameters:
    #       scf: SyncCrazyflie object, a synchronous Crazyflie instance
    #       logconf: log configuration
    with SyncLogger(scf, lg_stab) as logger:
        for log_entry in logger:
            timestamp = log_entry[0]
            data = log_entry[1]
            logconf_name = log_entry[2]
            print('[%d][%s]: %s' % (timestamp, logconf_name, data))
            break


def up(mc, dis):
    # TODO: move the crazyflie up

    # Parameters:
    #       mc: motion commander
    #       dis: a floating number representing move up distance
    mc.up(dis)


def down(mc, dis):
    # TODO: move the crazyflie down

    # Parameters:
    #       mc: motion commander
    #       dis: a floating number representing move down distance
    mc.down(dis)


def forward(mc, dis):
    # TODO: move the crazyflie forward

    # Parameters:
    #       mc: motion commander
    #       dis: a floating number representing forward distance
    mc.forward(dis)


def backward(mc, dis):
    # TODO: move the crazyflie backward

    # Parameters:
    #       mc: motion commander
    #       dis: a floating number representing backward distance
    mc.back(dis)


def left(mc, dis):
    # TODO: turn the crazyflie left

    # Parameters:
    #       mc: motion commander
    #       deg: a floating number representing the degree to turn left
    mc.left(dis)


def right(mc, dis):
    # TODO: turn the crazyflie right

    # Parameters:
    #       mc: motion commander
    #       deg: a floating number representing the degree to turn right
    mc.right(dis)


def land(mc):
    # land the crazyflie

    # Parameters:
    #       mc: motion commander
    mc.stop()


def calculate_movement(image, origin_box, current_box):
    """
    Control algorithm for the drone position based on given origin box and current 
    bounding box of object. Outputs a movement direction and magnitude.

    TODO: utilize origin_box instead of START_SIZE to calculate error in control algo
    """

    # adjust for sensitivity to forward & backward movement of target
    MARGIN = 100

    # determine which direction to display
    dir_text = ""
    diff: balls.BoundingBoxDelta = current_box - origin_box
    print(diff)
    if abs(diff.dcenter_x) > abs(diff.dcenter_y):
        dir_text = "right" if diff.dcenter_x > 0 else "left"
    else:
        dir_text = "down" if diff.dcenter_y > 0 else "up"

    if diff.dh > MARGIN and diff.dw > MARGIN:
        dir_text = "backward"
    elif diff.dh < -MARGIN and diff.dw < -MARGIN:
        dir_text = "forward"

    # add direction text to bottom right of the camera feed
    text = dir_text
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    text_x = image.shape[1] - text_size[0] - 10
    text_y = image.shape[0] - 20

    # add white bg for text
    cv2.rectangle(image,
                  (text_x - 5, text_y - text_size[1] - 5),
                  (text_x + text_size[0] + 5, text_y + 5),
                  (255, 255, 255),
                  -1)

    # add text
    cv2.putText(image, text, (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    return dir_text


def move(mc, direction, magnitude):
    """
    Function that actually moves the drone in the given direction with the given magnitude.
    """

    if direction == 'up':  # up
        up(mc, magnitude)
    elif direction == 'down':  # down
        down(mc, magnitude)
    elif direction == 'forward':  # forward
        forward(mc, magnitude)
    elif direction == 'backward':  # backward
        backward(mc, magnitude)
    elif direction == 'left':     # turn left
        left(mc, magnitude)
    elif direction == 'right':     # turn right
        right(mc, magnitude)


def param_deck_flow(_, value_str):
    # Check whether positioning deck is connected or not

    value = int(value_str)
    print(value)
    if value:
        deck_attached_event.set()
        print('Deck is attached!')
    else:
        print('Deck is NOT attached!')


# def fly_commander(scf, lg_stab, mc, SLEEP_TIME=0.3):
#     # Control the crazyflie to following the input command after taking off and before landing

#     command = ""
#     while (command != 'e'):
#         command = input()
#         command = command.strip()
#         if command == 'e':
#             break
#         elif command == 'i':     # read parameter
#             read_parameter(scf, lg_stab)
#         elif command[0] == 'u':  # up
#             dis = float(command.split()[1])
#             moving_up(mc, dis)
#         elif command[0] == 'd':  # down
#             dis = float(command.split()[1])
#             moving_down(mc, dis)
#         elif command[0] == 'f':  # forward
#             dis = float(command.split()[1])
#             forwarding(mc, dis)
#         elif command[0] == 'b':  # backward
#             dis = float(command.split()[1])
#             backwarding(mc, dis)
#         elif command[0] == 'l':     # turn left
#             deg = float(command.split()[1])
#             turning_left(mc, deg)
#         elif command[0] == 'r':     # turn right
#             deg = float(command.split()[1])
#             turning_right(mc, deg)
#         elif command == 'n':         # land
#             landing(mc)
#             return


def base_commander(scf, lg_stab, DEFAULT_HEIGHT=0.5, SLEEP_TIME=0.3):
    # Control the crazyflie to following the input command
    mc = None
    print("crazyflie takes off")
    # TODO: let the crazyflie to take off
    #      You can call fly_commander(scf, lg_stab, mc) to deal with flying part
    return MotionCommander(scf, default_height=DEFAULT_HEIGHT)


if __name__ == '__main__':
    cflib.crtp.init_drivers()

    lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
    lg_stab.add_variable('stabilizer.roll', 'float')
    lg_stab.add_variable('stabilizer.pitch', 'float')
    lg_stab.add_variable('stabilizer.yaw', 'float')

    group = 'stabilizer'
    name = 'estimator'

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        scf.cf.param.add_update_callback(group="deck", name="bcLighthouse4",
                                         cb=param_deck_flow)
        time.sleep(1)

        base_commander(scf, lg_stab)
