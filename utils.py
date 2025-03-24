from scipy.special import jv
import numpy as np
import csv

def data_analysis(v1f, v2f, cellgap):
    retardence =[]
    j1 = jv(1, np.pi/2)
    j2 = jv(2, np.pi/2)
    
    for v1, v2 in zip(v1f, v2f):
        if v1 == 0 or v2 == 0:
            retardence.append(np.nan)
            print("Careful! one value found at zero")
            continue

        delta = np.arctan((v1/v2)*(j2/j1))
        if v1>0 and v2>0:
            retardence.append((delta*635e-9)/(2*np.pi))
            continue
        elif v1>0 and v2<0:
            retardence.append(((delta+np.pi)*635e-9)/(2*np.pi))
            continue
        else:
            retardence.append((delta*635e-9)/(2*np.pi))
            print("Careful! one value out of range")
            continue
        # needs the rest of the conditionals this else is not a correct solution

    biref = [ret/cellgap for ret in retardence]
    return retardence, biref


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


def save_to_csv(filename, *columns):
    headers = ["Temperature (C)", "v1f (V)","v2f (V)", "ret (nm)", "$d_n$"]
    if not columns:
        raise ValueError("No data provided.")
    
    length = len(columns[0])
    if any(len(col) != length for col in columns):
        raise ValueError("All columns must have the same length.")
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Writing the headers
        writer.writerows(zip(*columns))  # Writing the rows

