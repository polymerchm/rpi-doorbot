from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.core.render import canvas
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime



# Initialize OLED display dimensions
WIDTH = 128
HEIGHT = 64

# Set up I2C communication with the OLED display

serial = i2c(port=1, address=0x3C)

# Device type
device = sh1106(serial)

# Display loop
while True:
	
	# Get time & date
	time = datetime.now().strftime("%H:%M")
	date = datetime.now().strftime("%d/%m/%y")
	
	# Select font(s) and draw to display
	with canvas(device) as draw:
		FontTemp = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",21)
		draw.text((12, 7), (date), font=FontTemp, fill="white")
		FontTemp = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",42)
		draw.text((0, 25), (time), font=FontTemp, fill="white")
		
sleep(1)
