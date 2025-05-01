import matplotlib as plt

class Plotter:
    def __init__(self, show_biref=True):
        self.temps = []
        self.retardances = []
        self.birefs = []
        self.show_biref = show_biref

        self.fig, self.ax1 = plt.subplots()
        self.ax1.set_xlabel("Temperature (°C)")
        self.ax1.set_ylabel("Retardance (nm)", color='tab:blue')
        self.line1, = self.ax1.plot([], [], 'o-', color='tab:blue', label='Retardance')

        if show_biref:
            self.ax2 = self.ax1.twinx()
            self.ax2.set_ylabel("Birefringence", color='tab:red')
            self.line2, = self.ax2.plot([], [], 'x--', color='tab:red', label='Birefringence')
        else:
            self.ax2 = None

        self.fig.tight_layout()

        plt.ion()  # Turn on interactive mode

    def update(self, temp, retardance, biref):
        self.temps.append(temp)
        self.retardances.append(retardance)
        self.line1.set_data(self.temps, self.retardances)
        self.ax1.relim()
        self.ax1.autoscale_view()

        if self.show_biref and self.ax2 is not None:
            self.birefs.append(biref)
            self.line2.set_data(self.temps, self.birefs)
            self.ax2.relim()
            self.ax2.autoscale_view()

        self.fig.canvas.draw()
        plt.pause(0.1)  # Pause for a moment to allow updates