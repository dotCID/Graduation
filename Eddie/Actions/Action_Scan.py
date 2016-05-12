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
        
        global user_contact_angles
        self.max_loops = loops
        if self.loopCheck() == EXIT_CODE_DONE:
            return EXIT_CODE_DONE
        
        print "Scan:",Action.user_contact_angles
        
        if Action.user_contact_angles['x'] is 0:
            return EXIT_CODE_CONTACT
            
        print self.loops_executed
        return EXIT_CODE_SCAN
