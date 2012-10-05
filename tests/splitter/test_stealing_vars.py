# coding: spec

from cwf.splitter.imports import steal
import stolen_vars

import itertools
import fudge

describe "Stealing variables":

    it "should complain if folder, globals or locals isn't supplied":
        value = fudge.Fake("value")
        for combination in itertools.combinations(['folder', 'globals', 'locals'], 2):
            kwargs = {key:value for key in combination}
            with self.assertRaises(Exception):
                steal("a", **kwargs)

    @fudge.patch("__builtin__.execfile", "os.path.join")
    it "execfiles on combination of folder and each filename with globals and locals", fake_execfile, fake_join:
        fn1 = fudge.Fake("fn1")
        fn2 = fudge.Fake("fn2")
        folder = fudge.Fake("folder")
        location1 = fudge.Fake("location1")
        location2 = fudge.Fake("location2")

        lcls = fudge.Fake("lcls")
        glbls = fudge.Fake("glbls")

        # Each location execfile'd is determined by joining folder with each filename
        (fake_join.expects_call()
            .with_args(folder, "%s.py" % fn1).returns(location1)
            .next_call().with_args(folder, "%s.py" % fn2).returns(location2)
            )

        # Execfile is called for each location
        (fake_execfile.expects_call()
            .with_args(location1, glbls, lcls)
            .next_call().with_args(location2, glbls, lcls)
            )

        # Call steal
        steal(fn1, fn2, folder=folder, globals=glbls, locals=lcls)

    it "should be able to steal variables from other files":
        # stolen_vars uses splitter.imports.steal
        # To steal from vars/numbers.py and vars/letters.py
        expected = [
              ('a', 'a')
            , ('b', 'b')
            , ('c', 'c')
            , ('one', 1)
            , ('two', 2)
            , ('three', 3)
            ]

        for key, val in expected:
            getattr(stolen_vars, key) |should| equal_to(val)
