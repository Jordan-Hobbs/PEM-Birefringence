from scipy.special import jv
import numpy as np
import csv

def hotstage_values_check(start, stop, step, rate):
    if not 25 <= start <= 300:
        values_valid = False
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
    else:
        values_valid = True
    return values_valid


def temp_generator(start, stop, step):
    num_points = int((start - stop) / step) + 1
    temps = np.linspace(start, stop, num_points)
    return temps

class analysis:
    def __init__(self, cellgap, wavelength):
        self.j1 = jv(1, np.pi/2)
        self.j2 = jv(2, np.pi/2)
        self.cellgap = cellgap
        self.wavelength = wavelength

    def compute_biref(self, v1f, v2f):
        if v1f == 0 or v2f == 0:   
            print("Careful! one value found at zero")
            return np.nan, np.nan
        else:
            delta = np.arctan((v1f/v2f)*(self.j2/self.j1))
            if v1f>0 and v2f>0:   # first conditional
                retardence = (delta*self.wavelength)/(2*np.pi)
                return retardence, retardence/self.cellgap
            elif v1f>0 and v2f<0: #second conditional
                retardence = ((delta+np.pi)*self.wavelength)/(2*np.pi)
                return retardence, retardence/self.cellgap
            else: # needs the rest of the conditionals this else is not a correct solution
                retardence = (delta*self.wavelength)/(2*np.pi)
                print("Careful! one value out of range")
                return retardence, retardence/self.cellgap

class output_writer:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file = open(self.file_name, mode = "a", newline = "")
        self.writer = csv.writer(self.file)
        self.writer.writerow(["T (C)", "v1f (V)", "v2f (V)", "R (nm)", "d_n"])
        self.file.flush()

    def write_csv_row(self, row):
        self.writer.writerow(row)
        self.file.flush()

    def close(self):
        self.file.close()



