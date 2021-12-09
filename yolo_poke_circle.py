
from yolo_poke_network_menu_navigator import *
from yolo_state_tracker_opencv import *
from switch_button_press import *
from opencv_yolo import YOLO

import datetime
datetime_object = datetime.datetime.now()
print(datetime_object)

import logging
log_filename = 'logs/runner_%s.log' % (datetime_object)
logging.basicConfig(filename=log_filename, filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.warning('This will get logged to a file')
logging.info('This will info message get logged to a file')


def process_live_video_feed2():
    import os

    state = WildState()
    state.is_network_match = True
    i = 0

    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_FFMPEG,True)
    cam.set(cv2.CAP_PROP_FPS,30)
#    cam.set(cv2.CAP_PROP_BUFFERSIZE,0)

#    _fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#    _out = cv2.VideoWriter("test_poke.mp4", _fourcc, 20.0, (1920,1080))

    i = 0
    actionCoolDown = time.time()
    wait_threshold = 0.2
    action = None
    while(True):
        if action is not None:
            for i in range(5):
                cam.grab()
        action, done = None, False
        ret,image = cam.read()
        image = cv2.resize(image, (1280, 720), interpolation = cv2.INTER_AREA)
#        if i % 5 == 0:
#            cv2.imshow('frame',frame)
#        _out.write(frame);

#        if len(labels_boxes) > 0:
#            print(labels_boxes)

        if time.time() - actionCoolDown >= wait_threshold: #some  value
            labels_boxes = yolo.process_image(image)

            if len(labels_boxes) > 0:
#                print(labels_boxes)
                pass
            else:
                sleep(0.01)
                action = 'clear sleep'
                continue

            #
            #  process both frames NOW !
            #
            action, done, wait = state.process_frame(image, labels_boxes)
            if action is not None:
                wait_threshold = wait
            else:
                wait_threshold = 0
        else:
            pass

        # reset time to make move
        if action is not None:
            print('Just wait a second')
            send(action.serial_rep())
            actionCoolDown = time.time()
            i += 1
#            save_file = 'frame_%d_%s.jpg' % (i, action.serial_rep())
#            cv2.imwrite(save_file, image)


#        print('Performing Action?: ', action)
#        print('Done?',done)
#        cv2.imshow('image2  www',image)
#        if cv2.waitKey(1) & 0xFF == ord('q'):
#            break

#        time.sleep(1)
#        if is_done or i > 100:
        if done:
            break
            """
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break
        i += 1
        if i == 1000:
            break
            """
    cam.release()
#    _out.release()
    cv2.destroyAllWindows()


def start_cycle(trainer_name, style):
    import os
    network_state = NetworkState()

    wild_state = WildState(style, trainer_name)
    wild_state.is_network_match = True

    curr_state = network_state
    i = 0

    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_FFMPEG,True)
    cam.set(cv2.CAP_PROP_FPS,30)
#    cam.set(cv2.CAP_PROP_BUFFERSIZE,0)

#    _fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#    _out = cv2.VideoWriter("test_poke.mp4", _fourcc, 20.0, (1920,1080))

    i = 0
    actionCoolDown = time.time()
    wait_threshold = 0.2
    action = None
    while(True):
        if action is not None:
            for i in range(5):
                cam.grab()
        action, done = None, False
        ret,image = cam.read()
        image = cv2.resize(image, (1280, 720), interpolation = cv2.INTER_AREA)
#        if i % 5 == 0:
#            cv2.imshow('frame',frame)
#        _out.write(frame);


        if time.time() - actionCoolDown >= wait_threshold: #some  value
            labels_boxes = yolo.process_image(image)
            if len(labels_boxes) > 0:
#                print(labels_boxes)
                pass
            #
            #  process both frames NOW !
            #
            action, done, wait = curr_state.process_frame(image, labels_boxes)
            actionCoolDown = time.time()
            if action is not None:
                wait_threshold = wait
            else:
                wait_threshold = wait
        else:
            pass

        # reset time to make move
        if action is not None:
            print('Just wait a second')
            send(action.serial_rep())
            actionCoolDown = time.time()
            i += 1
#            save_file = 'frame_%d_%s.jpg' % (i, action.serial_rep())
#            cv2.imwrite(save_file, image)


        if done:
            # reset states
            if curr_state == network_state:
                print('Network portion done, moving to game')
                logging.info('Network portion done, moving to game')
                wild_state = WildState(trainer_name, style)
                wild_state.is_network_match = True
                curr_state = wild_state
            else:
                print('Game portion done, moving to Network')
                logging.info('Game portion done, moving to Network')
                network_state = NetworkState()
                curr_state = network_state
                logging.info('\n\nNet Match Begin\n\n')

    cam.release()
#    _out.release()
    cv2.destroyAllWindows()




if __name__ == '__main__':

    yolo = YOLO(**{
                "score" : 0.8,
                "gpu_num" : 0,
                }
               )

    trainer_name = 'thunder'
    style  = NETWORK_STYLE.RANDO_BOT

    if style == NETWORK_STYLE.HONORABLE_SALAD:
        graph_options = tf.GraphOptions(place_pruned_graph =False)
        config = tf.ConfigProto(allow_soft_placement=True, log_device_placement=True, graph_options=graph_options)
        config = tf.ConfigProto()
        # Avoid warning message errors
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        BUTTON_PRESS_DELAY = 0.2

        # Allowing GPU memory growth
        config.gpu_options.allow_growth = True
        K.clear_session()

        button_press_pool = Pool(1)

        use_gpu = False
        if not use_gpu:
            config = tf.ConfigProto()

        with tf.Session(config=config):
            start_cycle(trainer_name, style)
    else:
        start_cycle(trainer_name, style)

    i = 1/0
