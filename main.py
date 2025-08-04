import numpy as np

import utils
import time
import disp

def run_temperature_sweep(start, stop, step, rate, wavelength, cellgap, file_name, hotstage, lockin):

    if not utils.hotstage_values_check(start, stop, step, rate):
        print("Input params invalid")
        return
    
    print("Input params valid")
    temps = utils.temp_generator(start, stop, step)

    current_temp, _ = hotstage.current_temperature()
    if current_temp != start:
        print(f"Going to start temperature at {start} C")
        hotstage.set_temperature(start, 50)
        hotstage.validate_temperature(start)
        print(f"At {start} C waiting for initial stabilisation")
        time.sleep(60)

    calc = utils.Analysis(cellgap, wavelength)
    output = utils.OutputWriter(file_name)
    plotter = disp.Plotter()
    try:
        for temp in temps:
            print(f"Running {temp} C process")
            hotstage.set_temperature(temp, rate)
            print(f"Waiting for stabilisation at {temp} C")
            time.sleep(10)   
            at_temp = hotstage.validate_temperature(temp)
            print(f"Temperature stabilised at {temp} C")

            for _ in range(120):
                c_temp, status = hotstage.current_temperature()
                if at_temp and status == "Holding":
                    x1, x2 = lockin.read_dualharmonic_data()
                    ret, biref = calc.compute_biref(x1, x2)
                    output.write_csv_row([c_temp, x1, x2, ret, biref])
                    print(f"[{time.strftime('%H:%M:%S')}] Measurement at {temp} C done")
                    plotter.update(c_temp, ret, biref)

                    time.sleep(1)
                    break
                time.sleep(1)
            else:
                output.write_csv_row([c_temp, np.nan, np.nan, np.nan, np.nan])
                print(f"Measurement at {temp} C skipped due to timeout")
    finally:
        output.close()
        return
    
def run_fast_temperature_sweep(start, stop, wavelength, cellgap, file_name, hotstage, lockin):

    current_temp, _ = hotstage.current_temperature()
    if current_temp != start:
        print(f"Going to start temperature at {start} C")
        hotstage.set_temperature(start, 100)
        hotstage.validate_temperature(start)
        print(f"At {start} C waiting for initial stabilisation")
        time.sleep(30)

    calc = utils.Analysis(cellgap, wavelength)
    output = utils.OutputWriter(file_name)
    plotter = disp.Plotter()

    try:
        hotstage.set_temperature(stop, 10)

        while True:
            c_temp, _ = hotstage.current_temperature()

            if round(abs(stop - c_temp), 2) <= 0.1:
                break

            x1, x2 = lockin.read_dualharmonic_data()
            ret, biref = calc.compute_biref(x1, x2)
            output.write_csv_row([c_temp, x1, x2, ret, biref])
            print(f"[{time.strftime('%H:%M:%S')}] Measurement at {c_temp:.2f} °C done")
            plotter.update(c_temp, ret, biref)

            time.sleep(1)
    finally:
        output.close()
        return