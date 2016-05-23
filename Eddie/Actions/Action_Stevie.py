#!/user/bin/python
"""
An action where the robot is drifting away, engulfed in the music.
"""
from Action import Action

from globalVars import EXIT_CODE_DONE
from globalVars import EXIT_CODE_ERROR
from globalVars import EXIT_CODE_STEVIE
import random

EXIT_CODE_SELF = EXIT_CODE_STEVIE

class SpecificAction(Action):
    drifting_pos_C = [  85.0, 100.0, 195.0]
    drifting_pos_L = [  75.0, 105.0, 190.0]
    drifting_pos_R = [ 105.0,  95.0, 200.0]
    
    # Random additional angle for movement
    R_extra_max = 5.0
    
    def R_extra(self):
        return random.uniform(-1*self.R_extra_max, self.R_extra_max)

    def execute(self,loops = 50):
        """
        Main executing method of this Action.
        @param loops: The amount of times the action will execute a "step" until it finishes. Defaults to 50.
        """
        self.max_loops = loops
        if self.loopCheck() == EXIT_CODE_DONE:
            return EXIT_CODE_DONE
       
       if self.done(self.currentPosition(), self.drifting_pos_C) or \
          self.done(self.currentPosition(), self.drifting_pos_L) or \
          self.done(self.currentPosition(), self.drifting_pos_R):
           
            rd = random.random()

            if rd < 0.33:
                self.pos_target = drifting_pos_C
            elif rd <0.66:
                self.pos_target = drifting_pos_L
            else:
                self.pos_target = drifting_pos_R
            
            for i in range(len(pos_target)):
                pos_target[i] += R_extra
            
        self.move(self.pos_target)
        
        return EXIT_CODE_SELF
