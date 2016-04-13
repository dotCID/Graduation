import RunCmd
from pubsub import pub

def listener1(arg1, arg2=None):
    print 'Function listener1 received:'
    print '  arg1 =', arg1
    print '  arg2 =', arg2

pub.subscribe(listener1, 'targetLocation')
RunCmd.RunCmd(["python", "./20160413_simpleCV.py"], 10).Run()
