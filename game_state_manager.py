class GameStateManager:
    def __init__(self, current_state):
        self.current_state = current_state
        self.reset_requested = False

    def get_state(self):
        return self.current_state

    def set_state(self, state):
        self.current_state = state
        if state == 'reset_level':
            self.reset_requested = True
            self.current_state = 'level'

    def is_reset_requested(self):
        # Method to check if a reset was requested
        return self.reset_requested

    def clear_reset_request(self):
        # Reset the flag once the request has been handled
        self.reset_requested = False