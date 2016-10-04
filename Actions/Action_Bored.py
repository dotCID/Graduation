#!/user/bin/python
"""
An action where the robot is bored.
"""
import random
from Action import Action

## Exit codes
from globalVars import EXIT_CODE_DONE
from globalVars import EXIT_CODE_ERROR
from globalVars import EXIT_CODE_BORED
EXIT_CODE_SELF = EXIT_CODE_BORED

## Poses
from poses import bored_pos_C
from poses import bored_pos_L
from poses import bored_pos_R


class SpecificAction(Action):

    def execute(self,loops = 50):
        """
        Main executing method of this Action.
        @param loops: The amount of times the action will execute a "step" until it finishes. Defaults to 50.
        """
        global bored_pos_C, bored_pos_L, bored_pos_R
        
        self.max_loops = loops
        if self.loopCheck() == EXIT_CODE_DONE:
            return EXIT_CODE_DONE

        rd = random.random()

        if self.done(self.currentPosition(), bored_pos_C):
            if rd < 0.5:
                self.pos_target = bored_pos_L
            else:
                self.pos_target = bored_pos_R
                
        elif self.done(self.currentPosition(), bored_pos_L):
            if rd < 0.5:
                self.pos_target = bored_pos_C
            else:
                self.pos_target = bored_pos_R
            
        elif self.done(self.currentPosition(), bored_pos_R):
            if rd < 0.5:
                self.pos_target = bored_pos_L
            else:
                self.pos_target = bored_pos_C
                
        elif self.done(self.currentPosition(), self.pos_target):
            self.pos_target = bored_pos_C
            
        self.move(self.pos_target)

        return EXIT_CODE_SELF
