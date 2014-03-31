# -*- coding: utf-8 -*-
"""
@file    vehicleCollection.py
@author  Nicole Ronald
@date    2014-03-17
@version 

Defines a collection of vehicles.

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
from vehicle import VehicleState
import csv

class VehicleCollection:
    """ collection of vehicles """
    fleet = {}

    def __init__(self):
        self.fleet = {}

    def addVehicle(self, vehicle):
        """ add a vehicle to the collection 
        (Vehicle)"""
        self.fleet[vehicle.name] = vehicle

    def stopVehicle(self, vehicleID, step):
        """ list a vehicle as stopped once it has left the simulation
        (string, int)"""
        if vehicleID in self.fleet:
            self.fleet[vehicleID].stop(step)

    def getValues(self):
        """ return a list of vehicles
        () -> Vehicle[]"""
        return self.fleet.values()

    def getVehicle(self, vehicleID):
        """ return a particular vehicle 
        (string) -> Vehicle """
        return self.fleet[vehicleID]

    def removeVehicles(self, step):
        for v in self.fleet:
            if self.fleet[v].parked == 900 or self.fleet[v].end == step:
                traci.vehicle.remove(v)
                

    def output(self, folder="./", code="0"):
        """ print details of all vehicles, to vehicle.out.csv in an
        optionally-specified folder """
        summary = {"passengers" :0, "distance": 0.0, "tripsVKT": 0.0}
        with open(folder + code + '-vehicle.out.csv', 'wb') as csvfile:
            vehicleWriter = csv.writer(csvfile, delimiter=',')
            vehicleWriter.writerow(["vehicleID","totalPassengers",
                                    "totalDistance","avOccupancy",
                                    "trips/VKT","sharedProp","deadheadProp",
                                    "shared","deadhead"])
            for vehicle in self.fleet.values():
                vehOutput = vehicle.getOutput()
                vehicleWriter.writerow(vehOutput)
                summary["passengers"] += vehOutput[1]
                summary["distance"] += vehOutput[2]
                

        with open(folder + code + '-vehicle-summary.out.csv', 'wb') as csvfile:
            vehicleWriter = csv.writer(csvfile, delimiter=',')
            vehicleWriter.writerow(["numVehicles","passengersCarried",
                                    "totalDistance", "trips/VKT"])
            output = []
            output.append(len(self.fleet.values()))
            output.append(summary["passengers"])
            output.append(summary["distance"])
            output.append(summary["passengers"]/summary["distance"]*1000)
            vehicleWriter.writerow(output)
                

    def addBookingToOptimumItinerary(self, person, step):
        """ determine best vehicle for person and add them to it
        (Person, int)"""
        vehicle = None
        penalty = 0.0
        bestVehiclePenalty = 10000000
        bestIncrPenalty = 100000000
        puPosition = None # link
        duPosition = None # link
        bestVehicle = None
        bestPUPosition = None # link
        bestDOPosition = None # link
        puLink = None
        doLink = None # link

        # extract values from person
        personID = person.personID
        link1 = person.getOrigin().link
        pos1 = person.getOrigin().pos
        link2 = person.getDestination().link
        pos2 = person.getDestination().pos
        puLink = Stop(personID, link1, pos1, StopType.PICKUP)
        doLink = Stop(personID, link2, pos2, StopType.DROPOFF)

        # iterate over all vehicles
        for veh in self.fleet.values():
            if veh.getState() <= VehicleState.vsRunning: # only if not stopped
                (puPosition, doPosition, penalty) = \
                    veh.calcTentativeItineraryPenalty(puLink, doLink, step)
                print veh.name, penalty, penalty - \
                      veh.calcCurrentItineraryPenalty(step)
                if penalty < 900000:
                    incrPenalty = penalty - \
                                  veh.calcCurrentItineraryPenalty(step)
                    # update if best incremental penalty
                    if incrPenalty < bestIncrPenalty:
                        bestVehicle = veh
                        bestIncrPenalty = incrPenalty
                        bestVehiclePenalty = penalty
                        bestDropoffPosition = doPosition
                        bestPickupPosition = puPosition

        # add person to best vehicle
        if bestVehicle != None:
            bestVehicle.addPerson(person, bestPickupPosition,
                                  bestDropoffPosition, bestVehiclePenalty)
            return 0
        else:
            return -1
        
vehicleCollection = VehicleCollection()


