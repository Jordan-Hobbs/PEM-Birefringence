from instruments import LinkamHotstage, SRLockinAmplifier
from scipy.special import jv
import time, numpy as np


def run_temperature_sweep(start, stop, step, rate, hotstage, lockin):
    values_valid = hotstage_values_check(start, stop, step, rate)
    if values_valid == True:
        print("Input params valid")
        temps = temp_generator(start, stop, step)
        v1f = []
        v2f = []
        m_temps = []

        if hotstage.current_temperature()[0] != start:
            print(f"Going to start temperature at {start} C")
            hotstage.set_temperature(start, 50)
            hotstage.validate_temperature(start)
            print(f"At {start} C waiting for initial stabilisation")
            time.sleep(60)
        else:
            pass

        for temp in temps:
            attemp = False
            print(f"Running {temp} C process")
            hotstage.set_temperature(temp, rate)
            print(f"Waiting for stabilisation at {temp} C")
            time.sleep(10)   
            attemp = hotstage.validate_temperature(temp)
            time.sleep(10)
            print(f"Temperature stabilised at {temp} C")

            n=0
            while n<120:
            # seems silly to stick all of this in a while loop but cant think 
            # of a better way to continously check for temp and status
            # it does allow for timeout check so maybe not so bad
                c_temp, status = hotstage.current_temperature()
                if attemp == True and status == "Holding":
                    x1, x2 = lockin.read_dualharmonic_data()
                    m_temps.append(c_temp)
                    v1f.append(x1)
                    v2f.append(x2)
                    print(f"Measurement at {temp} C done")
                    time.sleep(1)
                    break
                else:
                    n += 1
                    time.sleep(1)
                    continue
            if n>=120:
                m_temps.append(np.nan)
                v1f.append(np.nan)
                v2f.append(np.nan)
                print(f"Measurement at {temp} C skipped due to timeout")
        
        hotstage.close()
        lockin.close()
        return m_temps, v1f, v2f
    
    elif values_valid == False:
        hotstage.close()
        lockin.close()
        return False, False, False


def data_analysis(v1f, v2f):
    ret =[]
    j1 = jv(1, np.pi/2)
    j2 = jv(2, np.pi/2)
    
    for v1, v2 in zip(v1f, v2f):
        if v1 == 0 or v2 == 0:
            ret.append(np.nan)
            print("Careful! one value found at zero")
            continue

        delta = np.arctan((v1/v2)*(j2/j1))
        if v1>0 and v2>0:
            ret.append((delta*635e-9)/(2*np.pi))
            continue
        elif v1>0 and v2<0:
            ret.append(((delta+np.pi)*635e-9)/(2*np.pi))
            continue
        else:
            ret.append((delta*635e-9)/(2*np.pi))
            print("Careful! one value out of range")
            continue
        # needs the rest of the conditionals this else is not a correct solution
    return ret

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