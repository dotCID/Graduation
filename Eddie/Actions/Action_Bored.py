#!/user/bin/python
"""
An action where the robot is bored.
"""
from Action import Action

from globalVars import EXIT_CODE_DONE
from globalVars import EXIT_CODE_ERROR
from globalVars import EXIT_CODE_BORED

import random

EXIT_CODE_SELF = EXIT_CODE_BORED

class SpecificAction(Action):
    bored_pos_C = [  85.0, 120.0, 195.0]
    bored_pos_L = [  25.0, 120.0, 190.0]
    bored_pos_R = [  165.0, 120.0, 200.0]

    def execute(self,loops = 50):
        """
        Main executing method of this Action.
        @param loops: The amount of times the action will execute a "step" until it finishes. Defaults to 50.
        """
        self.max_loops = loops
        if self.loopCheck() == EXIT_CODE_DONE:
            return EXIT_CODE_DONE
git sta
        rd = random.random()

        if self.done(self.currentPosition(), self.bored_pos_C):
            if rd < 0.5:
                self.pos_target = bored_pos_L
            else:
                self.pos_target = bored_pos_R
                
        elif self.done(self.currentPosition(), self.bored_pos_L):
            if rd < 0.5:
                self.pos_target = bored_pos_C
            else:
                self.pos_target = bored_pos_R
            
        elif self.done(self.currentPosition(), self.bored_pos_R):
            if rd < 0.5:
                self.pos_target = bored_pos_L
            else:
                self.pos_target = bored_pos_C
            
        self.move(self.pos_target)

        return EXIT_CODE_SELF
