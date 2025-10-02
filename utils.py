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
        elif v1f<0 and v2f<0: # third conditional
            retardence = ((delta+np.pi)*self.wavelength)/(2*np.pi)
            return retardence, retardence/self.cellgap
        elif v1f<0 and v2f>0: # fourth conditional
            retardence = ((delta+2*np.pi)*self.wavelength)/(2*np.pi)
            return retardence, retardence/self.cellgap
        else: # needs the rest of the conditionals this else is not a correct solution
            retardence = (delta*self.wavelength)/(2*np.pi)
            print("Something odd happened here...")
            return np.nan, np.nan

class OutputWriter:
    def __init__(self, file_name, x_mode="temp"):
        self.file_name = file_name
        self.file = open(self.file_name, mode = "w", newline = "")
        self.writer = csv.writer(self.file)
        if x_mode == "temp":
            self.writer.writerow(["T (C)", "v1f (V)", "v2f (V)", "R (nm)", "d_n"])
            self.file.flush()
        elif x_mode == "time":
            self.writer.writerow(["t (s)", "v1f (V)", "v2f (V)", "R (nm)", "d_n"])
            self.file.flush()

    def write_csv_row(self, row):
        self.writer.writerow(row)
        self.file.flush()

    def close(self):
        self.file.close()

