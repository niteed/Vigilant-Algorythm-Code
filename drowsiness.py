from imutils import face_utils
import numpy as np
import imutils
import dlib
import cv2

class Drowsy(object):

    def __init__(self):
        self.eye_thresh = 0.3
        self.eye_consec_frames = 50
        self.mouth_thresh = 0.4
        self.mouth_consec_frames = 50

        self.eye_count = 0
        self.mouth_count = 0
        self.yawn_alarm = False
        self.sleep_alarm = False

        self.WHITE_COLOR = (255, 255, 255)
        self.YELLOW_COLOR = (0, 255, 255)
        self.RED_COLOR = (0, 0, 255)
        self.GREEN_COLOR = (0, 255, 0)
        self.BLUE_COLOR = (255, 0, 0)
        self.BLACK_COLOR = (0, 0, 0)

        self.w, self.h = 60, 35

        self.shape_predictor = "model/shape_predictor_68_face_landmarks.dat"
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(self.shape_predictor)

        #self.fbApp = firebase.FirebaseApplication('https://vigilant-73f45-default-rtdb.firebaseio.com/', None)

    # Grab the indexes of the facial landmarks for the left and right eye and mouth respectively
        (self.lStart, self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (self.rStart,
         self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        (self.mStart, self.mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]
    
    # Returns EAR given eye landmarks
    def eye_aspect_ratio(self, eye):
        # Compute the euclidean distances between the two sets of
        # vertical eye landmarks (x, y)-coordinates
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])

    # Compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
        C = np.linalg.norm(eye[0] - eye[3])

    # Compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)

    # Return the eye aspect ratio
        return ear

    # Returns MAR given eye landmarks
    def mouth_aspect_ratio(self, mouth):
        # Compute the euclidean distances between the three sets
        # of vertical mouth landmarks (x, y)-coordinates
        A = np.linalg.norm(mouth[13] - mouth[19])
        B = np.linalg.norm(mouth[14] - mouth[18])
        C = np.linalg.norm(mouth[15] - mouth[17])

    # Compute the euclidean distance between the horizontal
    # mouth landmarks (x, y)-coordinates
        D = np.linalg.norm(mouth[12] - mouth[16])

    # Compute the mouth aspect ratio
        mar = (A + B + C) / (2 * D)

    # Return the mouth aspect ratio
        return mar

    def check_drowsy(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        contrast = 1.25
        brightness = 50
        frame[:, :, 2] = np.clip(
            contrast * frame[:, :, 2] + brightness, 0, 255)
        frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
        frame = imutils.resize(frame, width=480)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = self.detector(gray)
        if len(rects) > 0:
            rect = rects[0]
        else:
            return 0,0

        shape = self.predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        mouth = shape[self.mStart:self.mEnd]
        leftEye = shape[self.lStart:self.lEnd]
        rightEye = shape[self.rStart:self.rEnd]

        mar = self.mouth_aspect_ratio(mouth)
        leftEAR = self.eye_aspect_ratio(leftEye)
        rightEAR = self.eye_aspect_ratio(rightEye)
        ear = (leftEAR + rightEAR) / 2.0
        diff_ear = np.abs(leftEAR - rightEAR)

        mouthHull = cv2.convexHull(mouth)
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [mouthHull], -1, self.YELLOW_COLOR, 1)
        cv2.drawContours(frame, [leftEyeHull], -1, self.YELLOW_COLOR, 1)
        cv2.drawContours(frame, [rightEyeHull], -1, self.YELLOW_COLOR, 1)

        for (x, y) in np.concatenate((mouth, leftEye, rightEye), axis=0):
            cv2.circle(frame, (x, y), 2, self.GREEN_COLOR, -1)

        if ear < self.eye_thresh:
            self.eye_count += 1
            if self.eye_count > self.eye_consec_frames:
                if not self.sleep_alarm:
                    self.sleep_alarm = True
                    #self.fbApp.put('/vigilant-73f45-default-rtdb/Driver/-MXvinFMl_9RrzJgY70w', 'Sleepy', 'Yes')

            cv2.putText(frame, "You are Sleepy!!!", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            self.eye_count = 0
            self.sleep_alarm = False
            #self.fbApp.put('/vigilant-73f45-default-rtdb/Driver/-MXvinFMl_9RrzJgY70w', 'Sleepy', 'No')

        if mar > self.mouth_thresh:
            self.mouth_count += 1
            if self.mouth_count > self.mouth_consec_frames:
                if not self.yawn_alarm:
                    self.yawn_alarm = True
                    #self.fbApp.put('/vigilant-73f45-default-rtdb/Driver/-MXvinFMl_9RrzJgY70w', 'Yawning', 'Yes')

            cv2.putText(frame, "You are Yawning!!!", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            self.mouth_count = 0
            self.yawn_alarm = False
            #self.fbApp.put('/vigilant-73f45-default-rtdb/Driver/-MXvinFMl_9RrzJgY70w', 'Yawning', 'No')
        #return self.eye_count, self.mouth_count
