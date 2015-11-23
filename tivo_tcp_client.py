import os
import socket

TIVO_HOST = os.environ.get('TIVO_HOST')
TIVO_PORT = 31339


class TivoClient(object):
    def __init__(self, host=TIVO_HOST, port=TIVO_PORT):
        self.host = host
        self.port = port

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def send_command(self, command):
        self.socket.send('%s\r\n' % command)

    def send_ircode(self, ircode):
        self.send_command('IRCODE %s' % ircode)

    def close(self):
        self.socket.close()


if __name__ == '__main__':
    tivo = TivoClient()
    tivo.connect()
    tivo.send_ircode('TIVO')
    print 'Ready.'
    while True:
        command = raw_input('Command: ')
        if command == 'q':
            break
        else:
            tivo.send_ircode(command)
    tivo.close()
