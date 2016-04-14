#simply attempts to keep the simpleCV script running at all times
import RunCmd

while True:
    RunCmd.RunCmd(["python", "./20160413_simpleCV.py"], 3600).Run()

