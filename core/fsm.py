class State:
    def enter(self): pass
    def execute(self): pass
    def exit(self): pass

class FSMManager:
    def __init__(self):
        self.state = None

    def set_state(self, new_state):
        if self.state:
            self.state.exit()
        self.state = new_state
        self.state.enter()
