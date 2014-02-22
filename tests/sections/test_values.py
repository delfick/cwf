# coding: spec

from noseOfYeti.tokeniser.support import noy_sup_setUp
from should_dsl import should, should_not
from django.test import TestCase

from cwf.sections.errors import ConfigurationError
from cwf.sections.values import Values

import fudge

# Make the errors go away
be, equal_to, be_thrown_by, be_kind_of = None, None, None, None

describe TestCase, "Values":
    describe "initialisation":
        it "doesn't complain with default values":
            Values()
            assert True

        it "complains if each isn't callable":
            for val in (1, [1], {1:2}, True, type('o', (object, ), {})()):
                caller = lambda : Values(each=val)
                ConfigurationError |should| be_thrown_by(caller)

        it "doesn't complain if each is falsey or callable":
            for val in (0, [], {}, False, fudge.Fake("callable"), lambda:1):
                caller = lambda : Values(each=val)
                ConfigurationError |should_not| be_thrown_by(caller)

        it "complains if sorter is neither boolean or callable":
            for val in (0, 1, [], [1], {}, {1:2}, type('o', (object, ), {})()):
                caller = lambda : Values(sorter=val)
                ConfigurationError |should| be_thrown_by(caller)

        it "doesn't complain if sorter is either boolean or callable":
            for val in (False, True, fudge.Fake("callable"), lambda:2):
                caller = lambda : Values(sorter=val)
                ConfigurationError |should_not| be_thrown_by(caller)

    describe "Getting info":
        before_each:
            self.path = fudge.Fake("path")
            self.request = fudge.Fake("request")
            self.parent_url_parts = fudge.Fake("parent_url_parts")
            self.info = (self.request, self.parent_url_parts, self.path)

            self.fake_get_values = fudge.Fake("get_values")
            self.values = type("Values", (Values, ), {'get_values' : self.fake_get_values})()

        def get_info(self):
            return list(self.values.get_info(self.request, self.parent_url_parts, self.path))

        @fudge.test
        it "yields all (alias, url) from result of get_values":
            val1 = fudge.Fake("val1")
            val2 = fudge.Fake("val2")
            self.fake_get_values.expects_call().with_args(self.info).returns([val1, val2])
            self.get_info() |should| equal_to([val1, val2])

        @fudge.test
        it "doesn't yield any falsey values":
            val1 = fudge.Fake("val1")
            val2 = fudge.Fake("val2")
            self.fake_get_values.expects_call().with_args(self.info).returns([val1, None, val2])
            self.get_info() |should| equal_to([val1, val2])

    describe "Getting values":
        before_each:
            self.info = fudge.Fake("info")
            self.fake_sort = fudge.Fake("sort")
            self.fake_transform_values = fudge.Fake("transform_values")
            self.fake_normalised_values = fudge.Fake("normalised_values")

            self.values = fudge.Fake("values")
            self.sorted = fudge.Fake("sorted")
            self.normalised = fudge.Fake("normalised")
            self.transformed = fudge.Fake("transformed")

            self.values_kls = type("Values", (Values, ), {
                  'sort' : self.fake_sort
                , 'transform_values' : self.fake_transform_values
                , 'normalised_values' : self.fake_normalised_values
                }
            )

        @fudge.test
        it "returns None if self.values is falsey":
            values = self.values_kls(values=None)
            values.get_values(self.info) |should| be(None)

        @fudge.test
        it "sorts normalised values before transformation if not self.sort_after_transform":
            self.fake_normalised_values.expects_call().with_args(self.info).returns(self.normalised)
            self.fake_sort.expects_call().with_args(self.normalised).returns(self.sorted)
            self.fake_transform_values.expects_call().with_args(self.sorted, self.info).returns(self.transformed)
            result = self.values_kls(values=self.values, sort_after_transform=False).get_values(self.info)
            result |should| be(self.transformed)

        @fudge.test
        it "sorts normalised values after transformation if self.sort_after_transform":
            self.fake_normalised_values.expects_call().with_args(self.info).returns(self.normalised)
            self.fake_transform_values.expects_call().with_args(self.normalised, self.info).returns(self.transformed)
            self.fake_sort.expects_call().with_args(self.transformed).returns(self.sorted)
            result = self.values_kls(values=self.values, sort_after_transform=True).get_values(self.info)
            result |should| be(self.sorted)

    describe "Transforming values":
        before_each:
            self.info = fudge.Fake('info')

        @fudge.test
        it "maps self.values to self.each with passed in info if self.each is set":
            number = {'num' : 0}
            def each_func(info, value):
                info |should| be(self.info)
                number['num'] += 1
                return (number['num'], value)

            v1 = fudge.Fake("v1")
            v2 = fudge.Fake("v2")
            v3 = fudge.Fake("v3")
            values = [v1, v2, v3]
            result = Values(each=each_func).transform_values(values, self.info)
            result |should| equal_to([(1, v1), (2, v2), (3, v3)])

        it "transforms list of values into list of double tuples of each value if self.each is not set":
            v1 = fudge.Fake("v1")
            v2 = fudge.Fake("v2")
            v3 = fudge.Fake("v3")
            values = [v1, v2, v3]
            result = Values(each=None).transform_values(values, self.info)
            result |should| equal_to([(v1, v1), (v2, v2), (v3, v3)])

    describe "Getting normalised values":
        before_each:
            self.info = fudge.Fake('info')

        @fudge.test
        it "calls values with info if callable":
            def values(info):
                info |should| be(self.info)
                yield 1
                yield 2
                yield 3

            Values(values=values, as_set=False).normalised_values(self.info) |should| equal_to([1, 2, 3])

            values2 = fudge.Fake('values2').expects_call().with_args(self.info).returns([5, 6, 7])
            Values(values=values2, as_set=False).normalised_values(self.info) |should| equal_to([5, 6, 7])

        @fudge.test
        it "turns result of calling values into a set if self.as_set":
            def values(info):
                info |should| be(self.info)
                yield 1
                yield 2
                yield 3

            result = Values(values=values, as_set=True).normalised_values(self.info)
            result |should| be_kind_of(set)
            result |should| equal_to(set([1, 2, 3]))

            values2 = fudge.Fake('values2').expects_call().with_args(self.info).returns([5, 6, 7])
            result = Values(values=values2, as_set=True).normalised_values(self.info)
            result |should| be_kind_of(set)
            result |should| equal_to(set([5, 6, 7]))

        @fudge.test
        it "turns values into a set if self.as_set":
            result = Values(values=[8, 8, 9, 0], as_set=True).normalised_values(self.info)
            result |should| be_kind_of(set)
            result |should| equal_to(set([8, 9, 0]))

        @fudge.test
        it "returns values as is if not callable and not self.as_set":
            values = type("values", (object, ), {})()
            result = Values(values=values, as_set=False).normalised_values(self.info)
            result |should| be(values)

    describe "Sorting values":
        before_each:
            self.values = fudge.Fake("values")
            self.sorter = fudge.Fake("sorter")
            self.sorted = fudge.Fake("sorted")

        it "does nothing if no sorter specified":
            Values(sorter=False).sort(self.values) |should| be(self.values)

        @fudge.patch("__builtin__.sorted")
        it "calls sorted with sorter as function if sorter is callable", fake_sorted:
            fake_sorted.expects_call().with_args(self.values, self.sorter).returns(self.sorted)
            Values(sorter=self.sorter).sort(self.values) |should| be(self.sorted)

        @fudge.patch("__builtin__.sorted")
        it "calls sorted on values with no function if sorter is truthy but not callable", fake_sorted:
            fake_sorted.expects_call().with_args(self.values).returns(self.sorted)
            Values(sorter=True).sort(self.values) |should| be(self.sorted)
