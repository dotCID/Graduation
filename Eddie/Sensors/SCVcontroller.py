#simply attempts to keep the simpleCV script running at all times
import RunCmd

while True:
    RunCmd.RunCmd(["python", "./simpleCV_2.py"], 600).Run()

