#!/user/bin/python
"""
Placeholder specific Action class.
"""
from Action import Action

from globalVars import EXIT_CODE_DONE
from globalVars import EXIT_CODE_ERROR
from globalVars import EXIT_CODE_SCAN
from globalVars import EXIT_CODE_CONTACT

class SpecificAction(Action):
    def execute(self,loops = 50):
        """
        Main executing method of this Action.
        @param loops: The amount of times the action will execute a "step" until it finishes. Defaults to 50.
        """
        self.max_loops = loops
        if self.loopCheck() == EXIT_CODE_DONE:
            return EXIT_CODE_DONE
        
        # Test for shared vars
        Action.user_contact_angles = {
                        't' : 5,
                        'x' : 1.0,
                        'y' : 2.0,
                        'z' : 3.0
                      }
#        print self.loops_executed
        print "Contact: new contact angles:",Action.user_contact_angles
        
        return EXIT_CODE_SCAN
