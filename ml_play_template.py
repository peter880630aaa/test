"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    ball_x_before = 100
    ball_y_before = 395
    destination_x = 100
    save = 0

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        ball_x = scene_info.ball[0]
        ball_y = scene_info.ball[1]
        platform_x = scene_info.platform[0]
        f = scene_info.frame

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            if ball_y > 130 and ball_y < 380 and f > save:
                if ball_x > ball_x_before and ball_y > ball_y_before :
                    save = ((400 - ball_y) / 7) + 1 + f
                    t = ball_y + (200 - ball_x)
                    if (400 - t) >= 200 :
                        destination_x = 200 - t
                    else :
                        destination_x = t - 200
                elif ball_x < ball_x_before and ball_y > ball_y_before :
                    save = ((400 - ball_y) / 7) + 1 + f
                    t = ball_y + ball_x
                    if (400 - t) >= 200 :
                        destination_x = t
                    else :
                        destination_x = 400 - t
            elif ball_y <= 130 :
                destination_x = 100
            
            if platform_x + 20 >= destination_x - 5 and platform_x + 20 <= destination_x + 5 :
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            elif platform_x + 20 < destination_x :
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            elif platform_x + 20 > destination_x :
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            else :
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
        
        ball_x_before = ball_x
        ball_y_before = ball_y
