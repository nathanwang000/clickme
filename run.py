from flask import Flask, render_template, jsonify, request, redirect
from collections import defaultdict
import datetime,json,re,os,subprocess

app = Flask(__name__, template_folder='views', static_folder='static')

def getStrTime(time=None,upto='second'):
    if not time: time = datetime.datetime.now()
    upto = {'year':1, 'month':2, 'day':3, 'hour':4, 'minute':5, 'second':6}[upto]
    info = [time.year,time.month,time.day,time.hour,time.minute,time.second]
    return '-'.join(map(str,info[:upto]))

# unsafe for multithread, but since only I use it, ok
thisHourCount = 0 
lastHour = getStrTime()
os.system('mkdir -p data/tasks/{alive,archive}')

@app.route('/',methods=['GET','POST'])
def index():
    data = defaultdict(lambda: None, tasks=[], archive=[])

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
            with open('data/tasks/alive/%s$%s.data' % (task,start),'a') as f:
                end = getStrTime(now+datetime.timedelta(days=duration))
                f.write("%s %s\n" % (start,end))

    # fetch alive task list TODO: defer this work later, just use a button and use ajax
    basedir = 'data/tasks/alive/'
    for fn in os.listdir(basedir):
        if fn.endswith('.data'):
            with open(os.path.join(basedir,fn),'r') as f:
                start,end = f.readline().strip().split(' ')
                # convert string into datetime TODO
                # http://stackoverflow.com/questions/466345/converting-string-into-datetime
                # $ is the delimiter
                data['tasks'].append((fn.split('$')[0],start,end))

    # fetch archive task list TODO: defer this work later, just use a button and use ajax
    basedir = 'data/tasks/archive/'
    for fn in os.listdir(basedir):
        if fn.endswith('.fin'):
            with open(os.path.join(basedir,fn),'r') as f:
                start,end = f.readline().strip().split(' ')
                # convert string into datetime TODO
                # http://stackoverflow.com/questions/466345/converting-string-into-datetime
                # $ is the delimiter
                data['archive'].append((fn.split('$')[0],'FINISHED'))
        if fn.endswith('.abort'):
            with open(os.path.join(basedir,fn),'r') as f:
                start,end = f.readline().strip().split(' ')
                # convert string into datetime TODO
                # http://stackoverflow.com/questions/466345/converting-string-into-datetime
                # $ is the delimiter
                data['archive'].append((fn.split('$')[0],'ABORTED'))

    # fetch number of clicks TODO:deferWork using ajax
    totalClicks = 0
    if (os.path.exists('data/click.data')):
        with open('data/click.data') as f:
            for l in f:
                time, count = l.strip().split(' ')
                totalClicks += int(count)
    data['totalClicks'] = totalClicks
    data['thishour'] = lastHour
    
    return render_template('index.html',**data)

@app.route('/click')
def click():
    global thisHourCount, lastHour

    thisHour = getStrTime()
    # writeback lastHour and update time
    if lastHour != thisHour:
        # write back the data
        with open('data/click.data','a') as f:
            f.write('%s %s\n' % (lastHour,thisHourCount))
        thisHourCount = 1
        lastHour = thisHour
    else:
        thisHourCount += 1
    data = {"nclick": thisHourCount}
    return jsonify(**data)

@app.route('/taskDelete',methods=['GET'])
def taskDelete():
    taskid = request.args.get('taskid') # TODO: sanitize this argument
    os.system('rm ' + os.path.join('data/tasks/alive/', '%s.data'%taskid))
    return redirect('/#tasks')

@app.route('/taskCheckin',methods=['GET'])
def taskCheckin():
    taskid = request.args.get('taskid').strip('\'')
    with open('data/tasks/alive/%s.data' % taskid,'a') as f:
        # TODO: fix the logic here so that everyday has only one checkin
        f.write('%s %s\n' % (getStrTime(upto='day'),1))
    return redirect('/#tasks')

@app.route('/taskFinish',methods=['GET'])
def taskFinish():
    # move to archive and mark in filename as fin
    taskid = request.args.get('taskid').strip('\'')
    fn = 'data/tasks/alive/%s.data' % taskid
    with open(fn,'a') as f: f.write('FIN %s\n' % getStrTime())
    # TODO use popopen b/c the file name may contain unwanted words
    os.system("mv '%s' 'data/tasks/archive/%s.fin'" % (fn,taskid))
    return redirect('/#archive')

@app.route('/taskAbort',methods=['GET'])
def taskAbort():
    # move to archive and mark in filename as abort
    fn = 'data/tasks/alive/%s.data' % taskid
    with open(fn,'a') as f: f.write('FIN %s\n' % getStrTime())
    # TODO use popopen b/c the file name may contain unwanted words
    os.system('mv "%s" data/tasks/archive/%s.abort' % (fn,taskid))
    return redirect('/#archive')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
