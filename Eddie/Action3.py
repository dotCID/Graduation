#!/user/bin/python
"""
Placeholder specific Action class.
"""
from Action import Action

from globalVars import EXIT_CODE_DONE
from globalVars import EXIT_CODE_ERROR
from globalVars import EXIT_CODE_A3

class Action3(Action):
    def execute(self,loops = 50):
        """
        Main executing method of this Action.
        @param loops: The amount of times the action will execute a "step" until it finishes. Defaults to 50.
        """
        self.max_loops = loops
        if self.loopCheck() == EXIT_CODE_DONE:
            return EXIT_CODE_DONE
        print EXIT_CODE_A3, self.loops_executed
        return EXIT_CODE_A3
