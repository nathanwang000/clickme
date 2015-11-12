from flask import Flask, render_template, jsonify, request
from collections import defaultdict
import datetime,json,re,os

app = Flask(__name__, template_folder='views', static_folder='static')

def getStrTime(time=datetime.datetime.now()):
    return '-'.join(map(str,[time.year,time.month,time.day,time.hour,
                             time.minute,time.second]))

# unsafe for multithread, but since only I use it, ok
thisHourCount = 0 
lastHour = getStrTime()
os.system('mkdir -p data/tasks')

@app.route('/',methods=['GET','POST'])
def index():
    data = defaultdict(lambda: None, tasks=[])

    if request.method == 'POST':
        # should trim to alphanumeric, TODO
        task = re.sub(r"[\s\$]"," ",request.form.get('taskdesc').strip())
        duration = {
            'week': 7,
            'day': 1,
            'month': 31,
            'year': 365
        }[request.form.get('duration')]
        if task:
            now = datetime.datetime.now()
            start = getStrTime(now)
            with open('data/tasks/%s$%s.data' % (task,start),'a') as f:
                end = getStrTime(now+datetime.timedelta(days=duration))
                f.write("%s %s\n" % (start,end))

    # fetch task list TODO: defer this work later, just use a button and use ajax
    basedir = 'data/tasks'
    for fn in os.listdir(basedir):
        if fn.endswith('.data'):
            with open(os.path.join(basedir,fn),'r') as f:
                start,end = f.readline().strip().split(' ')
                # convert string into datetime TODO
                # http://stackoverflow.com/questions/466345/converting-string-into-datetime
                # $ is the delimiter
                data['tasks'].append((fn.split('$')[0],start,end))

    # fetch number of clicks TODO:deferWork using ajax
    totalClicks = 0
    if (os.path.exists('data/click.data')):
        with open('data/click.data') as f:
            for l in f:
                time, count = l.strip().split(' ')
                totalClicks += int(count)
    data['totalClicks'] = totalClicks
    
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
