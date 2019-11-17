import os
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import shutil
import matplotlib.pyplot as plt


class evaluation():
    def __init__(self, gaze_data_file_name, img_file_name, predict_file_name):
        self.img_dir = r'C:\Users\zhangzhida\Desktop\EyeGazePipeline\data\screenshot'
        self.gaze_data_dir = r'C:\Users\zhangzhida\Desktop\EyeGazePipeline\observer'
        self.predict_dir = r'C:\Users\zhangzhida\Desktop\EyeGazePipeline\pipeline'
        self.gaze_data_file_name = gaze_data_file_name
        self.img_file_name = img_file_name
        self.predict_file_name = predict_file_name

        # csv_filename = os.path.join(os.getcwd(), 'eval_prediction.csv')
        # if not os.path.exists(self.csv_filename):

        self.eval_table = pd.DataFrame(columns=['img_name', 'img_time', 'gaze_time', 'real_label'])
        # self.eval_table.to_csv(self.csv_filename, index=False)

        self.gaze_data = pd.read_csv(os.path.join(self.gaze_data_dir, self.gaze_data_file_name))
        print("The shape of gaze_data.csv: ".format(self.gaze_data.shape))

        self.img_file = pd.read_csv(os.path.join(self.gaze_data_dir, self.img_file_name)) 
        print("The shape of gaze_data.csv: ".format(self.img_file.shape))

        self.prediction_file = pd.read_csv(os.path.join(self.gaze_data_dir, self.predict_file_name)) 
        print("The shape of gaze_data.csv: ".format(self.prediction_file.shape))


    def __del__(self):
        if os.path.exists(self.csv_filename):
            os.remove(self.csv_filename)

        if os.path.exists(self.gaze_data_file_name):
            os.remove(self.gaze_data_file_name)

        if os.path.exists(self.img_file_name):
            os.remove(self.img_file_name)

        if os.path.exists(self.predict_file_name):
            os.remove(self.predict_file_name)


    def eval_res(self, delay_threshold=0.01):  
        # self.delay_threshold = delay_threshold 
        i = 0
        j = 0 
        cnt = 0
        # df_eval = pd.read_csv(self.csv_filename)
        # df_predict = pd.read_csv(self.predict_dir)

        while i < self.img_file.shape[0] and j < self.gaze_data.shape[0]:
            img = self.img_file.iloc[i]
            gaze_record = self.gaze_data.iloc[j]
            
            gaze_point_time = gaze_record['timestamp']
            img_time = img['time']
            # skip time == null 
            if gaze_point_time != gaze_point_time:
                j += 1
                continue
                
            diff_time = gaze_point_time - img_time
            # print(i, j, diff_time)
            if abs(diff_time) < delay_threshold:
                print(i, j, diff_time)

                # if gaze_record['FPOGY'] is None: continue
                if gaze_record['FPOGX'] is None:
                    j += 1
                    continue
                elif gaze_record['FPOGX'] < 0.5:
                    self.eval_table.loc[cnt] = [img['img_name'], img_time, gaze_point_time, 0] # left
                else:
                    self.eval_table.loc[cnt] = [img['img_name'], img_time, gaze_point_time, 1] # right

                cnt += 1
                i += 1

            if gaze_point_time < img_time:
                j += 1
            else:
                i += 1

        # res = pd.merge(df_eval, df_predict, on='img_name')  
        self.eval_table.merge(self.prediction_file, on='img_name')
        # df_eval.to_csv(self.csv_filename, index=False)
        # return self.eval_table


    def eval_plot(self):
        # self.eval_table
        # self.eval_table.plot(x='img_time', y=['real_label', 'predict_label'], figsize=(10,5), grid=True)
        plt.plot(self.eval_table['img_time'], self.eval_table['real_label'], 'b-', label="real_label")
        plt.plot(self.eval_table['img_time'], self.eval_table['predict_label'], 'r-', label="predict_label")
        plt.legend(loc='best')
        plt.savefig(os.path.join(os.getcwd(), 'evaluation.img'))
        plt.show()


if __name__ == "__main__":
    pass