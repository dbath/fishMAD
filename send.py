#import fishMAD.Dannetwork
import time
import socket
import struct
import argparse

IP = '10.126.17.254'
statusPort = 5007
sendStatusCode = 1002


def sendVal(val):
    status = False
    socketClient = socket.socket()
    socketClient.settimeout(10)
    socketClient.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        socketClient.connect((ip, statusPort))
        try:
            data = struct.pack('>i', val)
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
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--val', type=int, required=True,
                            help='number representing condition')  
	args = parser.parse_args()
	sendVal(args.val)
