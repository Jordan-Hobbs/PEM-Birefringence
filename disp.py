from IPython.display import display, clear_output, HTML

class status_updates:
    def __init__(self, initial_text):
        self.display_handle = display(HTML(initial_text), display_id=True)

    def print_output(self, statement):
        clear_output(wait=True)
        self.display_handle.update(HTML(statement))

    def clear_display(self):
        clear_output()