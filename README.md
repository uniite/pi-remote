# pi-remote

Controls a TiVo via TCP and Speakers/TV via LIRC with a TiVo RF remote.

Just setup LIRC on your raspberry PI with the appropriate profile, and plug in a TiVo USB remote dongle, and it will translate the USB HID commands to TiVo and LIRC commands. The TiVo TCP protocol allows quick control over the network without any physical connection to the box (see `tivo_tcp_client.py`).


