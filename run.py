from flask import Flask, render_template, jsonify
from collections import defaultdict
import datetime
import json

app = Flask(__name__, template_folder='views', static_folder='static')

now = datetime.datetime.now()
# unsafe for multithread, but since only I use it, ok
thisHourCount = 0 
lastHour = '-'.join(map(str,[now.year,now.month,now.day,now.hour,now.minute,now.second]))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/click')
def click():
    global thisHourCount, lastHour
    thisHourCount += 1
    now = datetime.datetime.now()
    thisHour = '-'.join(map(str,[now.year,now.month,now.day,now.hour,now.minute,now.second]))
    # writeback lastHour and update time
    if lastHour != thisHour:
        # write back the data
        with open('data/click.data','a') as f:
            f.write('%s %s\n' % (lastHour,thisHourCount))
        thisHourCount = 1
        lastHour = thisHour
    data = {"nclick": thisHourCount}
    return jsonify(**data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
