import utils
import time
import numpy as np

def run_temperature_sweep(start, stop, step, rate, wavelength, cellgap, file_name, hotstage, lockin):

    values_valid = utils.hotstage_values_check(start, stop, step, rate)
    if values_valid == True:
        print("Input params valid")
        temps = utils.temp_generator(start, stop, step)

        if hotstage.current_temperature()[0] != start:
            print(f"Going to start temperature at {start} C")
            hotstage.set_temperature(start, 50)
            hotstage.validate_temperature(start)
            print(f"At {start} C waiting for initial stabilisation")
            time.sleep(90)
        else:
            pass

        calc = utils.analysis(cellgap, wavelength)
        output = utils.output_writer(file_name)
        for temp in temps:
            at_temp = False
            print(f"Running {temp} C process")
            hotstage.set_temperature(temp, rate)
            print(f"Waiting for stabilisation at {temp} C")
            time.sleep(10)   
            at_temp = hotstage.validate_temperature(temp)
            time.sleep(10)
            print(f"Temperature stabilised at {temp} C")

            n=0
            while n<120:
            # seems silly to stick all of this in a while loop but cant think 
            # of a better way to continously check for temp and status
            # it does allow for timeout check so maybe not so bad
                c_temp, status = hotstage.current_temperature()
                if at_temp == True and status == "Holding":
                    x1, x2 = lockin.read_dualharmonic_data()
                    ret, biref = calc.compute_biref(x1, x2)
                    output.write_csv_row([c_temp, x1, x2, ret, biref])
                    print(f"Measurement at {temp} C done")
                    time.sleep(1)
                    break
                else:
                    n += 1
                    time.sleep(1)
                    continue
            if n>=120:
                output.write_csv_row([c_temp, np.nan, np.nan, np.nan, np.nan])
                print(f"Measurement at {temp} C skipped due to timeout")
        
        output.close()

    elif values_valid == False:
        print("Input params invalid")