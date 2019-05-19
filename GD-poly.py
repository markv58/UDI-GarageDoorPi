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
        gpio.setwarnings(False)
        gpio.cleanup()
        gpio.setmode(gpio.BCM)
        self.d1_relay_pin = 23
        self.d1_state_pin_closed = 27
        self.d1_state_pin_open = 22
        self.d1_state = 5
        self.d1_last_state = 5
        self.d2_relay_pin = 24
        self.d2_state_pin_closed = 5
        self.d2_state_pin_open = 6
        self.d2_state = 5
        self.d2_last_state = 5
        gpio.setup(self.d1_relay_pin, gpio.OUT)
        gpio.setup(self.d1_state_pin_closed, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.setup(self.d1_state_pin_open, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.output(self.d1_relay_pin, True)
        gpio.setup(self.d2_relay_pin, gpio.OUT)
        gpio.setup(self.d2_state_pin_closed, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.setup(self.d2_state_pin_open, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.output(self.d2_relay_pin, True)
        self.travel_time = 15
        self.polling = True
        self.dualSensor = False
        self.pause_poll = False
        self.restart = True
        self.door2 = False
        self.send_d1 = True
        self.send_d2 = False
      
    def start(self):
        LOGGER.info('Starting Garage Door NodeServer v1.0.0')
        self.removeNoticesAll()
        self.check_params()
        self.setDriver('ST', 1)
        self.setDriver('GV1', 5)
        self.setDriver('GV2', 5)
        self.setDriver('GV3', 1)
        self.setDriver('GV4', 5)
        self.setDriver('GV5', 5)
        self.check_door2()
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
    
    def check_door2(self):
        if not self.door2:
            self.setDriver('GV2', 6)
            self.setDriver('GV5', 6)
            
    def toggle_relay(self, command):
        self.pause_poll = True
        if command == 1:
            gpio.output(self.d1_relay_pin, False)
            time.sleep(0.2)
            gpio.output(self.d1_relay_pin, True)
        if command == 2:
            gpio.output(self.d2_relay_pin, False)
            time.sleep(0.2)
            gpio.output(self.d2_relay_pin, True)

    def get_state(self):
        if self.dualSensor:
            _d1valClosed = gpio.input(self.d1_state_pin_closed)
            _d1valOpen = gpio.input(self.d1_state_pin_open)
            if _d1valClosed == 0 and _d1valOpen == 1:
                self.setDriver('GV1', 0)
                self.d1_state = 0 #closed
            elif _d1valOpen == 0 and _d1valClosed == 1:
                self.setDriver('GV1', 3)
                self.d1_state = 3 #open
            elif _d1valClosed == 1 and _d1valOpen == 1 and self.d1_state != 4:
                if self.d1_last_state == 1:
                    self.setDriver('GV1', 2)
                elif self.d1_last_state == 2:
                    self.setDriver('GV1', 1)
                else:
                    self.setDriver('GV1', 4)
                    self.d1_state = 4
            if self.door2:
                _d2valClosed = gpio.input(self.d2_state_pin_closed)
                _d2valOpen = gpio.input(self.d2_state_pin_open)
                if _d2valClosed == 0 and _d2valOpen == 1:
                    self.setDriver('GV2', 0)
                    self.d2_state = 0 #closed
                elif _d2valOpen == 0 and _d2valClosed == 1:
                    self.setDriver('GV2', 3)
                    self.state = 3 #open
                elif _d2valClosed == 1 and _d2valOpen == 1 and self.d2_state != 4:
                    if self.d2_last_state == 1:
                        self.setDriver('GV2', 2)
                    elif self.d2_last_state == 2:
                        self.setDriver('GV2', 1)
                    else:
                        self.setDriver('GV2', 4)
                        self.d2_state = 4
            else:
                self.setDriver('GV2', 6)
            self.pause_poll = False
        else:
            _valClosed = gpio.input(self.d1_state_pin_closed)
            if _valClosed == 0:
                self.setDriver('GV1', 0)
                self.d1_state = 0 #closed
            else:   
                self.setDriver('GV1', 3)
                self.d1_state = 3
            self.pause_poll = False
                
    def StopStartDoor(self, command):
        if command == 1:
            _currentState = int(self.d1_state)
            _lastState = self.d1_last_state
        else:
            _currentState = int(self.d2_state)
            _lastState = self.d2_last_state
            
        if _currentState == 4 and self.restart: # This will allow a relay toggle if the nodeserver is restarted
            self.restart = False                # while the door is in the midway position and update the status.
            LOGGER.info('Toggling the garage door button.')
            self.pollTimer(command, 5)
        if _currentState == 4: # If the door is partially open.
            #_state = self.d1_last_state
            if _lastState == 1: #opening
                if command == 1:
                    self.d1_last_state = 2 # set to closing
                    self.setDriver('GV4', 4)
                    self.setDriver('GV1', 2)
                    self.d1_state = 3
                elif command == 2:
                    self.d2_last_state = 2 # set to closing
                    self.setDriver('GV5', 4)
                    self.setDriver('GV2', 2)
                    self.d2_state = 3
                self.toggle_relay(command)
            if _lastState == 2: #closing
                if command == 1:
                    self.d1_last_state = 1 # set to opening
                    self.setDriver('GV4', 4)
                    self.setDriver('GV1', 1)
                    self.d1_state = 0
                elif command == 2:
                    self.d1_last_state = 1 # set to opening
                    self.setDriver('GV1', 4)
                    self.setDriver('GV5', 1)
                    self.d1_state = 0
                self.toggle_relay(command)   
        if _currentState == 1:
            LOGGER.info('Stopping the garage door.')
            self.toggle_relay(command)
            if command == 1:
                self.d1_last_state = 1
                self.setDriver('GV4', 1)
                self.d1_state = 4
                self.setDriver('GV1', 4)
            elif command == 2:
                self.d2_last_state = 1
                self.setDriver('GV5', 1)
                self.d2_state = 4
                self.setDriver('GV2', 4)
        if _currentState == 2:
            LOGGER.info('Stopping the garage door.')
            self.toggle_relay(command)  
            if command == 1:
                self.d1_last_state = 2
                self.setDriver('GV4', 2)
                self.d1_state = 4
                self.setDriver('GV1', 4)
            elif command == 2:
                self.d2_last_state = 2
                self.setDriver('GV5', 2)
                self.d2_state = 4
                self.setDriver('GV2', 4)
    # There has to be an easier way to do all these things. Well I will just have to dig into this code and finger it out!            
   
    def openDoor(self, command):
        _door = command
        if self.d1_state == 0 or self.d2_state == 0: #closed
            if _door == 1:
                self.d1_last_state = 1
                self.setDriver('GV4', 0)
            if _door == 2:
                self.d2_last_state = 1
                self.setDriver('GV5', 0)
            self.pollTimer(_door, 1)
            LOGGER.debug('Opening the garage door')
            
    def closeDoor(self, command):
        if self.d1_state == 3 or self.d2_state == 3:
            if command == 1:
                self.d1_last_state = 2
                self.setDriver('GV4', 3)
            if command == 2:
                self.d2_last_state = 2
                self.setDriver('GV5', 3)
            self.pollTimer(command, 2)
            LOGGER.debug('Closing the garage door')    
            
    def pollTimer(self, door, command):
        self.toggle_relay(door)
        if door == 1:
            self.d1_state = command
            self.setDriver('GV1', command)
        if door == 2:
            self.d2_state = command
            self.setDriver('GV2', command)
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
            _val = str(self.polyConfig['customParams']['short_poll'])
            _vallower = _val.lower()
            if _vallower == 'true':
                self.polling = True
            if _vallower == 'false':
                self.polling = False
        LOGGER.info('The short poll is set to %s', str(self.polling))  
        
        if 'dual_sensor' in self.polyConfig['customParams']:
            _val = str(self.polyConfig['customParams']['dual_sensor'])
            _vallower = _val.lower()
            if _vallower == 'true':
                self.dualSensor = True
            if _vallower == 'false':
                self.dualSensor = False
        LOGGER.info('Dual sensor is set to %s', str(self.dualSensor))      
        
        if 'two_doors' in self.polyConfig['customParams']:
            _val = str(self.polyConfig['customParams']['two_doors'])
            _vallower = _val.lower()
            if _vallower == 'true':
                self.door2 = True
            if _vallower == 'false':
                self.door2 = False
        LOGGER.info('Two doors is set to %s', str(self.door2))  
        
        if 'travel_time' in self.polyConfig['customParams']:
            self.travel_time = self.polyConfig['customParams']['travel_time']
        LOGGER.info('The door travel time is set to %s seconds.', str(self.travel_time))
        
        self.addCustomParam({'short_poll': self.polling, 'travel_time': self.travel_time, 'dual_sensor': self.dualSensor, 'two_doors': self.door2})
        
    def open_1(self, command):
        self.openDoor(1)
        
    def open_2(self, command):
        if self.door2:
            self.openDoor(2)
        else:
            pass
        
    def close_1(self, command):
        self.closeDoor(1)
        
    def close_2(self, command):
        if self.door2:
            self.closeDoor(2)
        else:
            pass
        
    def ss_1(self, command):
        self.StopStartDoor(1)
        
    def ss_2(self, command):
        if self.door2:
            self.StopStartDoor(2)
        else:
            pass
        
    def remove_notices_all(self,command):
        LOGGER.info('remove_notices_all:')
        # Remove all existing notices
        self.removeNoticesAll()

    def update_profile(self, command = None):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    drivers = [
               {'driver': 'ST', 'value': 1, 'uom': 2},
               {'driver': 'GV1', 'value': 0, 'uom': 25},
               {'driver': 'GV2', 'value': 0, 'uom': 25},
               {'driver': 'GV3', 'value': 0, 'uom': 56},
               {'driver': 'GV4', 'value': 0, 'uom': 25},
               {'driver': 'GV5', 'value': 0, 'uom': 25}
              ]

    id = 'controller'

    commands = {
                'OPEN_DOOR_1': open_1,
                'STOP_DOOR_1': ss_1,
                'CLOSE_DOOR_1': close_1,
                'OPEN_DOOR_2': open_2,
                'STOP_DOOR_2': ss_2,
                'CLOSE_DOOR_2': close_2,
                'UPDATE_PROFILE': update_profile
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
