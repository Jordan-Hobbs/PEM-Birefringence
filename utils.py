
from instruments import LinkamHotstage, SRLockinAmplifier
import time, numpy as np


def run_temperature_sweep(start, stop, step, rate, hotstage, lockin):
    temps = temp_generator(start, stop, step)
    v1f = []
    v2f = []
    print("here")
    if hotstage.current_temperature()[0] != start:
        hotstage.set_temperature(start, 50)
        check_temperature(start, hotstage)
        print("not here")
        time.sleep(120)
    else:
        pass

    print("there")
    for temp in temps:
        if abs(temp - hotstage.current_temperature()[0]) > 0.1:
            hotstage.set_temperature(temp, rate)
            check_temperature(temp, hotstage)
            time.sleep(15)
        else:
            pass
        v1, v2 = lockin.read_dualharmonic_data()
        v1f.append(v1)
        v2f.append(v2)

    return v1f, v2f

def check_temperature(end_temp, hotstage):
    while True:
        temperature = hotstage.current_temperature()[0]
        if temperature is None:
            continue
        if abs(end_temp-temperature) <= 0.1:
            break
        time.sleep(0.1)

def temp_generator(start, stop, step):
    num_points = int((start - stop) / step) + 1
    temps = np.linspace(start, stop, num_points)
    return temps