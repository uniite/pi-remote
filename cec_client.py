import os
from subprocess import Popen, PIPE

CEC_CLIENT_COMMAND = "cec-client -d 1 -o 'Raspberry Pi' RPI"


class CecClient(object):
	def __init__(self, inputs):
		self.inputs = inputs
		self.current_input = 0
		self.cec_client = Popen(CEC_CLIENT_COMMAND, stdin=PIPE, stdout=PIPE, shell=True)
		while True:
	 		line = self.cec_client.stdout.readline().strip()
			if line == 'waiting for input':
				break

	def _set_input(self, input_number, name=None):
		''' Changes to the HDMI input specfied by number (starting at 1) '''
		print 'Switching to input %s' % input_number
		# Change the HDMI port number of the CEC adapter
		self.send_command('p 0 %s' % input_number)
		# Make the CEC adapter the active source
		self.send_command('as')
		# Set the input name if specified
		if name:
			self.send_command('osd 0 %s' % name)

	def change_input(self, input_index=None):
		if input_index is not None:
			self.current_input = input_index
		else:
			self.current_input += 1
			if self.current_input >= len(self.inputs):
				self.current_input = 0
		selected = self.inputs[self.current_input]
		self._set_input(selected['addr'], selected['name'])

	def send_command(self, command):
		self.cec_client.stdin.write('%s\n' % command)


if __name__ == '__main__':
	client = CecClient()
	client.send_command('as')
