# DHT30 sensor on Pi pico W with report to Domoticz using Micropython

---

## Description

This project utilizes a Raspberry Pi Pico-W for accessing Adafruit’s DHT30 sensor for temperature and relative humidity data, and sending that to a local instance of Domoticz. All code is in Micropython. Even though Adafruit’s Circuitpython has excellent support for the DHT30, I found it to be a little overkill for a small project like this. Moreover the support for Wifi was at the time of development not yet robust.

The code is deliberately kept simple, using only what is required to get reliable repeated measurement with lw frequency. Extending from this point should be straightforward. The documentation is a little extensive so it is understandable for anyone without much prior knowledge.

## Installation

Download the Python files, run them through e.g. Thonny on a second Raspberry Pi on your pico. Flash them to the pico as you would for any other piece of Micropython code, and that should be it.

## Usage

Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## SHT30 Technical background

To fully understand the SHT30 search for the Sensiron SHT3x-DIS check the pdf-documentation in this repository. For our purpose we only need the command syntax for a few commands, notably making and sending a single measurement. The documentation lists many more. Once you know  the principle, then using any of the other commands is straightforward.

The manufacturers documentation indicates that sending 0x2C06 will trigger the sensor toe perform a measurement. The i2c address is standard 0x44 for the DHT30. Ignore the 'high repeatability with clock stretching' for this simple case. Once the measurement is completed, the sensor will return 6 bytes, two data-bytes and a crc-byte for the temperature, followed by two data-bytes and crc-byte for the relative humidity.

![measurement.PNG](.attachments.1265/measurement.PNG)

Assuming no data corruption the temperature and relative humidity can be decoded from the received bytes using the following formula's.

![decode.png](.attachments.1265/decode.png)

In general it makes sense to check if the computed checksum matches the transferred CRC-byte. See code example below on how that is done. The manufacturer's specification is as follows (NB in Python we need to explicitly code the Polynomial as 0x131 as we can only XOR on integers):

![crc.png](.attachments.1265/crc.png)

## The i2c bus on the picoW

The PicoW and the Pico both have two hardware i2c buses. The 'frequency' parameter defaults to 400kHz. The sensor supports even higher speeds. However, this requires good and short wires. In my case I needed to extend the wire between the sensor and the Pico and had to lower lowering the frequency to about 0kHz to get reliable communication over the bus. In principle this could handicap other devices on the same bus. In this example the DHT30 is the only device on the i2c-bus, and we can freely choose the frequency.

Assignment of GPIO pins to the data (sda) and clock (clk) lines can be done with calls to Micropython's 'machine' module.

## Example code for communicating with the DHT30

If you want to get started and check whether everything is wired up correctly, it should suffice to copy paste the code below and check you get a return, albeit gibbrisch without decoding, from the DHT30. We use pins 16 and 17 for i2cbus 0, but it should work with suitable pair (check the pico pinning documentation) of i2cbus pins.

```
import time
from machine import Pin, I2C, 

sdaPIN = Pin(16)
sclPIN = Pin(17)

# sda_gpio16 and scl_gpio17 are linked to i2c-bus 0
i2cbus = 0        
i2c    = I2C(i2cbus,sda=sdaPIN, scl=sclPIN, freq=10000)

# send break and reset to start with clean state
# 0x44 is address of Adafruit's DHT30
  
i2c.writeto(0x44,b'\x30\x93')
time.sleep_ms(10)
i2c.writeto(0x44,b'\x30\xA2')
time.sleep_ms(10)

while True:
    # single measurement with high repeatability
    i2c.writeto(0x44,b'\x2C\x06') 
    time.sleep_ms(10)
    # DHT30 will send 6 bytes as reply
    data = i2c.readfrom(0x44,6)
    time.sleep(1)
    # Without decoding the following will print gibberish,  
    # but it does prove correct bus-communication
    print(data) 
```

Once you are happy the communication between the pico and the DHT30 works as expected it is time to extract the data. Using the conversion formula’s above we can replace the print(data) statement with:

```
    temp = round(((data[0] * 256 + data[1]) * 175 / 0xFFFF) - 45,1)
    hum = round((data[3] * 256 +  data[4]) * 100.0 / 0xFFFF,1)
    print(temp, hum)
```

This should get you the temperature in Celsius and the relative humidity in %

We have ignored any possible data corruption to this point. Add the following function to your code, and pass it the 6-byte data array. If it returns True then the data passes the CRC test and there is a high probability it is not corrupted in transmission.

```
def check_crc(raw_data: bytes) -> bool :
    crc_pass = True
    for i in range(2):
        data = raw_data[i*3:i*3 + 3]
        crc = 0xFF                            # crc initialization
        for byte in data[:-1]: 
            crc ^= byte;                      # NB, both are type 'int'
            for _ in range(8, 0, -1):
                if crc & 0x80:                # if leading bit = 1, then
                    crc = (crc << 1) ^ 0x131  # XOR crc with polynomial
                else:
                    crc <<= 1
        if data[-1] != crc:
            crc_pass = False
    return crc_pass
```

## Support

Raise an 'issue' if you have any questions or suggestions.

## Roadmap

There appear to be no obvious extensions to this simple functionality, hence there is no roadmap. But raise an 'issue' if you think this can be pushed further.

## Credits

[R.Sanchez](https://github.com/rsc1975/micropython-sht30/blob/master/sht30.py) wrote an implementation for accessing the DHT-30 for a totally different, and now obsolete(?), board that proved a useful insight. If anything it was a clear indication that a simple approach with Micropython was possible. In fact for the Pico it required even less code to communicate with the DHT30.

## Project status

The project achieves it's current aim to demonstrate a simple implementation, hence it is frozen (for now).
