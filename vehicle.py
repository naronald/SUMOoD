# -*- coding: utf-8 -*-
"""
@file    vehicle.py
@author  Nicole Ronald
@date    2014-03-17
@version 

Defines vehicles and their properties.

SUMOoD (SUMO on Demand); see http://imod-au.info/sumood
Copyright (C) 2014 iMoD
SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2008-2012 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""


import subprocess, random, sys, os
SUMO_HOME = os.path.realpath(
    os.environ.get("SUMO_HOME",
                   os.path.join(os.path.dirname(__file__),
                                "..", "..", "..", "..")))
sys.path.append(os.path.join(SUMO_HOME, "tools"))

import traci
import traci.constants as tc
from stop import Stop, StopType
from peopleCollection import PeopleCollection, peopleCollection
from network import network, Network
import csv

DWELLTIME = 2000
MILLISECONDS = 1000
M2KM = 1000
LARGEDIST = 1000000
INFPENALTY = 1000000
STOP_OFFSET = 20.0
PARK_OFFSET = 60.0

class VehicleState:
    """ state of the vehicle """
    vsNotStarted = 1
    vsRunning = 2
    vsStopped = 3
    vsGoingHome = 4


class VehicleStatus:
    """ status of vehicle, was used when taxi """
    VACANT = 0
    BOOKED = 1
    ENGAGED = 2
    PARKED = 3


class Vehicle:
    """ a vehicle """
    num = 0


    def __init__(self, name):
        self.name = name
        self.plan = []
        self.operatingState = VehicleState.vsNotStarted
        self.currentStatus = VehicleStatus.PARKED
        currentLink = str(traci.vehicle.getRoadID(self.name))
        self.lastLink = currentLink
        currentPos = float(traci.vehicle.getLanePosition(self.name))
        self.lastPos = currentPos
        self.visited = []
        self.visited.append(Stop(-1, currentLink, currentPos, StopType.DEPOT))
        self.totalPassengers = 0
        self.totalDistance = 0
        self.nextUpdate = None
        self.itineraryPenalty = 0
        self.countPassengers = 0
        self.capacity = 10
        self.currentPassengers = []
        self.end = 3660
        self.parkedLink = currentLink
        self.parkedPos = currentPos
        self.occupancyTime = 0
        depotStop = Stop(-1, "out", 0, StopType.DEPOT, self.end)
        traci.vehicle.setStop(self.name, currentLink, currentPos, 0,
                              self.end*MILLISECONDS)
        self.plan.append(depotStop)
        self.actualEnd = self.end
        self.shared = 0
        self.deadheading = 0
        self.i = Vehicle.num
        Vehicle.num += 1

    def getState(self):
        return self.operatingState


    def changeTarget(self, link):
        """ change current route to aim for a new target
        (Stop)"""
        traci.vehicle.changeTarget(self.name, link)
        self.nextUpdate = link

    def addStop(self, link, pos):
        """ add a stop, dwell time currently 5s
        (string, float) """
        traci.vehicle.setStop(self.name, link, pos, 0, DWELLTIME)

    def stop(self, step):
        """ stop vehicle once it leaves simulation
        i.e., no longer available """
        self.operatingStatus = VehicleState.vsStopped
        self.actualEnd =  step


    def addPerson(self, person, puPosition, doPosition, penalty):
        """ add a person to a vehicle's plan, insert stops at specified places
        (Person, int, int, float)"""

        # extract details from person
        personID = person.personID
        link1 = person.getOrigin().link
        pos1 = person.getOrigin().pos
        request = person.getOrigin().serviceTime
        link2 = person.getDestination().link
        pos2 = person.getDestination().pos

        # add stops to plan 
        self.plan.insert(puPosition, Stop(personID, link1, pos1,
                                          StopType.PICKUP, request))
        self.plan.insert(doPosition, Stop(personID, link2, pos2,
                                          StopType.DROPOFF))
        print "Person " + str(personID) + " now waiting at " + link1 + "," + \
              str(pos1) + " going to " + link2 + "," + str(pos2) + \
              " waiting for " + self.name

        print self.name, "plan:"
        for i in range(0, len(self.plan)):
            self.plan[i].printLn()

        # set person to allocated
        person.allocated()

        # reroute vehicle as plan is updated
        self.currentLink = network.getVehicleCurrentEdge(self.name)
        self.currentPos = network.getVehicleCurrentPosition(self.name)
        if self.currentStatus == VehicleStatus.PARKED:
            self.currentStatus = VehicleStatus.BOOKED
            if self.operatingState != VehicleState.vsRunning:
                # raise from parking position at depot
                print self.parkedLink, self.parkedPos
                traci.vehicle.setStop(self.name, self.parkedLink,
                                      self.parkedPos, 0, 0)
            else:
                # raise from parking position
                traci.vehicle.setStop(self.name, self.parkedLink,
                                      self.parkedPos, 0, 0) 
        myNextStop = self.plan[0]
        traci.vehicle.changeTarget(self.name, myNextStop.link)
        traci.vehicle.setStop(self.name, myNextStop.link, myNextStop.pos, 0,
                              DWELLTIME)
        print self.name, " heading for ", myNextStop.personID, " at", \
              myNextStop.link, myNextStop.pos

        self.operatingState = VehicleState.vsRunning


    def getCurrentPos(self):     
        """ return current position """

        if self.currentStatus != VehicleStatus.PARKED:
            currentLink = network.getVehicleCurrentEdge(self.name)
            currentPos = network.getVehicleCurrentPosition(self.name)
        else:
            currentLink = self.lastLink
            currentPos = self.lastPos

        currentStop = Stop(-1, currentLink, currentPos, StopType.CURRENT)
        return currentStop # Stop
        

    def calcTentativeItineraryPenalty(self, puLink, doLink, step):
        """ calculate penalty for tentative passenger by iterating through
        possibilities
        (int, int, int)"""
        currentPlan = list(self.plan)
        offset = 1
        # insert current position at start
        currentPlan.insert(0,self.getCurrentPos()) 
        
        bestPickupPosition = None
        bestDropoffPosition = None
        minPenalty = INFPENALTY

        penalty = 0

        for c in currentPlan:
            print self.name, c.link, c.pos, c.stopType

        # need (len(currentPlan) + 1) so stop could be added at end,
        # removed as DEPOT now at end
        # start with pickup stop
        for puIteration in range(offset, len(currentPlan)):
            currentPlan.insert(puIteration, puLink)
            # dropoff stop can be any position after the pickup
            for doIteration in range(puIteration + 1, len(currentPlan)):
                currentPlan.insert(doIteration, doLink)
                penalty = self.calcItineraryPenalty(currentPlan, step)
                if penalty < minPenalty:
                    bestPickupPosition = puIteration
                    bestDropoffPosition = doIteration
                    minPenalty = penalty  
                currentPlan.pop(doIteration)
            currentPlan.pop(puIteration)

        if minPenalty < INFPENALTY:
            # -offset due to adding the current position 
            return (bestPickupPosition - offset, bestDropoffPosition - offset, minPenalty)
        else:
            return (None, None, INFPENALTY)

    def calcCurrentItineraryPenalty(self, step):
        """ calculate penalty for tentative passenger by iterating through
        possibilities
        (int, int, int)"""
        currentPlan = list(self.plan)
        offset = 1
        # if already servicing an action, add that back in
        if self.nextUpdate != None: 
            currentPlan.insert(0, self.nextUpdate)
            offset += 1
        # insert current position at start
        currentPlan.insert(0,self.getCurrentPos()) 
        return self.calcItineraryPenalty(currentPlan, step)                

    def calcItineraryPenalty(self, plan, step):
        """ calculates penalty for a particular plan, at a particular time step  
        (Stop[], int)"""
        penalty = 0
        nPassengers = self.countPassengers
        currentPassengers = list(self.currentPassengers)
        runningTime = step

        for i in range(0, len(plan)-1):
            o = plan[i]
            d = plan[i+1]
            timeLapse = network.getTime(o,d)
            runningTime += int(timeLapse)
            # too early
            if d.serviceTime != None and runningTime < d.serviceTime: 
                runningTime = d.serviceTime
            # running overtime
            if runningTime > self.end:
                return INFPENALTY
            # if pickup, update passengers
            if d.stopType == StopType.PICKUP:
                nPassengers += 1
                currentPassengers.append(d.personID)
            # if dropoff, determine penalty to that passenger given dropoff
            # time
            elif d.stopType == StopType.DROPOFF:
                nPassengers -= 1
                currentPassengers.remove(d.personID)
                penalty += peopleCollection.estimatePenalty(d.personID,
                                                            runningTime)
            # if over capacity, return infinity
            if nPassengers > self.capacity:
                return INFPENALTY
        return penalty

    def getItineraryPenalty(self):
        """ return itinerary penalty for current plan 
        () -> float"""
        return self.itineraryPenalty # float
        

    def newRouteStop(self, stop):
        """ reroute vehicle 
        (Stop)"""
        traci.vehicle.changeTarget(self.name, stop.link)
        traci.vehicle.setStop(self.name, stop.link, stop.pos, 0, DWELLTIME)
        self.nextUpdate = stop
        self.currentStatus = VehicleStatus.BOOKED

    def getNextStop(self, delete=False):
        """ return next stop in plan, None if plan empty;
        if delete = true, delete stop from plan
        (bool) -> Stop"""
        if delete:
            self.plan.pop(0)
        if len(self.plan) > 0:
            return self.plan[0]
        else:
            return None

    def update(self, step):
        """ update plan at a time step 
        (int)"""
        global peopleCollection

        # determine current position
        self.currentLink = network.getVehicleCurrentEdge(self.name)
        self.currentPos = network.getVehicleCurrentPosition(self.name)

        # distance travelled
        if self.lastLink != None: # has started moving
            # if has moved since last update, ignore if vehicle parked
            if not(self.lastLink == self.currentLink and \
                   self.lastPos == self.currentPos) or \
                   self.currentStatus != VehicleStatus.PARKED: 
                distMoved = network.getDistanceLong(self.lastLink, self.lastPos,
                                                    self.currentLink,
                                                    self.currentPos)
                if distMoved < LARGEDIST: # ignore large numbers
                    self.totalDistance += distMoved
                    # update passengers
                    for p in self.currentPassengers:
                        peopleCollection.incrementPersonDistance(p, distMoved)
                    # update shared/deadheading
                    if self.countPassengers >= 2:
                        self.shared += distMoved
                    if self.countPassengers == 0:
                        self.deadheading += distMoved
                        
        nextUpdate = self.getNextStop()
        # if at target and not depot; "at target" considered to be within
        # STOP_OFFSET of actual target, otherwise bus crowding delays passengers
        # unnecessarily
        while nextUpdate != None and nextUpdate.stopType != StopType.DEPOT and \
            nextUpdate.link == self.currentLink and \
            nextUpdate.pos - self.currentPos < STOP_OFFSET:
            print step, self.name, nextUpdate.link, nextUpdate.pos, \
                  nextUpdate.stopType, self.currentLink, self.currentPos, \
                  nextUpdate.serviceTime
            # if target is a pickup
            if nextUpdate.stopType == StopType.PICKUP:
                peopleCollection.updatePersonPickup(nextUpdate.personID, step)
                self.countPassengers += 1
                self.currentStatus = VehicleStatus.BOOKED
                self.currentPassengers.append(nextUpdate.personID)
                print self.name, self.countPassengers, " on board"
                nextUpdate = self.getNextStop(True)
            # else if target is a dropoff
            elif nextUpdate.stopType == StopType.DROPOFF:
                self.countPassengers -= 1
                peopleCollection.updatePersonDropoff(nextUpdate.personID, step)
                peopleCollection.incrementPersonDistance(nextUpdate.personID,
                                                         nextUpdate.pos)
                self.totalPassengers += 1
                self.currentPassengers.remove(nextUpdate.personID)
                self.occupancyTime += \
                    peopleCollection.getTravelTime(nextUpdate.personID)
                print self.name, self.countPassengers, " on board"
                nextUpdate = self.getNextStop(True)
            

        # update route
        if nextUpdate != None:
            if nextUpdate.stopType == StopType.DEPOT:
                # no future requests at this stage
                if self.operatingState == VehicleState.vsRunning:
                    assert self.countPassengers == 0
                    currentStop = self.getCurrentPos()
                    goHomeTime = self.end - network.getTime(currentStop,
                                                            nextUpdate)
                    if step < goHomeTime: # not time to go home yet
                        if self.currentStatus != VehicleStatus.PARKED:
                            self.currentStatus = VehicleStatus.PARKED
                            print self.name, "waiting", goHomeTime
                            self.parkedLink = self.currentLink
                            self.parkedPos = self.currentPos + PARK_OFFSET
                            # !! was 60+5*self.i
                            # if many vehicles and few set stops, then parking
                            # somewhere else reduces delay to other vehicles
                            traci.vehicle.setStop(self.name, self.parkedLink,
                                                  self.parkedPos, 0,
                                                  (goHomeTime - step)*MILLISECONDS)
                    else:
                        # raise from parking position and go home
                        traci.vehicle.setStop(self.name, self.parkedLink,
                                              self.parkedPos, 0, 0) 
                        self.operatingState = VehicleState.vsGoingHome
                        traci.vehicle.changeTarget(self.name, nextUpdate.link)
                        self.currentStatus = VehicleStatus.BOOKED
                        print self.name, "moving to depot"
                #elif self.operatingState == VehicleState.vsNotStarted:
                    # waiting at start
            else: # update route for next pickup/dropoff
                traci.vehicle.changeTarget(self.name, nextUpdate.link)
                traci.vehicle.setStop(self.name, nextUpdate.link,
                                      nextUpdate.pos, 0, DWELLTIME)
                if self.currentStatus == VehicleStatus.PARKED:
                    # raise from parking position if parked
                    traci.vehicle.setStop(self.name, self.parkedLink,
                                          self.parkedPos, 0, 0) 
                self.currentStatus = VehicleStatus.BOOKED
            

        # store last known link
        self.lastLink = self.currentLink
        self.lastPos = self.currentPos

    def getCurrentLink(self):
        """ return current link 
        () -> Stop"""
        return self.currentLink

    def output(self):
        """ print details of vehicle """
        d = self.visited[-1]
        #endPos = network.getEdgeLength(d.link) # add length of final link
        #self.totalDistance += endPos
        print self.name + "," + str(self.totalPassengers) + "," + \
              str(self.totalDistance)

    def getOutput(self):
        """ print details of vehicle """
        # check that distance travelled with 0 and 2+ passengers is less
        # than total distance travelled
        assert self.totalDistance >= self.deadheading + self.shared
        return [self.name, self.totalPassengers, self.totalDistance,
                self.occupancyTime / float(self.actualEnd),
                self.totalPassengers/float(self.totalDistance)*M2KM,
                self.shared / float(self.totalDistance),
                self.deadheading / float(self.totalDistance),
                self.shared, self.deadheading]
        

    
