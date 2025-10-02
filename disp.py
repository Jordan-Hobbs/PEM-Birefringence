import matplotlib.pyplot as plt

class Plotter:
    def __init__(self, show_biref=True, x_mode="temp"):
        """
        Parameters
        ----------
        show_biref : bool
            Whether to plot birefringence on a secondary axis.
        x_mode : str
            'temp' → x-axis is temperature
            'time' → x-axis is time (you must supply it in update())
        """
        self.x_vals = []
        self.retardances = []
        self.birefs = []
        self.show_biref = show_biref
        self.x_mode = x_mode

        # Create figure and axes
        self.fig, self.ax1 = plt.subplots()

        if x_mode == "temp":
            self.ax1.set_xlabel("Temperature (°C)")
        else:
            self.ax1.set_xlabel("Time (s)")

        self.ax1.set_ylabel("Retardance (nm)", color='tab:blue')
        self.line1, = self.ax1.plot([], [], 'o-', color='tab:blue')

        if show_biref:
            self.ax2 = self.ax1.twinx()
            self.ax2.set_ylabel("Birefringence", color='tab:red')
            self.line2, = self.ax2.plot([], [], 'x--', color='tab:red')
        else:
            self.ax2 = None

        self.fig.tight_layout()
        plt.ion()

    def update(self, x_val, retardance, biref):
        """
        Parameters
        ----------
        x_val : float
            Temperature (if x_mode='temp') or time value (if x_mode='time').
        retardance : float
            Retardance value in nm.
        biref : float
            Birefringence value.
        """
        self.x_vals.append(x_val)
        self.retardances.append(retardance)
        self.line1.set_data(self.x_vals, self.retardances)
        self.ax1.relim()
        self.ax1.autoscale_view()

        if self.show_biref and self.ax2 is not None:
            self.birefs.append(biref)
            self.line2.set_data(self.x_vals, self.birefs)
            self.ax2.relim()
            self.ax2.autoscale_view()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.1)