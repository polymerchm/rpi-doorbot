#!/usr/bin/env python

import pigpio

class decoder:

   """

   Weigand timing

   ______    _______   ___________________________________ w0
         |  |       |  |
         |  |       |  |
         |  |       |  |
         |  |       |  |
         |  |       |  |
          --         --
        100 us pulse width
   ____________    _______   ______________________________ w1
               |  |       |  |
               |  |       |  |
               |  |       |  |
               |  |       |  |
               |  |       |  |
                --         --
            ^  ^
            |  |
            20-100 ms interpulse gap  
 
 binary 0101

 data assummed to end after 26/32 bits or 10*100 ms (1 second) gap
 since last pulse
 
 
 
   A class to read Wiegand codes of an arbitrary length.

   The code length and value are returned.

   EXAMPLE

   #!/usr/bin/env python

   import time

   import pigpio

   import wiegand

   def callback(bits, code):
      print("bits={} code={}".format(bits, code))

   pi = pigpio.pi()

   w = wiegand.decoder(pi, 14, 15, callback)

   time.sleep(300)

   w.cancel()

   pi.stop()
   """

   def __init__(self, pi, gpio_0, gpio_1, callback, bit_timeout=5):

      """
      Instantiate with the pi, gpio for 0 (green wire), the gpio for 1
      (white wire), the callback function, and the bit timeout in
      milliseconds which indicates the end of a code.
      
      NB: the output of the reader is 0-5V.   Must be reduced to 3.3V to avoid
      smoking the micro.

      The callback is passed the code length in bits and the value.
      _cb() is the low level callback when a trigger occurs on a pin
      """

      self.pi = pi
      self.gpio_0 = gpio_0
      self.gpio_1 = gpio_1

      self.callback = callback

      self.bit_timeout = bit_timeout

      self.in_code = False

      self.pi.set_mode(gpio_0, pigpio.INPUT)
      self.pi.set_mode(gpio_1, pigpio.INPUT)

      self.pi.set_pull_up_down(gpio_0, pigpio.PUD_UP)
      self.pi.set_pull_up_down(gpio_1, pigpio.PUD_UP)

      # set low level call back for trigger events on the two pins.
      self.cb_0 = self.pi.callback(gpio_0, pigpio.FALLING_EDGE, self._cb)
      self.cb_1 = self.pi.callback(gpio_1, pigpio.FALLING_EDGE, self._cb)

   def _cb(self, gpio, level, tick):

      """
            low level callback for edge trigger or timeout event

            gpio is pin that triggered the callback
            level is return as either 
               0 (falling edge)
               1 (rising edge)
               pigpio.TIMEOUT, if timeout has been set
            tick is microsec since boot (72 minutes rollover)
      """

      if level < pigpio.TIMEOUT: #  edge trigger before timeout
         if self.in_code == False: # initial bit
            self.bits = 1
            self.num = 0

            self.in_code = True
            self.code_timeout = 0 # bit 0 is dat_0 timeout flat, bit 2 is dat_1 timeout flag
            # set timers on dat0 and dat1
            self.pi.set_watchdog(self.gpio_0, self.bit_timeout) 
            self.pi.set_watchdog(self.gpio_1, self.bit_timeout)
         else: # next bit
            self.bits += 1
            self.num = self.num << 1 # shift accumulator

         if gpio == self.gpio_0:
            self.code_timeout = self.code_timeout & 2 # clear gpio 0 timeout
            # a zero is effectively appended by the shift above
         else:
            self.code_timeout = self.code_timeout & 1 # clear gpio 1 timeout
            self.num = self.num | 1 # append high bit

      else: # timeout occured

         if self.in_code:

            if gpio == self.gpio_0:
               self.code_timeout = self.code_timeout | 1 # set timeout on gpio 0
            else:
               self.code_timeout = self.code_timeout | 2 # set timeout on gpio 1

            if self.code_timeout == 3: # both gpios timed out
               self.pi.set_watchdog(self.gpio_0, 0)
               self.pi.set_watchdog(self.gpio_1, 0)
               self.in_code = False
               self.callback(self.bits, self.num)

   def cancel(self):

      """
      Cancel the Wiegand decoder.
      """

      self.cb_0.cancel()
      self.cb_1.cancel()



if __name__ == "__main__":

   import time

   import pigpio
   import DoorBot.Config as Config



   def callback(bits, value):
      print("bits={} value={}".format(bits, value))

   pi = pigpio.pi()

   gpio = Config.get('gpio')
   data0 = gpio['data0']
   data1 = gpio['data1']

   print("Start to decode")


   w = decoder(pi, data0, data1,  callback)

   time.sleep(300) #collect data for 5 minutes

   w.cancel()

   pi.stop()
