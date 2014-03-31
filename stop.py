# -*- coding: utf-8 -*-
"""
@file    stop.py
@author  Nicole Ronald
@date    2014-03-17
@version 

Defines a stop in a plan (both vehicle and passenger).

SUMOoD (SUMO on Demand); see http://imod-au.info/sumood
Copyright (C) 2014 iMoD
SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2008-2012 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""


class Stop:
    """ Represents a stop in a vehicle's and passenger's plan """

    def __init__(self, personID, link, pos, stopType, serviceTime = None):
        self.personID = personID
        self.link = link
        self.pos = pos
        self.stopType = stopType
        self.serviceTime = serviceTime
            

    def printLn(self):
        print self.personID, self.link, self.pos, self.stopType, self.serviceTime

class StopType:
    """ Represents the different type of stops """
    DEPOT = 0
    PICKUP = 1
    DROPOFF = 2
    CURRENT = 3
    WAIT = 4
