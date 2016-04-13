import zmq
 
if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, '')
    socket.connect("tcp://127.0.0.1:4999")
    
    print "Listening."
    
    while True:
        msg = socket.recv()
        print(msg)
