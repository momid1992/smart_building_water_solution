from __future__ import division
import socket
import RPi.GPIO as GPIO
import time, math, sys
import Adafruit_MCP3008

# Set pi GPIOs
GPIO.setmode(GPIO.BCM)

#########################################################################
#              Setup Socket                                             #
#########################################################################
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '192.168.0.199'
port = 5900
#########################################################################
#              Software SPI configuration:                              #
#########################################################################
CLK = 11
MISO = 9
MOSI = 10
CS = 8
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
inpt = 27
GPIO.setup(inpt, GPIO.IN)
#########################################################################
#                       Global Variables                                #
#########################################################################

pervious_temp = 0
diff_temp = 0
pervious_liter = 0
minto = 1
sec = 1
power_energy = 0.0
flow_rate = 0
pulses = 0
liter2 = 0
tot_cnt = 0
secs = 0
flag = 0
s.connect((host, port))
print('Connected with: ', host)

####************************************************************************************#####
####                    First Function                                                  #####
####************************************************************************************#####


def printing(flow, liters, minute, temperature, power_energy, hours, decimalPlaces=2):  # new_message, decimalPlaces=2):
    times = 0.6
    global names
    new_messages = str(names)

    flows = round(flow, decimalPlaces)
    flow = str(flows)
    new_messagew = "L/min in float value in " + new_messages + ": " + flow + " "
    print(new_messagew)  # , ":", flow)
    s.send(str.encode(new_messagew))
    time.sleep(times)

    literss = round(liters, decimalPlaces)
    liters = str(literss)
    new_messagew = "Total  liters used in " + new_messages + ": " + liters + " "
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
    new_messagew = "Temperature of water in " + new_messages + ": " + temperatures + "  celsius  "
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

def calcus(bytesValues, decimalPlacese=2):
    global tot_cnt
    global liter2
    global pulses
    global secs
    global flow_rate
    global sec
    hour = 0
    rate_cnt = 0
    gpio_lasts = 0
    constant = 1
    # time_zero = time.time()
   # global flag
    #while True:# flag == 1:
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
            kelvin = A + B * lo
            kelvin = 1 / kelvin
            kelvin = round(kelvin, decimalPlacese)
            celsius = kelvin - 273.15

        except:
            print("There is error in temperature sensor or code: ")
            return voltage

        try:
            liter = float(tot_cnt * constant)
            # lits = (liter - 1)
            diff_time = round((time_end - time_start), 2)
            flow_rate = round((liter - liter2) / diff_time)
            liter2 = liter
            minute = (time_end - time_zero) / 60
            minutes = int(minute)
            if minutes >= 60:
                minutes = 0
                hour += 1

        except:
            print("Flow rate error: ", flow_rate)
            return voltage

        seconds = (time_end - time_zero)
        seconds = int(seconds)
        global minto  ## Variable for difference temperature and liters
        global current_temp  # verable for current temperature
        current_temp = celsius  # whatever temperature will be here assign to current temperature

        if seconds >= sec and current_temp >= 26:
            global pervious_temp
            global diff_temp
            global pervious_liter
            global power_energy

            if current_temp < pervious_temp:
                diff_temp = -current_temp + pervious_temp
                diff_temp = round(diff_temp, 2)
                print('Temperature of water is decressing : ', diff_temp)
            if pervious_temp <= current_temp:
                diff_temp = current_temp - pervious_temp

            diff_liter = liter - pervious_liter
            pervious_liter = liter
            pervious_temp = current_temp
            sec += 1
            power_energy = (diff_liter * 4 * diff_temp) / 3412
            power_energy = round(power_energy, 4)
            print('Power is used liter(s)/second: ', power_energy)
            sec = seconds
        pulses = 0
        printing(flow_rate, liter, minute, celsius, power_energy, hour)

    except KeyboardInterrupt:
        GPIO.cleanup()
        reply = 'crashed'
        s.send(str.encode(reply))
#flag = 0


names = raw_input("Name>   ")
time_zero = time.time()
while True:
    #flag = 1
    # global new_messages
    times = 0.06

    values = [0] * 1
    for i in range(2):
        values = mcp.read_adc(0)
    bytess = float(values)
    time.sleep(times)
    calcus(bytess)



