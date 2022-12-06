from flask import Flask,request
import socket
import os
import sys
import struct
import time
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def hello():
    return "hello"

@app.route('/client')
def client():  # put application's code here
    # In[64]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('10.10.1.1', 1234))
    except socket.error as msg:
        print(msg)
        sys.exit(1)

    # In[65]:

    filepath = request.args.get('fileAddress')
    filepath = filepath.replace("\\","/")
    print(filepath)
    # filepath = 'C:/Users/Jace/Downloads/final/23.jpg'
    fileinfo_size = struct.calcsize('128sl')
    # define the head infomaiton of the file
    fhead = struct.pack('128sl', bytes(os.path.basename(filepath).encode('utf-8')), os.stat(filepath).st_size)
    s.send(fhead)
    print('client filepath: {0}'.format(filepath))
    fp = open(filepath, 'rb')
    results = []

    # In[66]:

    while 1:
        data = fp.read(1024)
        if not data:
            print('{0} file send over...'.format(filepath))
            break
        startTime = time.time()
        s.send(data)
        res = s.recv(2048)
        if (res != b'200 OK: Ready'):
            type = res.decode()
        endTime = time.time()
        results.append(endTime - startTime)
    print(type)

    # In[ ]:

    msgSize = os.stat(filepath).st_size
    print(msgSize)
    measurement = "all"
    if measurement == "rtt" or measurement =="all":
        avrRTT = 1e3 * sum(results) / len(results) # ms
        print(avrRTT)
        dataframe = pd.DataFrame({"size": msgSize, "rtt": avrRTT}, index=[0])
        dataframe.to_csv('rtt.csv', mode='a', header=False, index=None)
    if measurement == "tput" or measurement =="all":
        avrTPUT = 1e-6 * sum([msgSize * 8 / i for i in results]) / len(results)  # Mbps
        dataframe = pd.DataFrame({"size": msgSize, "tput": avrTPUT}, index=[0])
        dataframe.to_csv('tput.csv', mode='a', header=False, index=None)
        print(avrTPUT)  # Mbps
    if measurement == "total" or measurement =="all":
        totalTime = 1e3 * sum(results) # ms
        print(totalTime)
        dataframe = pd.DataFrame({"size": msgSize, "total": totalTime}, index=[0])
        dataframe.to_csv('total.csv', mode='a', header=False, index=None)

    # In[ ]:

    return type


if __name__ == '__main__':
    app.run(host="localhost", port=5000)
