#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# -*- coding=utf-8 -*-
import socket
import threading
import time
import sys
import os
import struct
import torch
from PIL import Image
from torchvision import transforms
import json
type = "squeezeenet"
result = []


# In[ ]:


def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 1234))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print ("Waiting...")
    
    while 1:
        conn, addr = s.accept()
        res = []
        t = threading.Thread(target=deal_data, args=(conn, addr))
        t.start()
        

def deal_data(conn, addr):
    sucMsg = "200 OK: Ready"
    print ('Accept new connection from {0}'.format(addr))
    while 1:
        fileinfo_size = struct.calcsize('128sl')
        buf = conn.recv(fileinfo_size)
        if buf:
            filename, filesize = struct.unpack('128sl', buf)
            fn = filename.strip(str.encode('\00'))
            new_filename = os.path.join(str.encode('./'), str.encode('new_') + fn)
            print ('file new name is {0}, filesize if {1}'.format(new_filename, filesize))

            recvd_size = 0  # define the data size that is received
            fp = open(new_filename, 'wb')
            print ("start receiving...")
            while not recvd_size == filesize:
                if filesize - recvd_size > 1024:
                    data = conn.recv(1024)
                    recvd_size += len(data)
                    conn.send(sucMsg.encode())
                else:
                    data = conn.recv(filesize - recvd_size)
                    recvd_size = filesize
                fp.write(data)
            fp.close()
            print ("end receive...")
        break
    if type == "squeezeenet":
        model = torch.hub.load('pytorch/vision:v0.10.0', 'squeezenet1_0', pretrained=True)
    if type == "googlenet":
        model = torch.hub.load('pytorch/vision:v0.10.0', 'googlenet', pretrained=True)
    filename = os.path.join(str.encode('./'), str.encode('new_') + fn)
    input_image = Image.open(filename)
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = preprocess(input_image)
    input_batch = input_tensor.unsqueeze(0) # create a mini-batch as expected by the model
    output = model(input_batch )
    # The output has unnormalized scores. To get probabilities, you can run a softmax on it.
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    with open("imagenet_classes.txt", "r") as f:
        categories = [s.strip() for s in f.readlines()]
    top5_prob, top5_catid = torch.topk(probabilities, 5)
    # predict results
    a = ""
    for i in range(top5_prob.size(0)):
        result.append(categories[top5_catid[i]])
        a += categories[top5_catid[i]]
        a += "/"
        print(categories[top5_catid[i]], top5_prob[i].item())
    print(a)
    conn.sendall(a.encode())
    conn.close()
if __name__ == '__main__':
    socket_service()


# In[ ]:





# In[ ]:




