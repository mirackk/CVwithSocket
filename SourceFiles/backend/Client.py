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
    # 定义定义文件信息。128s表示文件名为128bytes长，l表示一个int或log文件类型，在此为文件大小
    fileinfo_size = struct.calcsize('128sl')
    # 定义文件头信息，包含文件名和文件大小
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
    measurement = "rtt"
    if measurement == "rtt":
        avrRTT = 1e3 * sum(results) / len(results)
        print(avrRTT)
        dataframe = pd.DataFrame({"size": msgSize, "rtt": avrRTT}, index=[0])
        dataframe.to_csv('rtt.csv', mode='a', header=False, index=None)
    if measurement == "tput":
        avrTPUT = 1e-6 * sum([msgSize * 8 / i for i in results]) / len(results)  # Mbps
        dataframe = pd.DataFrame({"size": msgSize, "rtt": avrTPUT}, index=[0])
        dataframe.to_csv('tput.csv', mode='a', header=False, index=None)
        print(avrTPUT)  # Mbps

    # In[ ]:

    return type


if __name__ == '__main__':
    app.run(host="localhost", port=5000)
