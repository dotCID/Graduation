#!/user/bin/python
"""
An action where the robot is focused on its musical role
"""
from Action import Action

from globalVars import EXIT_CODE_DONE
from globalVars import EXIT_CODE_ERROR
from globalVars import EXIT_CODE_FOCUS

import random

EXIT_CODE_SELF = EXIT_CODE_FOCUS

class SpecificAction(Action):
    focus_pos_C = [ 100.0,  20.0,  50.0]
    focus_pos_L = [  70.0,  30.0,  35.0]
    focus_pos_R = [ 120.0,  10.0,  25.0]

    def execute(self,loops = 50):
        """
        Main executing method of this Action.
        @param loops: The amount of times the action will execute a "step" until it finishes. Defaults to 50.
        """
        global focus_pos_L, focus_pos_C, focus_pos_R
        
        self.max_loops = loops
        if self.loopCheck() == EXIT_CODE_DONE:
            return EXIT_CODE_DONE
        
        rd = random.random()
       
        if self.done(self.currentPosition(), self.focus_pos_C):
            if rd < 0.33:
                self.pos_target = focus_pos_C
            elif rd <0.66:
                self.pos_target = focus_pos_L
            else:
                self.pos_target = focus_pos_R
                
        elif self.done(self.currentPosition(), self.focus_pos_L):
            # TODO: implement either different response to completion per case or combine
            if rd < 0.33:
                self.pos_target = focus_pos_C
            elif rd <0.66:
                self.pos_target = focus_pos_L
            else:
                self.pos_target = focus_pos_R
            
        elif self.done(self.currentPosition(), self.focus_pos_R):
            if rd < 0.33:
                self.pos_target = focus_pos_C
            elif rd <0.66:
                self.pos_target = focus_pos_L
            else:
                self.pos_target = focus_pos_R
            
        self.move(self.pos_target)

        return EXIT_CODE_SELF
