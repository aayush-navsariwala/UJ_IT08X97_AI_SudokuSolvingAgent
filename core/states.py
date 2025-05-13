from core.fsm import State

class InputState(State):
    def enter(self):
        print("Entered Input State")

    def execute(self):
        print("Awaiting player input...")

    def exit(self):
        print("Exiting Input State")

        
class ValidationState(State):
    def enter(self):
        print("Validating input...")

    def execute(self):
        print("Check if board is valid")

    def exit(self):
        print("Leaving Validation State")