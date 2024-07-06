import time
import board
import digitalio
import neopixel

# Configuration
pixel_pin = board.D2  # Pin where the NeoPixel strip is connected
num_pixels = 10       # Number of NeoPixels in the strip
switch1_pin = board.D3  # Pin for switch 1
switch2_pin = board.D4  # Pin for switch 2
switch3_pin = board.D0  # Pin for switch 3 (mode control)

# Initialize NeoPixel strip
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False)

# Initialize switches
switch1 = digitalio.DigitalInOut(switch1_pin)
switch1.direction = digitalio.Direction.INPUT
switch1.pull = digitalio.Pull.UP

switch2 = digitalio.DigitalInOut(switch2_pin)
switch2.direction = digitalio.Direction.INPUT
switch2.pull = digitalio.Pull.UP

switch3 = digitalio.DigitalInOut(switch3_pin)
switch3.direction = digitalio.Direction.INPUT
switch3.pull = digitalio.Pull.UP

def interpolate_color(color1, color2, factor):
    """Interpolate between two colors."""
    return (
        int(color1[0] + (color2[0] - color1[0]) * factor),
        int(color1[1] + (color2[1] - color1[1]) * factor),
        int(color1[2] + (color2[2] - color1[2]) * factor)
    )

def transition_colors_fade(color1, color2, transition_duration, hold_duration):
    """Transition all LEDs from color1 to color2 over 'transition_duration' seconds, holding each color for 'hold_duration' seconds."""
    steps = 50  # Number of steps in the transition
    delay = transition_duration / steps  # Delay between steps

    # Hold the initial color
    pixels.fill(color1)
    pixels.show()
    time.sleep(hold_duration)

    # Fade transition
    for step in range(steps + 1):
        factor = step / steps
        intermediate_color = interpolate_color(color1, color2, factor)
        pixels.fill(intermediate_color)
        pixels.show()
        time.sleep(delay)

    # Hold the final color
    pixels.fill(color2)
    pixels.show()
    time.sleep(hold_duration)

def transition_colors_sequential(color1, color2, transition_duration, hold_duration):
    """Transition LEDs one by one from color1 to color2 over 'transition_duration' seconds, then hold the final color for 'hold_duration' seconds."""
    delay = transition_duration / num_pixels  # Delay for each LED

    for i in range(num_pixels):
        pixels[i] = color2  # Change the current LED to the target color
        pixels.show()
        time.sleep(delay)

    # After all LEDs have transitioned, hold the final color
    pixels.fill(color2)
    pixels.show()
    time.sleep(hold_duration)

# Define colors
color_red = (255, 0, 0)    # Red
color_green = (0, 255, 0)  # Green
color_cyan = (0, 255, 255) # Cyan
color_purple = (128, 0, 128) # Purple

# Initial color and transition state
current_color = color_red
in_transition_mode = False

while True:
    # Read switch states
    switch1_state = switch1.value
    switch2_state = switch2.value
    switch3_state = switch3.value

    # Determine the mode based on switch 3
    in_transition_mode = not switch3_state  # Switch 3 closed means transition mode

    if in_transition_mode:
        # Transition Mode

        # Determine transition type from Switch 1
        if switch1_state:
            transition_type = 'fade'  # Switch 1 open
        else:
            transition_type = 'sequential'  # Switch 1 closed

        # Determine hold duration from Switch 2
        if switch2_state:
            hold_duration = 2  # Switch 2 open
        else:
            hold_duration = 10  # Switch 2 closed

        # Define transition colors
        transition_colors = [color_red, color_green, color_cyan, color_purple]

        for i in range(len(transition_colors)):
            color1 = transition_colors[i]
            color2 = transition_colors[(i + 1) % len(transition_colors)]

            if transition_type == 'fade':
                transition_colors_fade(color1, color2, 2, hold_duration)
            elif transition_type == 'sequential':
                transition_colors_sequential(color1, color2, 2, hold_duration)

            time.sleep(0.1)  # Small delay before the next transition

    else:
        # Color Mode
        if switch1_state and switch2_state:
            target_color = color_red  # Both switches open
        elif not switch1_state and not switch2_state:
            target_color = color_green  # Both switches closed
        elif switch1_state and not switch2_state:
            target_color = color_cyan  # Switch 1 open, switch 2 closed
        elif not switch1_state and switch2_state:
            target_color = color_purple  # Switch 1 closed, switch 2 open

        # Change to the target color if it's different
        if target_color != current_color:
            transition_colors_fade(current_color, target_color, 2, 0)
            current_color = target_color

    time.sleep(0.1)  # Small delay to debounce switch reads

