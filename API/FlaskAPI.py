from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
import HueController
from colour import Color
import simplejson
import datetime
import time
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('api.properties')
hueIP = config.get('Hue', 'ip')
hostIP=config.get('Host', 'ip')

app = FlaskAPI(__name__)
hue = HueController.hue_rgb(hueIP)

def logger(information):
    f = open('api.log', 'a+')
    ts = time.time()
    f.write(information +  "  Timestamp: " + str(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))  + '\n')
    f.close

def set_hue():
    hue = HueController.hue_rgb(hueIP)


def set_rgb(rgb):
    rgb = rgb.split(',')
    rgb = map(float, rgb)
    hue.rgb_set(rgb)

def hue_on(state):
    hue.on(state)

def set_brightness(brightness):
    hue.brightness(int(float(brightness) * 2.54))

def handle_transition(payload):
    hue.transition(payload)

def handle_hue(payload):
    set_hue()
    try:
        hue.set_group(payload['group'])
    except:
        return failed("couldn't get group", payload)
    if(payload.has_key('transitiontime')):
        handle_transition(payload)
    if(payload.has_key('brightness')):
        set_brightness(payload['brightness'])
    if(payload.has_key('rgb')):
        try:
            set_rgb(payload['rgb'])
        except:
            return failed("couldn't change rgb", payload)
    if(payload.has_key('on')):
        hue_on(payload['on'])
    return suceeded("success", payload)

def suceeded(result, payload):
    logger(result + str(payload))
    return {'API Status' : result}

def failed(result, payload):
    logger(result + str(payload))
    return {
            'api result' : result
            }

@app.route("/", methods=['GET', 'POST'])
def get_request():
    if request.method == 'POST':
#        action = str(request.data.get('action', ''))
        payload = request.get_json(silent=True)
        if(payload.has_key('hue')):
            return handle_hue(payload['hue']);
        else:
            return failed("couldn't get params", payload)

if __name__ == "__main__":
    app.run(debug=True,host=hostIP)
