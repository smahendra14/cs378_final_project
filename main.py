import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig
from cflib.positioning.motion_commander import MotionCommander

import time
import movement
import balls
import ai_deck
import cv2


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

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
    lg_stab.add_variable('stabilizer.roll', 'float')
    lg_stab.add_variable('stabilizer.pitch', 'float')
    lg_stab.add_variable('stabilizer.yaw', 'float')

    DEFAULT_HEIGHT = 0.5

    mc = None
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        scf.cf.param.add_update_callback(group="deck", name="bcLighthouse4",
                                         cb=movement.param_deck_flow)
        time.sleep(1)
        with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            START_SIZE = 0
            bounding_box = None
            while (1):
                ai_deck_img = ai_deck.get_img()
                print("got img from ai deck")

                # update start size on space bar press
                if cv2.waitKey(1) & 0xFF == ord(' '):  # Check if space bar is pressed
                    bounding_box = balls.get_bounding_box(ai_deck_img)
                    print(f"updated bounding box: {bounding_box}")

                if cv2.waitKey(1) & 0xFF == ord('l'):  # Check if 'l' is pressed
                    movement.land()

                if bounding_box is not None:
                    drone_should_move_this_direction = balls.move_based_on_balls(
                        ai_deck_img, bounding_box, START_SIZE)
                    print(drone_should_move_this_direction)
                    movement.move(mc, drone_should_move_this_direction, 0.01)
