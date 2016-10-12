#!/user/bin/python
"""
An action where the robot is drifting away, engulfed in the music.
"""

import random
from Action import Action

## Exit codes
from globalVars import EXIT_CODE_DONE
from globalVars import EXIT_CODE_ERROR
from globalVars import EXIT_CODE_STEVIE

EXIT_CODE_SELF = EXIT_CODE_STEVIE

## Poses
from poses import drifting_pos_C
from poses import drifting_pos_L
from poses import drifting_pos_R

from poses import pos_min
from poses import pos_max

class SpecificAction(Action):
    
    # Random additional angle for movement
    R_extra_max = 5.0
    
    def R_extra(self):
        return random.uniform(-1*self.R_extra_max, self.R_extra_max)

    def execute(self,loops = 150):
        """
        Main executing method of this Action.
        @param loops: The amount of times the action will execute a "step" until it finishes. Defaults to 50.
        """
        
        # the general max speed is a bit high here
        self.maxV = 0.25
        
        self.max_loops = loops
        if self.loopCheck() == EXIT_CODE_DONE:
            return EXIT_CODE_DONE
       
        ''' if self.done(self.currentPosition(), self.drifting_pos_C) or \
          self.done(self.currentPosition(), self.drifting_pos_L) or \
          self.done(self.currentPosition(), self.drifting_pos_R):
         '''
        if self.done(self.currentPosition(), self.pos_target):  
            rd = random.random()

            if rd < 0.33:
                self.pos_target = drifting_pos_C
            elif rd <0.66:
                self.pos_target = drifting_pos_L
            else:
                self.pos_target = drifting_pos_R
            
            for i in range(len(self.pos_target)):
                self.pos_target[i] += self.R_extra()
                if self.pos_target[i] > pos_max[i]:
                    self.pos_target[i] = pos_max[i]
                if self.pos_target[i] < pos_min[i]:
                    self.pos_target[i] = pos_min[i]
        
            print self.pos_target
        self.move(self.pos_target)
        
        return EXIT_CODE_SELF
