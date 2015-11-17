#import gevent
import os
from subprocess import Popen, PIPE
from tivo_tcp_client import TivoClient

USBHID_DUMP_CMD = 'usbhid-dump --entity=stream --model=150a:1203 --stream-timeout=0'

'''
Example stream from keypress:

001:005:000:STREAM             1447637897.846846
 10 42 00

001:005:000:STREAM             1447637897.982649
 10 00 00

'''

# All these are prefixed with 0x10 and suffixed with 0x00
# in the raw HID dump stream (eg. UP would be '10 42 00')
# The key up/release code is then '10 00 00'
CUSTOM_PREFIX = 'Custom - '
NORMAL_PREFIX = 0x10
NORMAL_SUFFIX = 0x00
NORMAL_PRESS_SIZE = 3
NORMAL_BUTTONS = {
    0x41: 'SELECT',
    0x42: 'UP',
    0x43: 'DOWN',
    0x44: 'LEFT',
    0x45: 'RIGHT',

    0x8D: 'GUIDE',
    # Technically Info is '10 09 02', but there is no '10 09 00' to conflict with
    0x09: 'INFO',
    # Not documented on the TiVo protocol, but it seems to work
    0x46: 'BACK',

    # I'm mapping "Zoom" on the remote to exit because there is not "EXIT" command
    0x6D: 'EXIT',

    0x9C: 'CHANNELUP',
    0x9D: 'CHANNELDOWN',

    0xE9: 'Custom - VOLUMEUP',
    0xEA: 'Custom - VOLUMEDOWN',
    0xE2: 'Custom - MUTE',
    0x30: 'Custom - TVPOWER',
    0x82: 'Custom - TVINPUT',

    0xB0: 'PLAY',
    0xB1: 'PAUSE',
    0xB2: 'RECORD',
    0xB3: 'FORWARD',
    0xB4: 'REVERSE',
    0xB5: 'ADVANCE',
    0xB6: 'REPLAY',
    0xF5: 'SLOW',

    0x83: 'ENTER',

    0x6C: 'ACTION_A',
    0x6B: 'ACTION_B',
    0x69: 'ACTION_C',
    0x6A: 'ACTION_D'
}

# Special buttons that are similar to above,
# but prefixed with 0x11
SPECIAL_PREFIX = 0x11
SPECIAL_BUTTONS = {
    0x3D: 'TIVO',
    0x3E: 'LIVETV',
    0x41: 'THUMBSDOWN',
    0x42: 'THUMBSUP'
}
# Weird Note:
# When you release the TIVO button it sends an additional 3 codes:
#   13 14
#   FC 03 01
#   FC 04 84

# All of these follow this pattern:
#   Press: '01 00 00 <key code> 00 00 00 00 00'
#   Release: '01 00 00 00 00 00 00 00 00'
NUMBER_PRESS_PATTERN = [1, 0, 0, None, 0, 0, 0, 0, 0]
NUMBER_PRESS_INDEX = 3
NUMBER_PRESS_SIZE = len(NUMBER_PRESS_PATTERN)
NUMBER_RELEASE = [1, 0, 0, 0, 0, 0, 0, 0, 0]
NUMBER_BUTTONS = {
  0x1E: 'NUM1',
  0x1F: 'NUM2',
  0x20: 'NUM3',
  0x21: 'NUM4',
  0x22: 'NUM5',
  0x23: 'NUM6',
  0x24: 'NUM7',
  0x25: 'NUM8',
  0x26: 'NUM9',
  0x27: 'NUM0',
  0xD8: 'CLEAR'
}


def process_keypress(key_codes):
    command = None

    ## Determine the keypress type by the key code, and parse appropriately
    # Numer pad
    if len(key_codes) == NUMBER_PRESS_SIZE:
        key = key_codes[NUMBER_PRESS_INDEX]
        key_codes[NUMBER_PRESS_INDEX] = None
        if key_codes == NUMBER_PRESS_PATTERN:
            command = NUMBER_BUTTONS.get(key)
    # Other
    elif len(key_codes) == NORMAL_PRESS_SIZE:
        prefix, key, _ = key_codes
        if prefix == NORMAL_PREFIX:
            command = NORMAL_BUTTONS.get(key)
        elif prefix == SPECIAL_PREFIX:
            command = SPECIAL_BUTTONS.get(key)

    return command

def parse_keypress(line):
    ''' Prase the given dump line of hex codes into an array of integers '''
    return [int(x, 16) for x in line.split()]

def lirc_irsend(command):
    print 'LIRC %s' % command
    os.system('irsend SEND_ONCE %s' % command)

def speaker_send(command):
    lirc_irsend('logitech_z5500 %s' % command)

def process_hid_events():
    client = TivoClient()
    client.connect()
    usbhid_dump = Popen(USBHID_DUMP_CMD, stdout=PIPE, shell=True)
    state = None
    while True:
        line = usbhid_dump.stdout.readline()
        # This line should contain a....
        if state == 'keypress':
            key_codes = parse_keypress(line)
            command = process_keypress(key_codes)
            print command
            # These are commands that are meant for controlling other devices
            # (normally by programming the buttons with different IR codes)
            if command and command.startswith(CUSTOM_PREFIX):
                command = command.replace(CUSTOM_PREFIX, '')
                # We can forward these to our IR-controlled speakers via LIRC
                TIVO_TO_SPEAKER_MAPPING = {
                    'TVPOWER': 'KEY_POWER',
                    'VOLUMEDOWN': 'KEY_VOLUMEDOWN',
                    'VOLUMEUP': 'KEY_VOLUMEUP',
                    'MUTE': 'KEY_MUTE',
                }
                speaker_cmd = TIVO_TO_SPEAKER_MAPPING.get(command)
                if speaker_cmd:
                    speaker_send(speaker_cmd)
            # Regular TV commnads get sent straight to the TiVo
            else:
                client.send_ircode(command)
            state = None
        # Looking for markers to indicate a switch to a new state
        else:
            # If we find a stream marker, the next line must contain the key press
            if ':STREAM' in line:
                state = 'keypress'


if __name__ == '__main__':
    process_hid_events()
