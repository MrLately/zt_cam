zt_cam

zt_cam is a Flask web application that provides essential information for ZeroTier networking and the connection between a Raspberry Pi and a control device. It offers the following features:

Check the ZeroTier connection status (direct or relayed).
Retrieve signal strength from a Huawei modem connected to the Raspberry Pi (tested with e3372h, e8372h, and a knockoff e3372h-510).
Measure latency between the Raspberry Pi and a designated control device on the same ZeroTier network.
Dependencies
Make sure to install these dependencies before using zt_cam:

Flask: pip install Flask

picamera: pip install picamera

requests: pip install requests

Configuration for latency feature.
Open app.py.
Find the target_ip variable.

![zt](https://github.com/MrLately/zt_cam/assets/94589563/f163d3de-6ac8-41b6-8522-548695f4905c)

Replace the IP address inside the quotes with your control device's ZeroTier-assigned IP address.

Access the application in your browser by entering the Raspberry Pi's ZeroTier-assigned IP address and port (default: http://RASPBERRY_PI_IP:6789).
