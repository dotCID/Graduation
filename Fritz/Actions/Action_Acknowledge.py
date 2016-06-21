#!/user/bin/python
"""
An action where the robot acknowledges user input
"""
import random, time
from Action import Action

## Exit codes
from globalVars import EXIT_CODE_DONE
from globalVars import EXIT_CODE_ERROR
from globalVars import EXIT_CODE_ACK

EXIT_CODE_SELF = EXIT_CODE_ACK

## Poses
from poses import ack_pos_C
from poses import ack_pos_L
from poses import ack_pos_R

class SpecificAction(Action):

    def execute(self,loops = 450):
        """
        Main executing method of this Action.
        @param loops: The amount of times the action will execute a "step" until it finishes. Defaults to 50.
        """
        
        self.max_loops = loops
        if self.loopCheck() == EXIT_CODE_DONE:
            return EXIT_CODE_DONE
        
        rd = random.random()
       
        if self.done(self.currentPosition(), self.pos_target): 
            if rd < 0.33:
                self.pos_target = ack_pos_C
            elif rd <0.66:
                self.pos_target = ack_pos_L
            else:
                self.pos_target = ack_pos_R
            
        self.move(self.pos_target)

        return EXIT_CODE_SELF
