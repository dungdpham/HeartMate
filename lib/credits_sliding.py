import ssd1306
from machine import Pin, I2C
import time

#i2c = I2C(1, sda=Pin(14), scl=Pin(15))
#oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Set font size
font_size = 2

# Define the speed of the animation
sliding_speed = 1000  # Increase this value to make the text move faster

# Loop counter for the animation
sliding_counter = 128

# Infinite loop for the animation
def credits_sliding(oled):
    global sliding_counter
    
    # Set starting x-axis position of the text
    x_pos1 = (sliding_counter) % (128 + len("Sakari Lukkarinen") * font_size * 6)
    x_pos2 = (sliding_counter - len("Adrian Garcia") * font_size * 8) % (128 + len("Hanh Hoang") * font_size * 6)
    x_pos3 = (sliding_counter - len("Hanh Hoang") * font_size * 8) % (128 + len("Arijana Maatta") * font_size * 6)
    x_pos4 = (sliding_counter - len("Arijana Maatta") * font_size * 8) % (128 + len("Dung Pham") * font_size * 6)
    x_pos5 = (sliding_counter - len("Dung Pham") * font_size * 8) % (128 + len("Sakari Lukkarinen") * font_size * 6)


    # Clear the display
    oled.fill(0)

    # Display the text at the current x-axis position
    oled.text("Sakari Lukkarinen", 128 - x_pos1, font_size * 6 * 0, font_size)
    oled.text("Adrian Garcia", x_pos2, font_size * 6 * 1, font_size)
    oled.text("Hanh Hoang", 128 - x_pos3, font_size * 6 * 2, font_size)
    oled.text("Arijana Maatta", x_pos4, font_size * 6 * 3, font_size)
    oled.text("Dung Pham", x_pos5, font_size * 6 * 4, font_size)

    oled.show()

    # Wait for a short period of time to create the animation effect
    time.sleep(1/sliding_speed)

    # Increment the loop counter
    sliding_counter += 1
