Log Visualizer
==============

Visualizes some LevelUp logs using LEDs

Debian
------

```
apt install mosquitto
pip install -r requirements.txt
```

Usage
-----

This comes in two pieces which connect together via MQTT: the order event
source, which pulls from Logentries and the animator which takes the orders
and visualizes them using a pattern.

### Source

`logentries_mqtt.py`

### Animator

`textvis.py`

a sample visualization

`gridvis.py`

The main LED visualizer

