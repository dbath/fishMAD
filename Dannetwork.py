import numpy
import threading
import time
import socket
import struct
import numpy as np
import threading
import time
import traceback

requestStatusCode = 1001
sendStatusCode = 1002

running = True


statusPort = 5007

IP = '10.126.17'


def giveStatus(ip):
    backlog = 1  # how many connections to accept
    maxsize = 28
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    binded = False
    while not binded:
        try:
            server.bind((ip,statusPort))
            binded = True
        except Exception,e:
            traceback.print_exc() 
            print '- Give Status -- binding failed \n', e
            binded = False
    server.listen(1)
    while running:
        print '--- waiting for a connection' 
        connection, client_address = server.accept()
        print '------ Connection coming from ' + str(client_address)



        code = struct.unpack('i',connection.recv(4))[0]
        print('------ code : '+ str(code))
        if code == requestStatusCode:
            data = struct.pack('i', sendStatusCode)
            try:
                connection.sendall(data)
            except:
                print 'sending did not work :/ but better not break everything'


def requestStatus(ip):
    status = False
    socketClient = socket.socket()
    socketClient.settimeout(10)
    socketClient.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connect = 0
    fishN=0
    print('--- Connection to ' + str(ip))

    try:
        socketClient.connect((ip, statusPort))
        print '--- Connected to ' + str(ip)
        try:
            data = struct.pack('i', requestStatusCode)
            socketClient.sendall(data)
            code = struct.unpack('i',socketClient.recv(4))[0]
            if code == sendStatusCode:
                status = True      
        finally:
            socketClient.shutdown(socket.SHUT_RDWR)
            socketClient.close()

    except:
        pass
        #print('--- connection failed')  
    return status



def sendModif(code,dataSend = []):
    dataRec =[]
    socketClient = socket.socket()
    socketClient.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connect = 0
    
    print '--- architect Connection  '

    
    while connect == 0:
        try:
            socketClient.connect((architectIP, modifPort))
            connect = 1
        except:
            connect = 0
    print('--- Architect connected')
    if code in expCode:  
        data = struct.pack('i', code)
        socketClient.sendall(data)
        dataRec = struct.unpack('ii',socketClient.recv(8))
    if code in fishVRCode:  
        data = struct.pack('i', code)
        socketClient.sendall(data)
        dataRec = struct.unpack('iiiiii',socketClient.recv(24))
    if code in modifCode:  
        data = struct.pack('i', code)
        socketClient.sendall(data)
        data = struct.pack('i', dataSend[0])
        socketClient.sendall(data)
        dataRec = struct.unpack('ii',socketClient.recv(8))
    if code in startDisplayCode:  
        data = struct.pack('i', code)
        socketClient.sendall(data)
        dataRec = struct.unpack('i',socketClient.recv(4))
    if code in startTrackingCode:  
        data = struct.pack('i', code)
        socketClient.sendall(data)
        dataRec = struct.unpack('i',socketClient.recv(4))
    if code in startMatrixCode:  
        data = struct.pack('i', code)
        socketClient.sendall(data)
        dataRec = struct.unpack('i',socketClient.recv(4))
    if code == killCode:  
        data = struct.pack('i', code)
        socketClient.sendall(data)
        dataRec = struct.unpack('i',socketClient.recv(4))

    print(dataRec)
    socketClient.shutdown(socket.SHUT_RDWR)
    socketClient.close()
    print('Architect Disconnected')
    return dataRec



def main():
    global running
    statusThread = threading.Thread(target = giveStatus, args=(IP,))
    statusThread.daemon = True
    statusThread.start()
    t0=time.time()
    while running:
        print('status ? ' +str(requestStatus(IP)))
        if time.time()-t0>30:
            running = False

if __name__ == '__main__':
    main()
