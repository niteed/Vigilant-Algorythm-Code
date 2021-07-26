from flask import Flask, render_template, Response, request
from camera import VideoCamera
from drowsiness import Drowsy
import json
import requests
from utils import Util
import firebase_admin
from firebase_admin import credentials, auth, firestore
cred = credentials.Certificate('PATH_TO_YOUR_CERTIFICATE')

user = {}
u = Util()
sleep_count = 0
yawn_count = 0
start_time = 0
ride_id = '' 
app = Flask(__name__)

FIREBASE_WEB_API_KEY = "YOUR_FIREBASE_WEB_API_KEY"
rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"

config = {
        "apiKey": "YOUR_API_KEY",
        "authDomain": "YOUR_AUTH_DOMAIN",
        "databaseURL": "YOUR_DATABASE_URL",
        "projectId": "YOUR_PROJECT_ID",
        "storageBucket": "YOUR_STORAGE_BUCKET",
        "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
        "appId": "YOUR_APP_ID"}

firebase_admin.initialize_app(cred, config)
db = firestore.client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global db
    if request.method == 'POST':
        user_details = {}
        user_details['Full Name'] = request.form.get('fname')
        user_details['Car No.'] = str(request.form.get('car'))
        user_details['DOB'] = str(request.form.get('dob'))
        user_details['Contact No.'] = str(request.form.get('phno'))
        user_details['Emergency Contact No.'] = str(request.form.get('sosno'))
        doc = db.collection(u'Drivers').document(f'{user.uid}')
        doc.set(user_details)
        print(user.uid)
    return render_template('login.html', task=1)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        global user
        email = request.form.get('email')
        pwd = request.form.get('password')
        user = auth.create_user(email = email, password = pwd)
        return render_template('details.html')
    return render_template('login.html', task=0)

@app.route('/logged_in', methods=['POST'])
def logged_in():
    global start_time
    if request.method == "POST":
        email = request.form.get('email')
        pwd = request.form.get('password')
        payload = json.dumps({
            "email": email,
            "password": pwd,
            "returnSecureToken": True
        })
        r = requests.post(rest_api_url,params={"key": FIREBASE_WEB_API_KEY},data=payload)
        start_time = u.get_time()
        #print(r.json())
        return render_template('camera.html')

@app.route('/end', methods=['GET', 'POST'])
def ride_end():
    global db
    if request.method == 'POST':
        global user
        global sleep_count
        global yawn_count
        global ride_id
        print(f'Sleep Count: {sleep_count}')
        print(f'Yawn Count: {yawn_count}')
        ltlng = u.get_lat_long()
        data = {}
        data['Ride Start Time'] = start_time
        data['End Start Time'] = u.get_time()
        data['Latitude'] = ltlng[0]
        data['Longitude'] = ltlng[1]
        data['No. of sleeps'] = sleep_count
        data['No. of yawns'] = yawn_count
        data['isDay'] = u.get_daytime()
        doc = db.collection(u'Drivers').document(f'{user.uid}').collection('Rides').document()
        doc.set(data)
        ride_id = doc.id
        sleep_count = 0
        yawn_count = 0
        return render_template('ride.html')

@app.route('/result', methods=['GET', 'POST'])
def show_result():
    global db
    if request.method == 'POST':
        global user
        global ride_id
        doc = db.collection(u'Drivers').document(f'{user.uid}')
        details = doc.get().to_dict()
        ride_doc = db.collection(u'Drivers').document(f'{user.uid}').collection(u'Rides').document(f'{ride_id}')
        ride_details = ride_doc.get().to_dict()
        #print(f'Sleep Count: {sleep_count}')
        #print(f'Yawn Count: {yawn_count}')
        if ride_details['No. of sleeps'] >= 5:
            sms = u.send_SMS(details['Emergency Contact No.'])
        else:
            sms = 'SMS not sent as the driver is not drowsy'

        return render_template('result.html', result = details, got_result=True, sms_status = sms, ride_result = ride_details)

def gen(camera):
    global sleep_count
    global yawn_count
    d = Drowsy()
    while True:
        frame = camera.get_frame()
        image = camera.save_frame()
        #print(image.shape)
        #slept, yawned = d.check_drowsy(image)
        d.check_drowsy(image)
        if d.eye_count >= d.eye_consec_frames:
            sleep_count += 1
            print('Slept')
        if d.mouth_count >= d.mouth_consec_frames:
            yawn_count += 1
            print('Yawned')
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)
