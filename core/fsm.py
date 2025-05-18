class State:
    # Called when the FSM enters this state
    def enter(self): pass
    
    # Called continuously while this state is active
    def execute(self): pass
    
    # Called when transitioning out of this state
    def exit(self): pass

class FSMManager:
    def __init__(self):
        # Initialises the FSM with no current state
        self.state = None

    # Switches FSM to a new state by calling exit() on the current state and then sets and enters a new state
    def set_state(self, state):
        if self.state:
            self.state.exit()
        self.state = state
        self.state.enter()
    
    # Executes the current state's behaviour
    def update(self):
        if self.state:
            self.state.execute()
    
    # Returns the current active state
    def get_state(self):
        return self.state
