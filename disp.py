from IPython.display import display, clear_output, HTML

class status_updates:
    def __init__(self):
        self.display_handle = display(HTML("Status Update Line"), display_id=True)

    def print_output(self, statement):
        clear_output(wait=True)
        self.display_handle.update(HTML(statement))