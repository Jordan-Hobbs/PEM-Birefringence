import utils
import time
import numpy as np

def run_temperature_sweep(start, stop, step, rate, hotstage, lockin):
    values_valid = utils.hotstage_values_check(start, stop, step, rate)
    if values_valid == True:
        print("Input params valid")
        temps = utils.temp_generator(start, stop, step)
        v1f = []
        v2f = []
        m_temps = []

        if hotstage.current_temperature()[0] != start:
            print(f"Going to start temperature at {start} C")
            hotstage.set_temperature(start, 50)
            hotstage.validate_temperature(start)
            print(f"At {start} C waiting for initial stabilisation")
            time.sleep(90)
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


