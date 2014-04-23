# -*- coding: utf-8 -*-
"""
@file    drt.py
@author  Nicole Ronald
@date    2014-03-17
@version 

Sets up and runs the simulation using SUMO and TraCI.

Based on constants.py, by Michael Behrisch and Daniel Krajzewicz.

SUMOoD (SUMO on Demand); see http://imod-au.info/sumood
Copyright (C) 2014 iMoD
SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2008-2012 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""


import subprocess, random, sys, os


PORT = 8813
SUMO_HOME = os.path.realpath(
    os.environ.get("SUMO_HOME",
                   os.path.join(os.path.dirname(__file__),
                                "..", "..", "..", "..","..","..")))
sys.path.append(os.path.join(SUMO_HOME, "tools"))

import traci
import traci.constants as tc
from vehicle import Vehicle
from vehicleCollection import VehicleCollection, vehicleCollection
from stop import Stop, StopType
from person import Person
from peopleCollection import PeopleCollection, peopleCollection

try:
    from sumolib import checkBinary
except ImportError:
    def checkBinary(name):
        return name
NETCONVERT = checkBinary("netconvert")
SUMO = checkBinary("sumo")
SUMOGUI = checkBinary("sumo-gui")

step=0
persons = []

def run(runId):
    """starts simulation, reads people file, runs sim, outputs results"""
    global peopleCollection, persons
    traci.init(PORT)
    print "Init"
    traci.simulation.subscribe([tc.VAR_DEPARTED_VEHICLES_IDS,
                                tc.VAR_ARRIVED_VEHICLES_IDS])

    filename = 'SampleInput/Requests/1a/sumo-%s-people.csv' % (runId)
    peopleCollection.readFile(filename)
    persons = peopleCollection.getList()
    persons.sort()
    

    while traci.simulation.getMinExpectedNumber() > 0:
        #traci.simulationStep()
        doStep()

    peopleCollection.output('./output/sumo-output1a/', runId)
    vehicleCollection.output('./output/sumo-output1a/', runId)
    traci.close()


def doStep():
    """ executes one step of simulation """
    global step
    step += 1
    traci.simulationStep()

    moveNodes = []  
    for veh, subs in traci.vehicle.getSubscriptionResults().iteritems():
        moveNodes.append((veh, subs[tc.VAR_ROAD_ID], subs[tc.VAR_LANEPOSITION]))

    departed = traci.simulation.getSubscriptionResults()[tc.VAR_DEPARTED_VEHICLES_IDS]
    for v in departed:
        if traci.vehicle.getTypeID(v) == "taxi":
            traci.vehicle.subscribe(v)
            subs = traci.vehicle.getSubscriptionResults(v)
            moveNodes.append((v, subs[tc.VAR_ROAD_ID],
                              subs[tc.VAR_LANEPOSITION]))
            vehicleCollection.addVehicle(Vehicle(v))
    for vehicleID, edge, pos in moveNodes:
        #print traci.vehicle.getPersonNumber(vehicleID)
        vehicleCollection.getVehicle(vehicleID).update(step)

    # remove vehicles from active list if they have left SUMO
    arrived = traci.simulation.getSubscriptionResults()[tc.VAR_ARRIVED_VEHICLES_IDS]
    for v in arrived:
        vehicleCollection.stopVehicle(v, step)

    # check for new requests
    newRequests = [p for p in persons if p.getCallTime() == step]
    for p in newRequests:
        success = vehicleCollection.addBookingToOptimumItinerary(p, step)
        if success == -1:
            p.rejected()
            print str(p.personID) + " rejected"
        persons.remove(p)         
        


if __name__ == "__main__":

    sumoExe = SUMO
    sumoConfig = "./SampleInput/SUMO/grid.sumocfg"
    sumoProcess = subprocess.Popen([sumoExe, sumoConfig], stdout=sys.stdout,
                                   stderr=sys.stderr)

    
    runId = "1a-%s-%02d" % (sys.argv[1], int(sys.argv[2]))
    print runId
    run(runId)
    sumoProcess.wait()
