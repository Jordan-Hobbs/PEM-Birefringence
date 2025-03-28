import pyvisa
import threading
import time

class LinkamHotstage:
    def __init__(self, address: str) -> None:
        self.address = address
        self.lock = threading.Lock()
        self.initialise_linkam()

    def initialise_linkam(self) -> None:
        rm = pyvisa.ResourceManager()

        self.linkam = rm.open_resource(self.address)
        self.init = False

        self.linkam.baud_rate = 19200  # type: ignore

        self.linkam.read_termination = "\r"  # type: ignore
        self.linkam.write_termination = "\r"  # type: ignore

        self.linkam.timeout = 3000

        try:
            temp = self.current_temperature()
            print("Linkam Connected")

        except pyvisa.errors.VisaIOError:
            print(
                "Could not connect to Linkam Hotstage. Try different address \
                (make sure it is switched on)"
            )

    def set_temperature(self, T: float, rate: float = 20.0) -> None:
        if self.init:
            with self.lock:
                self.linkam.write(f"R1{int(rate * 100)}")  # type: ignore
                self.linkam.read()  # type: ignore
                self.linkam.write(f"L1{int(T * 10)}")  # type: ignore
                self.linkam.read()  # type: ignore
        else:
            with self.lock:
                self.linkam.write(f"R1{int(rate * 100)}")  # type: ignore
                self.linkam.read()  # type: ignore
                self.linkam.write(f"L1{int(T * 10)}")  # type: ignore
                self.linkam.read()  # type: ignore
                self.linkam.write("S")  # type: ignore
                self.linkam.read()

                self.init = True

    def stop(self) -> None:
        with self.lock:
            self.linkam.write("E")  # type: ignore
            self.linkam.read()  # type: ignore
            self.init = False

    def current_temperature(self) -> tuple[float, str]:
        with self.lock:
            try:
                self.linkam.write("T")  # type: ignore
                raw_string = self.linkam.read_raw()  # type: ignore
            except UnicodeDecodeError:
                return 0.0, 0.0
        status_byte = int(raw_string[0])

        if status_byte == 1:
            status = "Stopped"
        elif status_byte == 16 or status_byte == 17:
            status = "Heating"
        elif status_byte == 32 or status_byte == 33:
            status = "Cooling"
        elif status_byte == 48 or status_byte == 49:
            status = "Holding"
        else:
            status = "Dunno"
        try:
            temperature = int(raw_string[6:10], 16) / 10.0
        except ValueError:
            return 0.0, 0.0
        return temperature, status

    def validate_temperature(self, end_temp):
        while True:
            temperature = self.current_temperature()[0]
            if temperature is None:
                continue
            print(temperature)
            if round(abs(end_temp-temperature),1) <= 0.1:
                break
            time.sleep(0.1)
        return True

    def close(self):
        self.linkam.close()

class SRLockinAmplifier:
    def __init__(self, address: str):
        self.address = address
        self.initialise_lockin()

    def initialise_lockin(self):
        rm = pyvisa.ResourceManager()
        self.lockin = rm.open_resource(self.address)
        try:
            self.send_command("ADF 1") # set lockin to default WITHOUT changing the address settings so connection is maintained. 
            print("Lockin connected")
        except pyvisa.errors.VisaIOError:
            print(
                "Could not connect to lockin. Try different address \
                (is it set to address 12?)"
            )

    def initialise_dualharmonic(self):
        self.send_command("REFMODE 1") # sets dual harmonic mode
        self.send_command("IE 2") # reference set to front input
        self.send_command("REFN1 1") # sets channel one to 1f mode
        self.send_command("REFN2 2") # sets channel two to 2f mode
        self.send_command("IMODE 0") # current mode off
        self.send_command("VMODE 1") # voltage input on channel A
        self.send_command("SEN 25") # sets senstivity - check it is suitible

    def read_dualharmonic_data(self):
        v1, b1 = self.send_command("X1.") # asks for X value from channel one
        v2, b2 = self.send_command("X2.") # asks for X value from channel two
        return float(v1), float(v2)

    def send_command(self, sCmd):
        self.lockin.write(sCmd)
        sResponse =  ''
        nStatusByte = int(self.lockin.stb)  
        while (nStatusByte & 0x80 != 0x80): # repeatedly read status byte until bit 7 is asserted 
            nStatusByte = int(self.lockin.stb) # meaning data available
            if (nStatusByte & 0x01 == 0x01): # if bit 1 asserted then break
                break

        if (nStatusByte & 0x80 == 0x80): # if data available
            sResponse = self.lockin.read() # read data
        
        while (nStatusByte & 0x01 != 0x01): # read status byte until bit 1 is asserted
            nStatusByte = int(self.lockin.stb)

        nStatusByte = nStatusByte & 143 # mask out bits 4, 5 & 6 which are not consistent across all instruments

        return sResponse, nStatusByte
    
    def close(self):
        self.lockin.close()