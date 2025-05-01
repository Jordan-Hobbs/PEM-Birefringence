import csv

from scipy.special import jv
import numpy as np
import matplotlib.pyplot as plt


def hotstage_values_check(start, stop, step, rate):
    values_valid = True
    if not 25 <= start <= 300:
        print(f"Improper start value: {start} must be 25 <= start <= 300")
        values_valid = False
    if not 25 <= stop <= 300:
        print(f"Improper stop value: {stop} must be 25 <= stop <= 300")
        values_valid = False
    if not 0.1 <= step <= 20:
        print(f"Improper step value: {step} must be 0.1 <= step <= 20")
        values_valid = False
    if not 0.1 <= rate <= 30:
        print(f"Improper rate value: {rate} must be 0.1 <= rate <= 30")
        values_valid = False
    return values_valid

def temp_generator(start, stop, step):
    if start > stop:
        num_points = int((start - stop) / step) + 1
        temps = np.linspace(start, stop, num_points)
    else:
        num_points = int((stop - start) / step) + 1
        temps = np.linspace(start, stop, num_points)
    return temps

class Analysis:
    def __init__(self, cellgap, wavelength):
        self.j1 = jv(1, np.pi/2)
        self.j2 = jv(2, np.pi/2)
        self.cellgap = cellgap
        self.wavelength = wavelength

    def compute_biref(self, v1f, v2f):
        if v1f == 0 or v2f == 0:   
            print("Careful! one value found at zero")
            return np.nan, np.nan

        delta = np.arctan((v1f/v2f)*(self.j2/self.j1))
        if v1f>0 and v2f>0:   # first conditional
            retardence = (delta*self.wavelength)/(2*np.pi)
            return retardence, retardence/self.cellgap
        elif v1f>0 and v2f<0: # second conditional
            retardence = ((delta+np.pi)*self.wavelength)/(2*np.pi)
            return retardence, retardence/self.cellgap
        else: # needs the rest of the conditionals this else is not a correct solution
            retardence = (delta*self.wavelength)/(2*np.pi)
            print("Careful! One value out of range")
            return retardence, retardence/self.cellgap

class OutputWriter:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file = open(self.file_name, mode = "w", newline = "")
        self.writer = csv.writer(self.file)
        self.writer.writerow(["T (C)", "v1f (V)", "v2f (V)", "R (nm)", "d_n"])
        self.file.flush()

    def write_csv_row(self, row):
        self.writer.writerow(row)
        self.file.flush()

    def close(self):
        self.file.close()

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
        self.fig.canvas.flush_events()