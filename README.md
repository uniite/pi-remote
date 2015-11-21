# pi-remote

Controls a TiVo via TCP and Speakers/TV via LIRC with a TiVo RF remote.

Just setup LIRC on your raspberry PI with the appropriate profile, and plug in a TiVo USB remote dongle, and it will translate the USB HID commands to TiVo and LIRC commands. The TiVo TCP protocol allows quick control over the network without any physical connection to the box (see `tivo_tcp_client.py`).


## Installation

As root (`sudo -i`):
```bash
# Add users and groups for the USB receiver and our script
useradd pi-remote
groupadd tivo-usb
useradd -G tivo-usb pi-remote

# Install pi-remote to /opt
mkdir -p /opt/pi-remote
chown pi-remote /opt/pi-remote
```

As pi-remote user (`sudo -iu pi-remote`)
```bash
cd /opt/pi-remote
git clone https://github.com/uniite/pi-remote.git src
mv src/* src/.git .
rm -r src
```

As root:
```bash
# Install init/upstart job to run pi-remote at startup
sudo cp /opt/pi-remote/config/upstart.conf /etc/init/pi-remote.conf
sudo chown root:root /etc/init/pi-remote.conf
sudo cp /opt/pi-remote/config/udev.rules /etc/udev/rules.d/50-tivo-usb.rules
```

Reboot (`sudo reboot`)
