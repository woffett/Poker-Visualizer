# Poker-Visualizer

USAGE:
bokeh serve --show comp_algs.py --args leduc3 P1 diff cfr_RM_la_alt cfr_RM+_la_alt

args:
1. the game to analyze
   - [kuhn,leduc3,leduc5]
2. the player infosets we want to look at
   - [P1,P2]
3. the metric to sort the infosets by (will be adding to this!)
   - [diff, square, reachIterate=<iterateNumber>]
4. the names of algorithms you want to compare, all w/ 500 iterates
   - [cfr_RM_la_alt, 
      cfr_RM+_la_alt,
      cfr_RM_la_nalt,
      cfr_RM+_la_nalt,
      cfr_RM_nla_alt,
      cfr_RM+_nla_alt,
      cfr_RM_nla_nalt,
      cfr_RM+_nla_nalt,
      strategies_egt_as (kuhn and leduc3 only), 
      strategies_cfrplus (kuhn and leduc3 only)
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
- add option for log scale
- contact Gabriele/Christian to make powerpoints of interesting results

Dependencies:
- Python (2.7+ or 3.6+)
- pycosat
- PyYaml
- Requests
- Anaconda
  - holoviews
  - param >=1.5, <2.0

