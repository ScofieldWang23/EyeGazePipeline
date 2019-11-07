import pyautogui
import time
import cv2
import numpy as np
import threading
import sys
import os
import multiprocessing

from publisher import Publisher
from face_detector import FaceDetector
from eyegaze import Eyegaze

class TimeControl:
    '''
    batch_num: num. if is -1, means unlimited num
    batch_interval: the interval between 2 batches
    unit_num: the num of unit in 1 batch
    unit_interval:
    is_unit_even: bool. if true, then unit_interval * unit_num == batch_interval

    '''
    def __init__(self, batch_num, batch_interval, unit_num, unit_interval=None, is_unit_even = None):
        if batch_num < 0:
            self.batch_num = sys.maxsize
        else:
            self.batch_num = batch_num
        self.batch_interval = batch_interval
        self.unit_num = unit_num
        self.unit_interval = unit_interval
        self.is_unit_even = is_unit_even


class Observer:
    def __init__(self, base_dir):
        self.publisher = Publisher()
        self.publisher.declare_queue('hello')
        self.base_dir = base_dir
        self.csv_filename = 'screenshot_list.csv'
        self.face_detector = FaceDetector()
        self.cap0 = cv2.VideoCapture()
        self.cap0.open(0)
        self.eyegaze_process = None

    def __del__(self):
        # self.cap0.release()
        # if self.eyegaze_process is not None:
        #     self.eyegaze_process.shutdown()
        self.cap0.release()

    def one_screenshot(self):
        '''

        :param base_dir:
        :return:
        '''
        timestamp = str(time.time())
        face_img_path = self.base_dir + '/' + timestamp + ".jpeg"

        ret0, mycapture = self.cap0.read()
        # mycapture = pyautogui.screenshot()
        # mycapture = cv2.cvtColor(np.array(mycapture), cv2.COLOR_RGB2BGR)

        if mycapture is None:
            print("capture null")
            return

        # cv2.imwrite(path, img)
        print('saved to ' + face_img_path + " at " + timestamp)

        # detect face
        face_filename = "face_" + timestamp + ".jpeg"
        self.face_detector.detect(mycapture, face_img_path)

        # write to csv
        self._write_to_csv(self.csv_filename, face_img_path, timestamp)

        # publish message
        self.publisher.publish(face_img_path)

        # return [path]

    def _write_to_csv(self, csv_filename, path, timestamp):
        if not os.path.exists(csv_filename):
            file = open(csv_filename, 'w')
            file.close()

        with open(csv_filename, 'a') as fd:
            fd.write(path + ',' + timestamp + '\n')

    def screenshots(self, time_control: TimeControl):
        for i in range(time_control.batch_num):
            batch_start_time = time.time()
            for j in range(time_control.unit_num):
                # self.one_screenshot()
                unit_start_time = time.time()

                # threading.Thread(target=self.one_screenshot(), args=(), daemon=True)
                p1 = multiprocessing.Process(target=self.one_screenshot(), args=(), daemon=True)
                p1.start()

                unit_end_time = time.time()

                time_to_sleep = max(0, time_control.unit_interval - unit_end_time + unit_start_time)
                time.sleep(time_to_sleep)

            batch_end_time = time.time()
            time_to_sleep = max(0, time_control.batch_interval - batch_end_time + batch_start_time)

            time.sleep(time_to_sleep)

    @staticmethod
    def run_eyegaze():
        HOST = '127.0.0.1'
        PORT = 4242
        base_dir = "C:\\Users\\zhangzhida\\Desktop\\EyeGazePipeline\\data\\" # this shoud be changed in Mac

        eyegaze = Eyegaze(HOST, PORT, base_dir)
        eyegaze.run_gazepoint()

    def run(self, time_control: TimeControl, use_eyegaze=False):

        # open a new process to run the eyegaze program
        if use_eyegaze is True:
            self.eyegaze_process = multiprocessing.Process(target=self.run_eyegaze, args=())
            self.eyegaze_process.start()
            print(self.eyegaze_process.pid)

        self.screenshots(time_control)


if __name__ == '__main__':
    # filepath = "C:\\Users\\zhangzhida\\Desktop\\EyeGazePipeline\\data\\screenshot"
    filepath = "/Users/weixin/Desktop/EyeGazePipeline/data/faces"
    observer = Observer(filepath)
    # time control on screenshot
    time_control = TimeControl(batch_num=2, batch_interval=5, unit_num=5, unit_interval=0.1)

    observer.run(time_control, use_eyegaze=True) # default is False

