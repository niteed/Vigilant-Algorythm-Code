import cv2

class VideoCamera(object):

    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def get_frame(self):
            ret , frame = self.cap.read()
            if ret:
                ret, jpeg = cv2.imencode('.jpg', frame)
                return jpeg.tobytes()
    
    def save_frame(self):
        ret , frame = self.cap.read()
        return frame
