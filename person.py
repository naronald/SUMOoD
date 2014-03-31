# -*- coding: utf-8 -*-
"""
@file    person.py
@author  Nicole Ronald
@date    2014-03-17
@version 

Defines a person who requests a trip from the demand-responsive
transportation system.

SUMOoD (SUMO on Demand); see http://imod-au.info/sumood
Copyright (C) 2014 iMoD
SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2008-2012 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""


from network import Network, network

class PersonState:
    """ state of a person """
    UNALLOCATED = 0
    ALLOCATED = 1
    ONBOARD = 2
    ARRIVED = 3
    UNSUCCESSFUL = 4   


class Person:
    """ a person """
    personID = None
    callTime = None
    pickupTime = None
    dropoffTime =  None
    origin = None
    destination = None
    state = None

    directDistance = -1
    directTime = -1
    waitTime = ""
    travelTime = ""
    requestTime = None

    def __init__(self, personID):
        self.personID = personID
        self.state = PersonState.UNALLOCATED
        self.actualDistance = 0

    def __lt__(self, other):
        """ for sorting on callTime """
        return self.callTime < other.callTime

    def setCallTime(self, callTime):
        """ set call time
        (int)"""
        self.callTime = callTime

    def setRequestTime(self, requestTime):
        """ set request time
        (int)"""
        self.requestTime = requestTime

    def setPickupTime(self, time):
        """ set pickup time once picked up
        (int)"""
        self.pickupTime = time
        self.waitTime = time - self.callTime
        self.state = PersonState.ONBOARD
        self.firstLink = True

    def setDropoffTime(self, time):
        """ set dropoff time, once dropped off
        (int)"""
        self.dropoffTime = time
        self.travelTime = time - self.pickupTime
        self.state = PersonState.ARRIVED

    def setOD(self, origin, destination):
        """ set origin and destination stops
        (Stop, Stop)"""
        self.origin = origin
        self.destination = destination
        self.setDirectDistance() # calculate direct distance
        self.setDirectTime() # calculate direct time

    def getOrigin(self):
        """ return origin
        () -> Stop """
        return self.origin # Stop

    def getDestination(self):
        """ return destination 
        () -> Stop """
        return self.destination # Stop

    def getCallTime(self):
        """ return call time 
        () -> int"""
        return self.callTime

    def setDirectDistance(self):
        """ set direct distance based on network """
        self.directDistance = network.getDistance(self.origin,
                                                  self.destination)

    def setDirectTime(self):
        """ set direct time  based on network """
        self.directTime = network.getTime(self.origin, self.destination)

    def allocated(self):
        """ update self to allocated """
        self.state = PersonState.ALLOCATED

    def rejected(self):
        """ update self to unsuccessful """
        self.state = PersonState.UNSUCCESSFUL
        self.waitTime = ""
        self.travelTime = ""

    def incrementDistance(self, distance):
        """ add distance travelled
        (int)"""
        self.actualDistance += distance
        

    def estimatePenalty(self, dropoffTime):
        """ estimate penalty given an estimated dropoff time 
        (int) -> float """
        return (dropoffTime - self.callTime)/float(self.directTime)


    def getOutput(self):
        """ print details of a person """
        excessTime = ""
        excessDistance = ""
        excessTravelTime = ""
        if self.state == PersonState.ARRIVED:
            excessTime = (self.waitTime + self.travelTime) - self.directTime
            excessDistance = self.actualDistance - self.directDistance
            excessTravelTime = self.travelTime - self.directTime
        return [self.personID, self.callTime, self.requestTime,
                self.directDistance, self.actualDistance, self.directTime,
                self.waitTime, self.pickupTime, self.travelTime,
                self.dropoffTime, excessTravelTime, excessTime, excessDistance,
                self.state]
        
    def output(self):
        """ print details of a person """
        print self.personID + "," + str(self.directDistance) + "," + \
              str(self.directTime) + "," + str(self.waitTime) + "," + \
              str(self.travelTime) + "," + str(self.state)        
        
