class State:
    def enter(self): pass
    def execute(self): pass
    def exit(self): pass

class FSMManager:
    def __init__(self):
        self.state = None

    def set_state(self, state):
        if self.state:
            self.state.exit()
        self.state = state
        self.state.enter()
        
    def update(self):
        if self.state:
            self.state.execute()
            
    def get_state(self):
        return self.state
