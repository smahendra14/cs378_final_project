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
uri = URI[1]  # TODO: change the uri based on your crazyflie number
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
            origin_box = None
            current_box = None
            while True:
                ai_deck_img = ai_deck.get_img()
                print("got img from ai deck")

                key_pressed = cv2.waitKey(1) & 0xFF
                if key_pressed == ord(' '):  # Check if space bar is pressed
                    # update origin box on space bar press
                    origin_box = balls.calibrate_origin_box(ai_deck_img)
                    print(f"calibrated origin box: {origin_box}")
                elif key_pressed == ord('l'):  # Check if 'l' is pressed
                    # land the drone and break loop
                    print("initiating land...")
                    movement.land(mc)
                    break

                if origin_box is not None: 
                    # get the current bounding box
                    current_box = balls.get_bounding_box(ai_deck_img)
                    print(f"got current bounding box: {current_box}")

                    # calculate direction and magnitude of expected movement based
                    # on origin box and bounding box
                    drone_should_move_this_direction = movement.calculate_movement(
                        ai_deck_img, origin_box, current_box)
                    print(f"drone moving {drone_should_move_this_direction}...")

                    # now move the drone in the outputted direction & magnitude
                    movement.move(mc, drone_should_move_this_direction, 0.01)

                cv2.imshow("camera feed", ai_deck_img)
