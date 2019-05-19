# Garage Door NodeServer

## Control one or two garage door openers with a Raspberry Pi.

### Installation

Please take the time to backup your ISY before installation just in case.
* Really, please do.

Install from the NodeServer Store or

Manual installation:

    cd .polyglot/nodeservers
    git clone https://github.com/markv58/UDI-Garage-Door-Pi.git
    cd UDI-Garage-Door-Pi
    chmod +x install.sh
    ./install.sh
    Add NodeServer in Polyglot

If you install maually, you will need to update with git pull after a git reset --hard.

This NodeServer will poll the status of the door at regular intervals and gives you Open, Close and Stop/Start control from the admin console and in your programs. The status of the door can be monitored to alert you when the door is opened or closed using a network resource or the <a target="_blank" href="https://github.com/markv58/UDI-Push">Push NodeServer.</a>

You can use either a single or dual sensor setup. The dual sensor setup will be more precise when determining the door position.

  This device can be a direct replacement for the io linc device on an Insteon 74551 setup using the existing wiring and sensor. An additional Open sensor can be added if you like. You will need to remove the IO Linc device from ISY and all programs and notifications will require updating to include the Garage Door NodeServer.
  
#### Requirements

* A Raspberry Pi 3 or better with Polyglot installed.
* Power supply.
* A magnetic reed switch like this <a target="_blank" href="https://www.amazon.com/gp/product/B00LYCUSBY/ref=ppx_yo_dt_b_asin_title_o01_s00?ie=UTF8&psc=1">here</a>.
* A relay switch like this <a target="_blank" href="https://www.amazon.com/SMAKN®-Active-Channel-Arduino-Raspberry/dp/B00VH8926C/ref=sr_1_5?">here</a>.
* 18 - 26 ga. twin wire.
* An enclosure. I used this one <a target="_blank" href="https://www.amazon.com/gp/product/B075X17M4T/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1">here</a>.
* A couple of strips of adhesive backed hook and loop or some stand offs to mount the Pi and relay.
* Raspberry pi female to female pin jumper wires.


#### Suggested mounting of the components

  ![Image of the enclosure](https://github.com/markv58/github.io/blob/master/First_enclosure.png) &nbsp ![Image of the second enclosure]
  
  The Pi, in the first pic, is mounted in the bottom half of a pi case and held in the enclosure with the adhesive backed hook and loop or the pi can be mounted to stand offs as in the second pic.
  
  Two small screws secure the relay into two mounts and I super glued a small platic stud to the enclosure to support the other side of the relay board. You can use stand offs as well.
  
  I carefully marked the location where the power cable would pass through on the outside and drilled a hole to accept the cable grommet.
  
  I used twin 18 ga. solid thermostat wire that fit nicely into the female jumpers for the connection to the reed switch. It was also used to connect the relay output to the door operator.
  
  The wire to the reed switch was run along the top of the rail under the existing wire clips. With the door closed the switch was fastened to the rail with the adhesive strip and the magnet was fixed to the trolley. Your setup may vary. For the dual sensor setup the door is then raised and the second reed switch is set in place.
  
  This device can be a direct replacement for the io linc device on an Insteon 74551 setup using the existing wiring and sensor. You will need to remove the device from ISY and all programs and notifications will require updating to include the Garage Door NodeServer.
  
  ![Trolley](https://github.com/markv58/github.io/blob/master/Trolley2.png)
  
  
  #### Wiring
  
  ![Wiring](https://github.com/markv58/github.io/blob/master/Wiring%20pic2.png)
  
  With the cover on, this device lives on top of the garage door opener.
