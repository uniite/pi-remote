# pi-remote

Controls a TiVo via TCP and Speakers/TV via LIRC with a TiVo RF remote.

Just setup LIRC on your raspberry PI with the appropriate profile, and plug in a TiVo USB remote dongle, and it will translate the USB HID commands to TiVo and LIRC commands. The TiVo TCP protocol allows quick control over the network without any physical connection to the box (see `tivo_tcp_client.py`).


## Installation
```bash
# Switch to root
sudo -i

# Add users and groups for the USB receiver and our script
useradd pi-remote
groupadd tivo-usb
useradd -G tivo-usb pi-remote

# Install pi-remote to /opt
sudo -u pi-remote bash -c 'cd /tmp && git clone https://github.com/uniite/pi-remote.git'
mv /tmp/pi-remote /opt/pi-remote
chown -R pi-remote:pi-remote /opt/pi-remote

# Install a systemd service to run pi-remote at startup
cd /opt/pi-remote/config
cp /opt/pi-remote/config/pi-remote.service /lib/systemd/system/
chown root:root /lib/systemd/system/pi-remote.service

# Configure the IP/hostname of TiVo you want to control
echo TIVO_HOST=1.2.3.4 > /etc/sysconfig/pi-remote

# Configure udev to allow access to the TiVo USB remote dongle
cp /opt/pi-remote/config/udev.rules /etc/udev/rules.d/50-tivo-usb.rules

# Reboot
sudo reboot
```
