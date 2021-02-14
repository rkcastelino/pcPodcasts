# Have to test linux

# If linux:
# import tty
# import sys
# import termios
#
# orig_settings = termios.tcgetattr(sys.stdin)
#
# tty.setcbreak(sys.stdin)
# x = 0
# while x != chr(27): # ESC
#     x=sys.stdin.read(1)[0]
#     print("You pressed", x)
#
# termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)



# If windows:
import keyboard  # using module keyboard
while True:  # making a loop
    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('q'):  # if key 'q' is pressed
            print('You Pressed A Key!')
            break  # finishing the loop
    except:
        break  # if user pressed a key other than the given key the loop will break
