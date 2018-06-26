from __future__ import division
import socket
import RPi.GPIO as GPIO
import time, math, sys
import Adafruit_MCP3008

# Set pi GPIOs
GPIO.setmode(GPIO.BCM)

#########################################################################
#                       Global Variables                                #
#########################################################################
HOST_IP = '192.168.0.199'
HOST_PORT = 5900

previous_temp = 0
diff_temp = 0
previous_liter = 0
minto = 1
sec = 1
power_energy = 0.0
flow_rate = 0
pulses = 0
liter2 = 0
tot_cnt = 0
secs = 0
flag = 0

#########################################################################
#              Setup Socket                                             #
#########################################################################

# Initializes an INET socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = HOST_IP
port = HOST_PORT

#########################################################################
#              Software SPI configuration:                              #
#########################################################################

# SPI ADC Pins

CLK = 11
MISO = 9
MOSI = 10
CS = 8

mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Set up reading flow rate/frequency sensor on GPIO
FLOW_RATE_IN_PIN = 27

# Set it as input
GPIO.setup(FLOW_RATE_IN_PIN, GPIO.IN)

s.connect((host, port))
print('Connected with: ', host)


def send_with_print(delay, msg):
    print(msg)  # , ":", flow)
    s.send(str.encode(msg))
    time.sleep(delay)


def send_data(flow=0, liters=0, minute=0, temperature=0, power_energy=0.0, hours=0,
              decimal_places=2):  # new_message, decimal_places=2):
    """
    this functions sends data

    :param flow: the caluclated flowrate from the sensor
    :param liters: used litres of water
    :param minute: timestamp
    :param temperature: temperature of the water
    :param power_energy: the delta power needed to raise the temperature to new value
    :param hours: timestamp
    :param decimal_places: return formatting for decimal
    :return:
    """
    send_delay_seconds = 0.6
    global names
    new_messages = str(names)

    flow = str(round(flow, decimal_places))
    send_with_print(send_delay_seconds, "L/min in float value in " + new_messages + ": " + flow + " ")

    liters = str(round(liters, decimal_places))
    send_with_print(send_delay_seconds, "Total  liters used in " + new_messages + ": " + liters + " ")

    minutes = str(int(minute))
    send_with_print(send_delay_seconds, "In total minute(s) " + new_messages + ": " + minutes + " ")

    temperatures = str(round(temperature, 0))
    send_with_print(send_delay_seconds, "Temperature of water in " + new_messages + ": " + temperatures + "  celsius  ")

    power_energy = str(round(power_energy, decimal_places))
    send_with_print(send_delay_seconds, "KWs is used " + new_messages + ": " + power_energy + " ")

    if hours > 0:
        hours = str(hours)
        new_messagew = "Total hour(s) " + new_messages + ": " + hours
        print(new_messagew)
        s.send(str.encode(new_messagew))
        time.sleep(send_delay_seconds)

    time.sleep(send_delay_seconds)
    #   space = ' '
    #   s.send(space)
    #   s.send(space)
    print("\n")
    print("\n")
    # time.sleep(send_delay_seconds)

    return flow, liters, minute, temperature


def calc_sensor_values(bytesValues, decimal_places=2):
    """
    This function calculates all the adc_values from the sensor

    :param bytesValues:
    :param decimal_places:
    :return:
    """
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
    # while True:# flag == 1:
    try:

        time_start = time.time()
        while pulses <= 5:
            gpio_curr = GPIO.input(FLOW_RATE_IN_PIN)

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
            resisT = round(resisT, decimal_places)
            A = float(1) / float(298.15)  # in 25 degree celsuis
            B = float(1) / float(3950)  # is the beta value
            lo = math.log(float(resisT) / float(50000))
            kelvin = A + B * lo
            kelvin = 1 / kelvin
            kelvin = round(kelvin, decimal_places)
            celsius = kelvin - 273.15

        except Exception as e:
            print("There is error in temperature sensor or code: {}".format(e))
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

        except Exception as e:
            print("Flow rate error: {}".format(e))
            return voltage

        seconds = (time_end - time_zero)
        seconds = int(seconds)
        global minto  # Variable for difference temperature and liters
        global current_temp  # variable for current temperature
        current_temp = celsius  # whatever temperature will be here assign to current temperature

        if seconds >= sec and current_temp >= 26:
            global previous_temp
            global diff_temp
            global previous_liter
            global power_energy

            if current_temp < previous_temp:
                diff_temp = -current_temp + previous_temp
                diff_temp = round(diff_temp, 2)
                print('Temperature of water is decressing : ', diff_temp)
            if previous_temp <= current_temp:
                diff_temp = current_temp - previous_temp

            diff_liter = liter - previous_liter
            previous_liter = liter
            previous_temp = current_temp
            sec += 1
            power_energy = (diff_liter * 4 * diff_temp) / 3412
            power_energy = round(power_energy, 4)
            print('Power is used liter(s)/second: ', power_energy)
            sec = seconds
        pulses = 0
        send_data(flow_rate, liter, minute, celsius, power_energy, hour)

    except KeyboardInterrupt:
        GPIO.cleanup()
        reply = 'crashed'
        s.send(str.encode(reply))

    except Exception as e:
        print('Error in calculation {}'.format(e))


names = raw_input("Name>   ")
time_zero = time.time()


# Runs continuously and grabs sensors values
# Hall effect from GPIO and temperature values from ADC

while True:
    delay_time = 0.06

    adc_values = [0] * 1
    for i in range(2):
        adc_values = mcp.read_adc(0)
    temp_byte = float(adc_values)
    time.sleep(delay_time)
    calc_sensor_values(temp_byte)
