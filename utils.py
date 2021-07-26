import geocoder
import datetime
from twilio.rest import Client

class Util:
    def __init__(self):
        self.g = geocoder.ip('me')
        self.account_sid = 'YOUR_TWILIO_ACCOUNT_SID'
        self.auth_token = 'YOUR_TWILIO_AUTH_TOKEN'

    def get_lat_long(self):
        return self.g.latlng
    
    @staticmethod
    def get_time():
        return datetime.datetime.now()

    def get_daytime(self):
        current_time = self.get_time()
        h = current_time.hour
        if h < 7 or h > 19:
            return False
        else:
            return True
    
    def send_SMS(self, number):
        client = Client(self.account_sid, self.auth_token)
        ltlng = self.get_lat_long()
        sendNo = '+91'+str(number)
        message = client.messages \
            .create(
                body=f'http://maps.google.com/maps?q={ltlng[0]},{ltlng[1]}',
                from_='YOUR_TWILIO_NO',
                to=sendNo
            ) 
        return message.status