# -*- coding: utf-8 -*-
"""
@file    peopleCollection.py
@author  Nicole Ronald
@date    2014-03-17
@version 

Defines a collection of people who request trips from the
demand-responsive transportation system.

SUMOoD (SUMO on Demand); see http://imod-au.info/sumood
Copyright (C) 2014 iMoD
SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2008-2012 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""


from person import Person
from stop import Stop, StopType
import csv

class PeopleCollection:
    """ a collection of persons """
    people = {}

    def __init__(self):
        self.people = {}

    def readFile(self, fileName):
        """ read people from a file
        format: 
        id, callTime, requestTime, originLink, originPos, destLink, destPos
        (string)"""
        with open(fileName, 'rb') as pFile:
            persons = csv.reader(pFile, delimiter=',')
            for row in persons:
                assert len(row) == 7
                i = row[0]
                entry = int(row[1])
                request = int(row[2])
                originLink = row[3]
                originPos = float(row[4])
                destLink = row[5]
                destPos = float(row[6])

                p = Person(i)
                p.setCallTime(entry)
                p.setRequestTime(request)
                p.setOD(Stop(i, originLink, originPos, StopType.PICKUP,
                             request),
                        Stop(i, destLink, destPos, StopType.DROPOFF))
                self.addPerson(p)
    

    def addPerson(self, person):
        """ add a person to the collection
        (Person)"""
        self.people[person.personID] = person

    def updatePersonPickup(self, personID, time):
        """ set a person's pickup time 
        (string, int)"""
        self.people[personID].setPickupTime(time)

    def updatePersonDropoff(self, personID, time):
        """ set a person's dropoff time 
        (string, int)"""
        self.people[personID].setDropoffTime(time)

    def incrementPersonDistance(self, personID, distance):
        """ increment the distance travelled by a person by the distance
        provided
        (string, float)"""
        self.people[personID].incrementDistance(distance)

    def getTravelTime(self, personID):
        """ return tiem passenger was travelling for occupancy
        (string) -> int"""
        return self.people[personID].travelTime

    def output(self, folder="./", code="0"):
        """ print details for all people, to *-person.out.csv in an optionally
        specified folder with an optionally specified run code
        (string ,string)"""
        with open(folder + code + '-person.out.csv', 'wb') \
            as csvfile:
            peopleWriter = csv.writer(csvfile,
                                      delimiter=',')
            peopleWriter.writerow(\
                ["personID","callTime","requestTime","directDistance",\
                 "actualDistance","directTime","waitTime","pickupTime",\
                 "travelTime", "dropoffTime", "excessTravelTime", \
                 "excessTime", "excessDistance","state"])
        
            for p in self.people.values():
                peopleWriter.writerow(p.getOutput())

    def getList(self):
        """ return a list of people 
        () -> Person[]"""
        persons = []
        for p in self.people.values():
            persons.append(p)
        return persons

    def estimatePenalty(self, personID, dropoffTime):
        """ estimate penalty for a person at an estimated dropoff time """
        return self.people[personID].estimatePenalty(dropoffTime)

peopleCollection = PeopleCollection()

        
