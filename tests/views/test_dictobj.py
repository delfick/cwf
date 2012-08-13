# coding: spec

from src.views.base import DictObj

describe "DictObj":
    it "starts as an empty dictionary":
        d = DictObj()
        self.assertListEqual(d.keys(), [])
        self.assertListEqual(d.values(), [])
        self.assertListEqual(d.items(), [])

    it "behaves like a dictionary":
        d = DictObj()

        d['a'] = 3
        d['b'] = 4
        d['c'] = 5

        self.assertListEqual(sorted(d.keys()), sorted(['a', 'b', 'c']))
        self.assertListEqual(sorted(d.values()), sorted([3, 4, 5]))
        self.assertListEqual(sorted(d.items()), sorted([('a', 3), ('b', 4), ('c', 5)]))

        self.assertEqual(d['a'], 3)
        self.assertEqual(d['b'], 4)
        self.assertEqual(d['c'], 5)

        with self.assertRaises(KeyError):
            self.assertEqual(d['d'], 7)

        self.assertIs(d.get('e'), None)
        self.assertEqual(d.get('f', 5), 5)

    it "behaves like an object":
        d = DictObj()

        d.a = 3
        d.b = 4
        d.c = 5

        self.assertListEqual(sorted(d.keys()), sorted(['a', 'b', 'c']))
        self.assertListEqual(sorted(d.values()), sorted([3, 4, 5]))
        self.assertListEqual(sorted(d.items()), sorted([('a', 3), ('b', 4), ('c', 5)]))

        self.assertEqual(d.a, 3)
        self.assertEqual(d.b, 4)
        self.assertEqual(d.c, 5)

        with self.assertRaises(AttributeError):
            self.assertEqual(d.d, 7)

        self.assertIs(d.get('e'), None)
        self.assertEqual(d.get('f', 5), 5)
