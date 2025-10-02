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

    def compute_biref(self, X1, X2, Y1, Y2):
        # complex phasors
        V1 = X1 + 1j*Y1
        V2 = X2 + 1j*Y2

        A1 = np.abs(V1)
        A2 = np.abs(V2)
        phi1 = np.angle(V1)   # in radians, range (-pi, pi]
        phi2 = np.angle(V2)

        if A1 == 0 or A2 == 0:   
            print("Careful! one value found at zero")
            return np.nan, np.nan

        B = np.arctan((A1/A2) * (self.j2/self.j1))

        # quadrant mapping via phases
        if phi1 >= 0 and phi2 >= 0:
            delta = B
        elif phi1 >= 0 and phi2 < 0:
            delta = np.pi - B
        elif phi1 < 0 and phi2 < 0:
            delta = np.pi + B
        elif phi1 < 0 and phi2 >= 0:
            delta = 2*np.pi - B
        else:
            # should not happen, fallback
            delta = B

        retardence = (delta * self.wavelength) / (2*np.pi)
        d_n = retardence/self.cellgap
        return retardence, d_n

class OutputWriter:
    def __init__(self, file_name, x_mode="temp"):
        self.file_name = file_name
        self.file = open(self.file_name, mode = "w", newline = "")
        self.writer = csv.writer(self.file)
        if x_mode == "temp":
            self.writer.writerow(["T (C)", "X1f (V)", "X2f (V)", "Y1f (V)", "Y2f (V)", "R (nm)", "d_n"])
            self.file.flush()
        elif x_mode == "time":
            self.writer.writerow(["t (s)", "X1f (V)", "X2f (V)", "Y1f (V)", "Y2f (V)", "R (nm)", "d_n"])
            self.file.flush()

    def write_csv_row(self, row):
        self.writer.writerow(row)
        self.file.flush()

    def close(self):
        self.file.close()

