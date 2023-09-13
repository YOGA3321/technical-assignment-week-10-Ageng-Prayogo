import RPi.GPIO as GPIO
from time import sleep
import Adafruit_ADS1x15
import requests
from hx711 import HX711
from w1thermsensor import W1ThermSensor

# Inisialisasi GPIO
GPIO.setmode(GPIO.BCM)

# Inisialisasi sensor HX711
hx = HX711(dout_pin=5, pd_sck_pin=6)
hx.set_scale_ratio(10)  # Ganti scale_ratio dengan nilai kalibrasi Anda
hx.reset()

# Inisialisasi ADC ADS1115
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1  # Ganti sesuai kebutuhan

# Inisialisasi sensor suhu W1ThermSensor
sensor_w1 = W1ThermSensor()

# Token dan label perangkat Ubidots
TOKEN = "BBFF-d1RJ4VTGj2RcJGWHxFx4FdDrfcK5sj"
DEVICE_LABEL = "base-srgt"  # Ganti dengan label perangkat Anda di Ubidots

def get_w1_temp():
    temperature = sensor_w1.get_temperature()
    return temperature

def get_hx_data():
    berat = hx.get_raw_data_mean()
    return berat

def get_ads_data():
    ampere = adc.read_adc(0, gain=GAIN)  # Membaca data ampere dari pin A0 pada ADC ADS1115
    volt = adc.read_adc(1, gain=GAIN)   # Membaca data voltage dari pin A1 pada ADC ADS1115
    return ampere, volt

def update_ubidots(suhu, berat, ampere, volt):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/{}".format(DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    payload = {
        "suhu": suhu,
        "berat": berat,
        "ampere": ampere,
        "volt": volt
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("Data berhasil dikirim ke Ubidots")
    else:
        print("Gagal mengirim data ke Ubidots. Kode status:", response.status_code)

try:
    while True:
        suhu = get_w1_temp()
        berat = get_hx_data()
        ampere, volt = get_ads_data()
        
        # Kirim data ke Ubidots
        update_ubidots(suhu, berat, ampere, volt)
        
        sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Program terminated.")
