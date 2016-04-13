''' 
Written by ralphtheninja on Stackoverflow
http://stackoverflow.com/questions/4158502/python-kill-or-terminate-subprocess-when-timeout

Usage: RunCmd(["./someProg", "arg1"], 60).Run()
'''

import subprocess as sub
import threading

class RunCmd(threading.Thread):
    def __init__(self, cmd, timeout):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.timeout = timeout

    def run(self):
        self.p = sub.Popen(self.cmd)
        self.p.wait()

    def Run(self):
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            self.p.terminate()      #use self.p.kill() if process needs a kill -9
            self.join()

