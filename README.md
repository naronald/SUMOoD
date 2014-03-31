SUMOoD
======

Modelling bus-on-demand using SUMO and TraCI.

SUMOoD (SUMO on Demand) is a TraCI-based implementation of the simulation
presented in [1,2].

SUMOoD v0.1 is based on a model of demand-responsive transportation developed by
Kanchana Sakulchariyalert, Russell Thompson, John Haasz, Stephan Winter and
Priyan Mendis in Delphi [1]. This software was developed further by John Haasz,
John McDonald and Nicole Ronald [2]. In this software, vehicles use a variant of
the DARP (Dial-a-Ride Problem) algorithm to pick up and drop off passengers at
nodes in a network. While pre-booking rides is permitted by the software, it was
used to experiment with ad-hoc (e.g., immediate pickups) only.

This model was replicated in SUMO using the TraCI Python interface. SUMOoD
deals with ad-hoc requests from passengers wanting to travel between two
locations.  Passengers were restricted to nodes so that results of both models
could be compared. In this case, it meant a node was represented by one outgoing
link in SUMO, about 50 metres past the intersection.

For more information about the model and potential extensions, please see
http://imod-au.info/sumood.

Installation
------------

SUMOoD has been known to work with SUMO v0.18.0.

Changes are required to the SUMO code as well as the TraCI Python interface.

Running
-------

The request input files are named sumo-&lt;scenario&gt;-&lt;config&gt;-&lt;run&gt;-people.csv,
where scenario and config are strings, and run is a 2-digit integer. In my input
files, the config is an integer-character pair, where the integer signifies the
number of vehicles (i.e., 3, 5, 8, or 10) and the character signifies the demand
("S", "M", "L" -> small (20 requests), medium (40 requests), large (60
requests)).

Vehicles are specified in a normal SUMO .rou file; the vehicle type is "taxi".

The simulation is started with:

python drt.py &lt;config&gt; &lt;run&gt;

Acknowledgements
----------------

This work has been supported by the Australian Research Council (LP120200130).

References
----------

[1] Thompson, R. G., Sakulchariyalert, K., Haasz, J., Winter, S. and Mendis, P.
(2011), Determining the Viability of a Demand Responsive Transport System,
published at http://imod-au.info/thompson11/.

[2] Ronald, N., Thompson, R. G., Haasz, J. and Winter, S. (2013), Determining the
Viability of a Demand-Responsive Transport System under Varying Demand
Scenarios. Proceedings of the 6th ACM SIGSPATIAL International Workshop on
Computational Transportation Science, Orlando, Florida.
