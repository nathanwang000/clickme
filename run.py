from flask import Flask, render_template, jsonify, request
from collections import defaultdict
import datetime
import json
import re

app = Flask(__name__, template_folder='views', static_folder='static')

def getStrTime(time=datetime.datetime.now()):
    return '-'.join(map(str,[time.year,time.month,time.day,time.hour,
                             time.minute,time.second]))

# unsafe for multithread, but since only I use it, ok
thisHourCount = 0 
lastHour = getStrTime()

@app.route('/',methods=['GET','POST'])
def index():
    data = {}
    if request.method == 'POST':
        # should trim to alphanumeric, TODO
        task = re.sub(r"\s"," ",request.form.get('taskdesc').strip())
        duration = {
            'week': 7,
            'day': 1,
            'month': 31,
            'year': 365
        }[request.form.get('duration')]
        if task:
            now = datetime.datetime.now()
            start = getStrTime(now)
            with open('data/tasks/%s-%s.data' % (task,start),'a') as f:
                end = getStrTime(now+datetime.timedelta(days=duration))
                f.write("%s %s %s\n" % (task,start,end))
        # pass variable to view
        data['task'] = task
        data['duration'] = duration
        print task
        print 'here'
    return render_template('index.html',**data)

@app.route('/click')
def click():
    global thisHourCount, lastHour
    thisHourCount += 1
    thisHour = getStrTime()
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
