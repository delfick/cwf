# coding: spec

from cwf.views.base import DictObj

describe "DictObj":
    it "starts as an empty dictionary":
        d = DictObj()
        d.keys() |should| equal_to([])
        d.values() |should| equal_to([])
        d.items() |should| equal_to([])

    it "behaves like a dictionary":
        d = DictObj()

        d['a'] = 3
        d['b'] = 4
        d['c'] = 5

        sorted(d.keys()) |should| equal_to(sorted(['a', 'b', 'c']))
        sorted(d.values()) |should| equal_to(sorted([3, 4, 5]))
        sorted(d.items()) |should| equal_to(sorted([('a', 3), ('b', 4), ('c', 5)]))

        d['a'] |should| equal_to(3)
        d['b'] |should| equal_to(4)
        d['c'] |should| equal_to(5)

        with self.assertRaises(KeyError):
            d['d'] |should| be(7)

        d.get('e') |should| be(None)
        d.get('f', 5) |should| equal_to(5)

    it "behaves like an object":
        d = DictObj()

        d.a = 3
        d.b = 4
        d.c = 5

        sorted(d.keys()) |should| equal_to(sorted(['a', 'b', 'c']))
        sorted(d.values()) |should| equal_to(sorted([3, 4, 5]))
        sorted(d.items()) |should| equal_to(sorted([('a', 3), ('b', 4), ('c', 5)]))

        d.a |should| equal_to(3)
        d.b |should| equal_to(4)
        d.c |should| equal_to(5)

        with self.assertRaises(AttributeError):
            d.d |should| equal_to(7)

        d.get('e') |should| be(None)
        d.get('f', 5) |should| equal_to(5)
