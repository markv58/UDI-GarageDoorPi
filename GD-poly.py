#!/usr/bin/env python3

#Garage Door Opener Controller

import polyinterface
import sys
import time
import RPi.GPIO as gpio
import threading

LOGGER = polyinterface.LOGGER

class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Garage Door'
        gpio.setmode(gpio.BCM)
        self.relay_pin = 23
        self.state_pin_closed = 27
        self.state_pin_open = 22
        self.state = 5
        gpio.setup(self.relay_pin, gpio.OUT)
        gpio.setup(self.state_pin_closed, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.setup(self.state_pin_open, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.output(self.relay_pin, True)
        self.travel_time = 15
        self.polling = True
        self.last_state = 5
        self.pause_poll = False
        self.restart = True
        
    def start(self):
        LOGGER.info('Starting Garage Door NodeServer v1.0.0')
        self.removeNoticesAll()
        self.check_params()
        self.setDriver('ST', 1)
        time.sleep(.5)
        self.setDriver('GV1', 5)
        time.sleep(1)
        self.get_state()
        
    def shortPoll(self):
        if self.polling and not self.pause_poll:
            self.get_state()
        else:
            pass
    
    def longPoll(self):
        pass

    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        pass

    def toggle_relay(self, command = None):
        self.pause_poll = True
        #LOGGER.debug('toggle')
        gpio.output(self.relay_pin, False)
        time.sleep(0.2)
        gpio.output(self.relay_pin, True)

    def get_state(self):
        #LOGGER.debug('getting door status')
        _valClosed = gpio.input(self.state_pin_closed)
        _valOpen = gpio.input(self.state_pin_open)
        if _valClosed == 0 and _valOpen == 1:
            self.setDriver('GV1', 0)
            self.state = 0 #closed
        elif _valOpen == 0 and _valClosed == 1:
            self.setDriver('GV1', 3)
            self.state = 3 #open
        elif _valClosed == 1 and _valOpen == 1:
            self.setDriver('GV1', 4)
            self.state = 4
        self.pause_poll = False
        
    def StopStartDoor(self, command):
        _currentState = int(self.state)
        if _currentState == 4 and self.restart: # This will allow a relay toggle if the nodeserver is restarted
            self.restart = False                # while the door is in the midway position and update the status.
            LOGGER.info('Toggling the garage door button.')
            self.pollTimer(5)
        if _currentState == 4: # If the door is partially open.
            _state = self.last_state
            if _state == 1: #opening
                self.last_state = 2 # set to closing
                self.setDriver('GV1', 2)
                self.state = 3
                self.closeDoor()
            if _state == 2: #closing
                self.last_state = 1 # set to opening
                self.setDriver('GV1', 1)
                self.state = 0
                self.openDoor()
                
        if _currentState == 1:
            LOGGER.info('Stopping the garage door.')
            self.toggle_relay()
            self.last_state = 1
            self.state = 4
            self.setDriver('GV1', 4)
            
        if _currentState == 2:
            LOGGER.info('Stopping the garage door.')
            self.toggle_relay()  
            self.last_state = 2
            self.state = 4
            self.setDriver('GV1', 4)
    
    def openDoor(self, command = None):
        if self.state == 0: #closed
            self.last_state = 1
            self.pollTimer(1)
            LOGGER.debug('Opening the garage door')
            
    def closeDoor(self, command = None):
        if self.state == 3:
            self.last_state = 2
            self.pollTimer(2)
            LOGGER.debug('Closing the garage door')    
            
    def pollTimer(self, command):
        self.toggle_relay()
        self.state = command
        self.setDriver('GV1', command)
        t = int(self.travel_time)
        timer_thread = threading.Timer(t, self.get_state)
        timer_thread.daemon = True
        timer_thread.start()
            
    def delete(self):
        LOGGER.info('Deleting Garage Door NodeServer.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def check_params(self):
        LOGGER.debug('Checking for custom configuration parameters.')
        
        if 'short_poll' in self.polyConfig['customParams']:
            _val = self.polyConfig['customParams']['short_poll']
            _vallower = _val.lower()
            if _vallower == 'true':
                self.polling = True
            if _vallower == 'false':
                self.polling = False
        LOGGER.info('The short poll is set to %s', str(self.polling))   
        
        if 'travel_time' in self.polyConfig['customParams']:
            self.travel_time = self.polyConfig['customParams']['travel_time']
        LOGGER.info('The door travel time is set to %s seconds.', str(self.travel_time))
    
    def remove_notices_all(self,command):
        LOGGER.info('remove_notices_all:')
        # Remove all existing notices
        self.removeNoticesAll()

    def update_profile(self, command = None):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    drivers = [{'driver': 'ST', 'value': 1, 'uom': 2},
               {'driver': 'GV1', 'value': 0, 'uom': 25}
              ]

    id = 'controller'

    commands = {
                'OPEN_DOOR': openDoor,
                'STOP_DOOR': StopStartDoor,
                'CLOSE_DOOR': closeDoor,
                'UPDATE_PROFILE': update_profile,
                'REMOVE_NOTICES_ALL': remove_notices_all
               }



if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('GDNodeServer')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        polyglot.stop()
        sys.exit(0)
