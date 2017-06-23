#import fishMAD.Dannetwork
import time
import socket
import struct

IP = '10.126.17.254'
statusPort = 5007
sendStatusCode = 1002

def convolutedClock(ip):
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
            data = struct.pack('>i', int(time.time()))
            socketClient.sendall(data)
            code = struct.unpack('>i',socketClient.recv(4))[0]
            print code
            if code == sendStatusCode:
                status = True      
        except Exception,e:
        	print e
        finally:
            socketClient.shutdown(socket.SHUT_RDWR)
            socketClient.close()

    except:
        pass
        #print('--- connection failed')  
    return status
    
if __name__ == "__main__":
	while True:
		convolutedClock(IP)
		time.sleep(1)
