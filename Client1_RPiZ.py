from __future__ import division
import socket
import RPi.GPIO as GPIO
import time, math, sys
import Adafruit_MCP3008

GPIO.setmode(GPIO.BCM)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '192.168.0.199'
port = 5900
# Software SPI configuration:
CLK = 11
MISO = 9
MOSI = 10
CS = 8
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
inpt = 27
GPIO.setup(inpt, GPIO.IN)

pervious_temp = 0
diff_temp = 0
pervious_liter = 0
minto = 1
sec = 1
power_energy = 0.0
s.connect((host, port))
print('Connected with: ', host)

pulses = 0
liter2 = 0
names = input("Name")
minute = 0

minutes2 = 0


####************************************************************************************#####
####                    First Function                                                  #####
####************************************************************************************#####

def sending(flow, liters, minute, temperature, power_energy, hours, decimalPlaces=2):  # new_message, decimalPlaces=2):

    times = 0.6
    global names
    new_messages = str(names)

    flows = round(flow, decimalPlaces)
    flow = str(flows)
    new_messagew = "L/min " + new_messages + ": " + flow + " "
    print(new_messagew)  # , ":", flow)
    s.send(str.encode(new_messagew))
    time.sleep(times)

    literss = round(liters, decimalPlaces)
    liters = str(literss)
    new_messagew = "Total  liter(s) used in " + new_messages + ": " + liters + " "
    print(new_messagew)
    s.send(str.encode(new_messagew))
    time.sleep(times)

    minute = int(minute)
    minutes = str(minute)
    new_messagew = "In total minute(s) " + new_messages + ": " + minutes + " "
    print(new_messagew)
    s.send(str.encode(new_messagew))
    time.sleep(times)

    temperature = round(temperature, 0)
    temperatures = str(temperature)
    new_messagew = "Temperature of water in " + new_messages + ": " + temperatures + " "
    print(new_messagew)
    s.send(str.encode(new_messagew))
    time.sleep(times)

    power_energy = round(power_energy, decimalPlaces)
    power_energys = str(power_energy)

    new_messagew = "KWs is used " + new_messages + ": " + power_energys + " "
    print(new_messagew)
    s.send(str.encode(new_messagew))
    if hours > 0:
        hours = str(hours)
        new_messagew = "Total hour(s) " + new_messages + ": " + hours
        print(new_messagew)
        s.send(str.encode(new_messagew))
        time.sleep(times)

    time.sleep(times)
    #   space = ' '
    #   s.send(space)
    #   s.send(space)
    print("\n")
    print("\n")
    # time.sleep(times)

    return flow, liters, minute, temperature


####***************************************************************************************####
####                            2nd Function                                               ####
####***************************************************************************************####


tot_cnt = 0


def calcus(bytesValues, decimalPlacese=2):
    global tot_cnt
    global minutes2
    global minute
    minute = 0

    global liter2
    hour = 0

    rate_cnt = 0
    gpio_lasts = 0
    constant = 1
    time_zero = time.time()

    while True:

        global pulses

        try:
            time_start = time.time()

            while pulses <= 5:
                gpio_curr = GPIO.input(inpt)
                if gpio_curr != 0 and gpio_curr != gpio_lasts:
                    pulses += 1
                gpio_lasts = gpio_curr
            tot_cnt += 1
            rate_cnt += 1
            time_end = time.time()

            try:
                voltage = ((bytesValues * 3.3) / 1023)
                voltageout = 3.3 - voltage
                resisT = float(10000) * float(voltage) / float(voltageout)
                resisT = round(resisT, decimalPlacese)
                A = float(1) / float(298.15)  # in 25 degree celsuis
                B = float(1) / float(3950)  # is the beta value
                lo = math.log(float(resisT) / float(50000))
                kalvin = A + B * lo
                kalvin = 1 / kalvin
                kalvin = round(kalvin, decimalPlacese)
                celsius = kalvin - 273.15
            except:
                print("There is an error in temperature sensor or code: ")
                return voltage

            liter = float(tot_cnt * constant)
            lits = (liter - 1)
            diff_time = round((time_end - time_start), 2)
            flow_rate = round((lits - liter2) / diff_time)
            liter2 = lits
            minute = ((time_end - time_zero) / 60) - (60 * minutes2)
            minute = int(minute)

            if minute >= 60:
                hour += 1
                minute = 0
                minutes2 += 1
            # else:

            seconds = minute * 60
            global sec
            global minto  ## Variable for difference temperature and liters
            global current_temp  # verable for current temperature
            current_temp = celsius  # whatever temperature will be here assign to current temperature

            if seconds >= sec and current_temp >= 30:
                global pervious_temp
                global diff_temp
                global pervious_liter
                global power_energy
                if current_temp < pervious_temp:
                    diff_temp = -current_temp + pervious_temp
                    print('Power is decreasing : ', diff_temp)
                if pervious_temp <= current_temp:
                    diff_temp = current_temp - pervious_temp
                diff_liter = lits - pervious_liter
                pervious_liter = lits
                pervious_temp = current_temp
                sec += 1
                power_energy = (diff_liter * 4 * diff_temp) / 3412
                print('Power is used liter(s)/second: ', power_energy)

            pulses = 0
            sending(flow_rate, lits, minute, celsius, power_energy, hour)
        except KeyboardInterrupt:
            GPIO.cleanup()
            reply = 'crashed'
            s.send(str.encode(reply))

    return voltage, lo


while True:
    # global names
    times = 0.6
    new_messages = str(names)
    print("Hello! sending data: " + new_messages)

    s.send(str.encode(new_messages))
    values = [0] * 1
    for i in range(2):
        values = mcp.read_adc(0)
    bytess = float(values)
    time.sleep(times)
    calcus(bytess)



