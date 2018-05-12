# Poker-Visualizer

USAGE:
bokeh serve --show sorted_comp.py --args leduc3 P1 diff cfr_RM_la_alt cfr_RM+_la_alt

args:
1. the game to analyze
   - [kuhn,leduc3,leduc5]
2. the player infosets we want to look at
   - [P1,P2]
3. the metric to sort the infosets by (will be adding to this!)
   - [diff, square]
4. the names of algorithms you want to compare
   - [cfr_RM_la_alt,
      cfr_RM+_la_alt,
      cfr_RM_la_nalt,
      cfr_RM+_la_nalt,
      cfr_RM_nla_alt,
      cfr_RM+_nla_alt,
      cfr_RM_nla_nalt,
      cfr_RM+_nla_nalt,
      strategies_egt_as, (kuhn and leduc3 only)
      strategies_cfrplus (kuhn and leduc3 only)
      ]

To-do:
- sorting by average sum of squared difference compared to last iterates
  - choose how to sort the iterates
  - whether algorithms converge to the same thing
  - consider convergence speed of the two algorithms (comparing integrals)
  - always put the worst first
  - absolute difference of final strategies
- develop dropdown with changing actions that are available
- choose different algorithms other than CFR+ and EGT
- optional sub-sampling
  - default: no sub-sampling
- print out reach (on final iteration) of each infoset at the side?
  - if the reach is low, then divergence between algorithms doesn't even matter
  - maybe weight the ordering by the reach?
  - also print out reach rank
- add triangles to 3-action infosets

- getting rid of extraneous actions in the legend
  - changing the selector to select from a third-party widget selector,
    which then chooses from dynamic map