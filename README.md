SUMOoD
======

Modelling bus-on-demand using SUMO and TraCI.

SUMOoD (SUMO on Demand) is a TraCI-based implementation of the simulation
presented in [1,2].

The system deals with ad-hoc requests from passengers wanting to travel between
two locations. Passengers are picked up from intersections (nodes) only.

This model was replicated in SUMO using the TraCI Python interface. Passengers
were restricted to nodes so that results of both models could be compared. In
this case, it meant a node was represented by one outgoing link in SUMO, about
50 metres past the intersection.

For more information about the model and potential extensions, please see
http://imod-au.info/sumood.

References
----------

[1] Thompson, R. G., Sakulchariyalert, K., Haasz, J., Winter, S. and Mendis, P.
(2011), Determining the Viability of a Demand Responsive Transport System,
published at http://imod-au.info/thompson11/.

[2] Ronald, N., Thompson, R. G., Haasz, J. and Winter, S. (2013), Determining the
Viability of a Demand-Responsive Transport System under Varying Demand
Scenarios. Proceedings of the 6th ACM SIGSPATIAL International Workshop on
Computational Transportation Science, Orlando, Florida.

Acknowledgements
----------------

This work has been supported by the Australian Research Council (LP120200130).
