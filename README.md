# LiesteriaDetect

For setup on the raspberry pi, there needs to be added a line to the configuration file and a new service file

# Liesteria Detect Application Software Deployment Guide

This guide details the steps required to configure the operating system and deploy the **Liesteria Detect Application** as a persistent service on a Raspberry Pi running Raspberry Pi OS.

***

## 1. ⚙️ System Configuration: Enabling Safe Shutdown

The graceful shutdown feature is enabled via a **Device Tree Overlay** in the system configuration file. This allows the operating system to detect the button press and initiate a clean shutdown sequence, which sends the `SIGTERM` signal to your application.

### 1.1. Edit Configuration File

The active configuration file is located at `/boot/firmware/config.txt`.

1.  Open the file with `sudo nano`:
    ```bash
    sudo nano /boot/firmware/config.txt
    ```

2.  Add the following configuration line to the **end** of the file:
    ```ini
    dtoverlay=gpio-shutdown,gpio_pin=6,active_low=1,gpio_pull=up,debounce=500
    ```
    > 💡 **Configuration Details:** This line tells the kernel to monitor **GPIO 6** and trigger a shutdown if the pin is held low for **500 milliseconds**.

3.  Save the file (**CTRL+X**, then **Y**, then **ENTER**).

4.  **Reboot** the Pi to apply the kernel change:
    ```bash
    sudo reboot
    ```

***

## 2. 🖥️ Application Deployment: `systemd` Service Setup

The application must be run as a `systemd` service. This ensures it **starts automatically** when the Pi boots and responds correctly to the graceful shutdown signal (`SIGTERM`) initiated by the OS.

### 2.1. Create Service File

Create the service unit file at `/etc/systemd/system/liesteria_detect.service`:

```bash
sudo nano /etc/systemd/system/liesteria_detect.service
```

Paste the following content into the file:

```ini
[Unit]
Description=Liesteria Detect Application
# Network dependency is intentionally omitted for faster startup, as the application is local.

[Service]
# NOTE: Adjust 'User' if your main user is not 'pi'
User=pi
# The full path to the Python script
ExecStart=/usr/bin/python3 /home/pi/LiesteriaDetect/main.py
# If the script exits unexpectedly, systemd will automatically restart it
Restart=always
# Set the working directory for file operations (e.g., accessing the SQLite DB)
WorkingDirectory=/home/pi/LiesteriaDetect
StandardOutput=journal

[Install]
# Enable the service to run on multi-user boot
WantedBy=multi-user.target
```
### 2.2. Activate the Service

Run these commands in the terminal to register, enable, and start the service:

Reload the daemon to read the new service file:

```bash
sudo systemctl daemon-reload
```
Enable the service to start automatically on every boot:

```bash
sudo systemctl enable liesteria_detect.service
```
Start the service immediately:

```bash
sudo systemctl start liesteria_detect.service
```

### 2.3. Verification

Check Status: Ensure the service is running successfully:

```bash
sudo systemctl status liesteria_detect.service
```
View Logs: Watch the application's real-time output (your print() statements) using the system journal (use CTRL+C to exit the view):

```bash
sudo journalctl -u liesteria_detect.service -f
```