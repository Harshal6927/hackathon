from datetime import datetime
import cv2
import csv
import os


class VideoCamera(object):
    def __init__(self):
        try:
            # self.video = cv2.VideoCapture(0)
            global sleep_time
            global file_name
            sleep_time = 0
            file_name = [f for f in os.listdir(
                'static/uploads/') if os.path.isfile(os.path.join('static/uploads/', f))]
            file_name = 'static/uploads/' + file_name[0]
            self.video = cv2.VideoCapture(file_name)
            with open('output.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['Date and Time', 'Vehicle Count'])
        except Exception as e:
            print(f'[__init__ ERROR]: {e}')

    def __del__(self):
        try:
            self.video.release()

            global file_name
            os.remove(file_name)
        except Exception as e:
            print(f'[__del__ ERROR]: {e}')

    def get_frame(self):
        global sleep_time
        success, frame = self.video.read()
        if success:
            cars_cascade = cv2.CascadeClassifier('cars.xml')
            frame = cv2.resize(frame, (848, 480))
            frame_gray = frame[260:480, 0:848]
            frame_gray = cv2.cvtColor(frame_gray, cv2.COLOR_BGR2GRAY)
            frame_gray = cv2.GaussianBlur(frame_gray, (5, 5), 0)
            cars = cars_cascade.detectMultiScale(frame_gray, 1.1, 1)
            var = 0
            for (x, y, width, hight) in cars:
                y += 260
                cv2.rectangle(frame, (x, y), (x + width,
                                              y + hight), (255, 255, 0), 2)
                var += 1
            print(f'[INFO]: {var} cars detected')
            dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            if int(dt_string[-1]) % 2 == 0:
                if sleep_time == 0:
                    sleep_time = 1
                    with open('output.csv', 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([dt_string, var])
            else:
                sleep_time = 0
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()
        else:
            print('[INFO]: No frame')
