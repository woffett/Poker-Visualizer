# Poker-Visualizer

USAGE:
bokeh serve --show sorted_comp.py --args leduc3 P1 diff cfr_RM_la_alt cfr_RM+_la_alt

args:
1. the game to analyze
   - [kuhn,leduc3,leduc5]
2. the player infosets we want to look at
   - [P1,P2]
3. the metric to sort the infosets by (will be adding to this!)
   - [diff, square, reachIterate=<iterateNumber>]
4. the names of algorithms you want to compare, all w/ 500 iterates unless specified
   - [cfr_RM_la_alt, 
      cfr_RM+_la_alt,
      cfr_RM_la_nalt,
      cfr_RM+_la_nalt,
      cfr_RM_nla_alt,
      cfr_RM+_nla_alt,
      cfr_RM_nla_nalt,
      cfr_RM+_nla_nalt,
      strategies_egt_as, (kuhn and leduc3 only, 2000 iterates)
      strategies_cfrplus (kuhn and leduc3 only, 2000 iterates)
      ]

To-do:
- sorting by average sum of squared difference compared to last iterates
  - choose how to sort the iterates
  - whether algorithms converge to the same thing
  - consider convergence speed of the two algorithms (comparing integrals)
  - always put the worst first
  - absolute difference of final strategies
- optional sub-sampling
  - default: no sub-sampling
- print out reach (on final iteration) of each infoset at the side?
  - if the reach is low, then divergence between algorithms doesn't even matter
  - maybe weight the ordering by the reach?
  - also print out reach rank
- fix x-axis to reflect actual iterate numbers
- add option for log scale
- contact Gabriele/Christian to make powerpoints of interesting results

QUESTIONS:
- for the reach: how to calculate?
- do we want to sort the list by reach of the infosets at each depth?

Dependencies:
- Python (2.7+ or 3.6+)
- pycosat
- PyYaml
- Requests
- Anaconda
  - holoviews
  - param >=1.5, <2.0

