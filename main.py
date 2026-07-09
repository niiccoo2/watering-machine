import machine
import time
import network
import urequests
from secrets import secrets

moisture = machine.ADC(27)
rtc = machine.RTC()
rtc.datetime((2026, 1, 1, 1, 0, 0, 0, 0))
pump = machine.Pin(0, mode=machine.Pin.OUT, value=0)

SSID = secrets["ssid"]
PASSWORD = secrets["password"]
PHONE_NUMBER = secrets["phone_number"]
API_KEY = secrets["callmebot_key"]
DRY_VALUE = 56500
WET_VALUE = 29000

# Init Wi-Fi Interface
def init_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # Connect to your network
    wlan.connect(ssid, password)
    # Wait for Wi-Fi connection
    connection_timeout = 10
    while connection_timeout > 0:
        if wlan.status() >= 3:
            break
        connection_timeout -= 1
        print('Waiting for Wi-Fi connection...')
        time.sleep(1)
    # Check if connection is successful
    if wlan.status() != 3:
        return False
    else:
        print('Connection successful!')
        network_info = wlan.ifconfig()
        print('IP address:', network_info[0])
        return True

def send_message(phone_number, api_key, message):
    # Safely encode spaces and percent symbols for the web address
    formatted_message = message.replace(" ", "+").replace("%", "%25")
    
    url = f'https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={formatted_message}&apikey={api_key}'

    try:
        response = urequests.get(url)
        if response.status_code == 200:
            print('Success!')
        else:
            print('Error:', response.status_code)
            print(response.text)
        response.close()
    except Exception as e:
        print('Network error sending message:', e)

past_data: list[float] = []
average_value: float = 1
last_water_time = 0

try: 
    # Connect to WiFi
    if init_wifi(SSID, PASSWORD):
        send_message(PHONE_NUMBER, API_KEY, "Plant Machine turned on!")

        while True:
          raw_value = moisture.read_u16()

          if raw_value < WET_VALUE or raw_value > DRY_VALUE:
            print(f"Raw value ({raw_value}) is out of range.")
            continue # if out of range: skip

          if len(past_data) >= 50: # if we have enough data
            average_value = sum(past_data)/len(past_data)
            print(f"Done calcing avg moisture: {average_value}")
            past_data = []

            if average_value < .32: # if under 32%
              if time.time() - last_water_time > 600: # if over ten mins from last water

                # watering logic here
                print("Watering now!")

                pump.on()
                time.sleep(5)
                pump.off()

                send_message(PHONE_NUMBER, API_KEY, f"Watering plant because moisture is {average_value}")

                last_water_time = time.time()
              else:
                print("Tried to water, but not enough time has passed.")

          else:
            percentage = (raw_value-DRY_VALUE)/(WET_VALUE-DRY_VALUE)

            past_data.append(percentage)

            print(percentage, raw_value)

          time.sleep(.2)

except Exception as e:
    print('Error:', e)

