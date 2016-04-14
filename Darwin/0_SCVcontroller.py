#simply attempts to keep the simpleCV script running at all times
import RunCmd

while True:
    RunCmd.RunCmd(["python", "./simpleCV.py"], 3600).Run()

