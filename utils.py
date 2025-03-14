from instruments import LinkamHotstage, SRLockinAmplifier
from scipy.special import jv
import time, numpy as np


def run_temperature_sweep(start, stop, step, rate, hotstage, lockin):
    values_valid = hotstage_values_check(start, stop, step, rate)
    if values_valid == True:
        temps = temp_generator(start, stop, step)
        v1f = []
        v2f = []
        m_temps = []

        if hotstage.current_temperature()[0] != start:
            hotstage.set_temperature(start, 50)
            wait_for_temperature(start, hotstage)
            time.sleep(90)
        else:
            pass

        for temp in temps:
            if abs(temp - hotstage.current_temperature()[0]) > 0.1:
                hotstage.set_temperature(temp, rate)
                wait_for_temperature(temp, hotstage)
                time.sleep(15)
            else:
                pass
            while True:
                c_temp, status = hotstage.current_temperature()
                if c_temp == temp and status == "Holding":
                    x1, x2 = lockin.read_dualharmonic_data()
                    m_temps.append(c_temp)
                    v1f.append(x1)
                    v2f.append(x2)
                    time.sleep(2)
                    break
                else:
                    continue

        hotstage.close()
        lockin.close()
        return m_temps, v1f, v2f
    
    elif values_valid == False:
        hotstage.close()
        lockin.close()
        return


def data_analysis(v1f, v2f):
    ret =[]
    j1 = jv(1, np.pi/2)
    j2 = jv(1, np.pi/2)
    
    for v1, v2 in zip(v1f, v2f):
        if v1 == 0 or v2 == 0:
            ret.append(np.nan)
            print("Careful! one value found at zero")
            continue

        delta = np.arctan((v1/v2))
        if v1>0 and v2>0:
            ret.append((delta*635e-9)/(2*np.pi))
            continue
        if v1>0 and v2<0:
            ret.append(np.pi + (delta*635e-9)/(2*np.pi))
            continue
        else:
            ret.append((delta*635e-9)/(2*np.pi))
            print("Careful! one value out of range")
            continue
        # needs the rest of the conditionals this else is not a correct solution
    return ret



def wait_for_temperature(end_temp, hotstage):
    while True:
        temperature = hotstage.current_temperature()[0]
        if temperature is None:
            continue
        if abs(end_temp-temperature) <= 0.1:
            break

        time.sleep(0.1)

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