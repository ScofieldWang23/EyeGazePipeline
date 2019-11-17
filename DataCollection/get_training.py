import os
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import shutil


class AddLable():
    def __init__(self, gaze_data_file_name, result_dir_name):
        self.base_dir = os.getcwd()
        self.result_dir = os.path.join(self.base_dir, result_dir_name)
        self.num_of_cameras = 2
        self.gaze_data = pd.read_csv(os.path.join(self.base_dir, self.gaze_data_file_name))
        print("The shape of gaze_data.csv: ".format(self.gaze_data.shape))


    def __del__(self):
        pass


    def move_to_result_directory(self, filename, source_dir, sub_dir):
        print("move has been made!")
        # create directory if not exists
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
        
        if not os.path.exists(os.path.join(self.result_dir, sub_dir)):
            os.makedirs(os.path.join(self.result_dir, sub_dir))
        
        destination_file_name = os.path.join(self.result_dir, sub_dir, filename)
        source_filename = os.path.join(source_dir, filename)
        # os.rename(destination_file_name)
        shutil.copy2(source_filename, destination_file_name)


    def process_raw_directory(self, id_camera):
        raw_photo_dir_i_cam = os.path.join(self.base_dir, 'face' + str(id_camera))
        # iterate photo directory and .csv file
        list_raw_photo_directory = os.listdir(raw_photo_dir_i_cam)
        list_raw_photo_directory.sort()
        delimeter = "_"
        delay_threshold = 0.01

        i = 0
        j = 0 
        while i < len(list_raw_photo_directory) and j < self.gaze_data.shape[0]:
            raw_photo_name = list_raw_photo_directory[i]
            gaze_record = self.gaze_data.iloc[j]
            
            gaze_point_timestamp = gaze_record['timestamp']
            raw_photo_timestamp = float(raw_photo_name.split(delimeter)[-1][:-4])
            if gaze_point_timestamp != gaze_point_timestamp:
                j += 1

            diff_time = gaze_point_timestamp - raw_photo_timestamp

            # if valid, with delay smaller than threshold
            if abs(diff_time) < delay_threshold:
                # print(diff_time)
                if gaze_record['FPOGX'] is None:
                    j += 1
                    continue
                elif gaze_record['FPOGX'] < 0.5:
                    self.move_to_result_directory(raw_photo_name, raw_photo_dir_i_cam, self.result_dir, r'left')
                else:
                    self.move_to_result_directory(raw_photo_name, raw_photo_dir_i_cam, self.result_dir, r'right')
                    
                i += 1
                # print(idx_of_camera, gaze_point_timestamp, raw_photo_timestamp)     

            if gaze_point_timestamp < raw_photo_timestamp:
                j += 1
            else:
                i += 1
    


if __name__ == "__main__":
    obj = AddLable('gaze_data.csv', 'preparation')
    for i in range(obj.num_of_cameras):
        obj.process_raw_directory(i)
    pass


    