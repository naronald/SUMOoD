# -*- coding: utf-8 -*-
"""
@file    network.py
@author  Nicole Ronald
@date    2014-03-17
@version 

Defines an interface to retrieving network details via TraCI.

SUMOoD (SUMO on Demand); see http://imod-au.info/sumood
Copyright (C) 2014 iMoD
SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2008-2012 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""


import subprocess, random, sys, os
SUMO_HOME = os.path.realpath(
                os.environ.get("SUMO_HOME",
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "..",
                             "..","..")))
sys.path.append(os.path.join(SUMO_HOME, "tools"))

import traci
import traci.constants as tc

class Network:
    """ Interface between system and network representation """

    def getEdgeLength(self, link):
        """ returns length of edge, by measuring lane 0 
        (string) -> float""" 
        return traci.lane.getLength(link+"_0")


    def getVehicleCurrentEdge(self, vehicleID):
        """ return the edge where the vehicle currently is 
        (string) -> string"""
        return traci.vehicle.getRoadID(vehicleID)

    def getVehicleCurrentPosition(self, vehicleID):
        """ return the current lane position of the vehicle 
        (string) -> float"""
        return traci.vehicle.getLanePosition(vehicleID)

    def getDistance(self, origin, destination):
        """ return the distance between two stops 
        (Stop, Stop) -> float"""
        return float(traci.simulation.getDistanceRoad(
            origin.link, origin.pos,
            destination.link, destination.pos,
            True))

    def getDistanceLong(self, oLink, oPos, dLink, dPos):
        """ return the distance between two stops provided as link/pos
        (string, string, string, string) -> float"""
        return float(traci.simulation.getDistanceRoad(
            oLink, oPos,
            dLink, dPos,
            True))

    def getTime(self, origin, destination):
        """ return travel time between two stops, based on speed limits 
        (Stop, Stop) -> float"""
        return traci.simulation.getDistanceTime(
            origin.link, origin.pos,
            destination.link, destination.pos)

network = Network()
        
