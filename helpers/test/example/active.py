from cwf.helpers import Parts, P

parts = Parts(
        __package__
      , P("part1")
      , P("part2")
      , P("part3", base=True)
      )
