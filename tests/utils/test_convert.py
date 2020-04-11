from datetime import datetime, timedelta, date

import builtins
import numpy as np
import pandas as pd
from pytest import raises
from tests.utils.convert_examples import BaseClass, Class2, SubClass
from tests.utils.convert_examples import SubClass as SubClassSame
import tests.utils.convert_examples as ex
from triad.utils.convert import (to_bool, to_datetime, to_timedelta,
                                 _parse_value_and_unit, as_type,
                                 str_to_instance, str_to_type, to_function,
                                 to_instance, to_size, to_type)


def test_to_size():
    raises(ValueError, lambda: to_size(None))
    raises(ValueError, lambda: to_size(""))
    raises(ValueError, lambda: to_size("abc"))
    raises(AssertionError, lambda: to_size("-1"))
    raises(AssertionError, lambda: to_size(-1))
    raises(ValueError, lambda: to_size("1xx"))
    assert 0 == to_size(0)
    assert 1 == to_size(1)
    assert 1 == to_size(1.9)
    assert 10 == to_size(" 1 0 B ")
    assert 10 * 1024 == to_size(" 10k")
    assert 10 * 1024 * 1024 == to_size(" 10 m b")
    assert 10 * 1024 * 1024 * 1024 == to_size("10g")
    assert 10 * 1024 * 1024 * 1024 * 1024 == to_size("10tb")
    assert int(1.1 * 1024 * 1024) == to_size(" 1 . 1 mb ")


def test_parse_value_and_unit():
    raises(ValueError, lambda: _parse_value_and_unit(None))
    raises(ValueError, lambda: _parse_value_and_unit(""))
    raises(ValueError, lambda: _parse_value_and_unit("abc"))
    assert (1.0, "") == _parse_value_and_unit(1)
    assert (1.1, "") == _parse_value_and_unit(1.1)
    assert (1.1, "") == _parse_value_and_unit(1.1)
    assert (1.1, "") == _parse_value_and_unit(np.float32(1.1))
    assert (1.0, "") == _parse_value_and_unit(" 1 ")
    assert (-1.0, "") == _parse_value_and_unit(" -1.0 ")
    assert (-1.0, "m10") == _parse_value_and_unit(" - 1 . 0 m 1 0 ")


def test_str_to_type():
    assert BaseClass == str_to_type("tests.utils.BaseClass")
    assert BaseClass == str_to_type("tests.utils.convert_examples.BaseClass")
    assert SubClass == str_to_type("SubClass", BaseClass)
    assert SubClassSame == str_to_type("SubClassSame")
    raises(TypeError, lambda: str_to_type(
        "tests.utils.convert_examples.BaseClass", int))
    raises(TypeError, lambda: str_to_type(
        "tests.utils.convert_examples.BaseClass1"))
    raises(TypeError, lambda: str_to_type("pytest.raises"))
    raises(TypeError, lambda: str_to_type("__dummy_impossible__"))

    assert RuntimeError == str_to_type("RuntimeError")
    assert RuntimeError == str_to_type("RuntimeError", Exception)
    raises(TypeError, lambda: str_to_type("RuntimeError", int))


def test_str_to_instance():
    i = str_to_instance("tests.utils.Class2")
    assert isinstance(i, Class2)
    assert i.s == "000"
    i = str_to_instance("tests.utils.Class2", args=[1, 2], kwargs=dict(c=3))
    assert isinstance(i, Class2)
    assert i.s == "123"
    i = str_to_instance("tests.utils.Class2", args=[1, 2], kwargs=dict(c=3))
    assert isinstance(i, Class2)
    assert i.s == "123"


def test_obj_to_type():
    assert to_type(None) is type(None)
    raises(TypeError, lambda: to_type(None, str))
    assert issubclass(to_type(123), int)
    raises(TypeError, lambda: to_type(123, str))
    i = to_type("tests.utils.Class2")
    assert issubclass(i, Class2)
    i = to_type(Class2)
    assert issubclass(i, Class2)
    raises(TypeError, lambda: to_type(Class2, BaseClass))
    raises(TypeError, lambda: to_type("tests.utils.Class2", BaseClass))

    assert ex.__Dummy__ is not __Dummy__
    assert to_type("tests.utils.convert_examples.__Dummy__",
                   first=True) is ex.__Dummy__
    assert to_type("tests.utils.convert_examples.__Dummy__",
                   first=False) is ex.__Dummy__
    assert ex.invoke_to_type("__Dummy__", first=True) is ex.__Dummy__
    assert ex.invoke_to_type("__Dummy__", first=False) is __Dummy__


def test_obj_to_instance():
    raises(ValueError, lambda: to_instance(None))
    i = to_instance("tests.utils.Class2", args=[1, 2, 3])
    assert isinstance(i, Class2)
    assert i.s == "123"
    i = to_instance(Class2, kwargs={"a": 1, "b": 2, "c": 3})
    assert isinstance(i, Class2)
    assert i.s == "123"
    i = to_instance(Class2)
    assert isinstance(i, Class2)
    i = to_instance(Class2, args=[1, 2, 3])
    assert isinstance(i, Class2)
    raises(TypeError, lambda: to_instance(Class2,
                                          BaseClass, args=[1, 2, 3]))
    i = to_instance(Class2("a:int"))
    assert isinstance(i, Class2)
    raises(TypeError, lambda: to_instance(Class2(), BaseClass))
    raises(ValueError, lambda: to_instance(Class2(), args=[1]))
    raises(ValueError, lambda: to_instance(Class2(), kwargs={"a": 1}))

    assert ex.__Dummy__ is not __Dummy__
    assert type(to_instance("__Dummy__")) is __Dummy__
    assert type(to_instance("tests.utils.convert_examples.__Dummy__",
                            first=True)) is ex.__Dummy__
    assert type(to_instance("tests.utils.convert_examples.__Dummy__",
                            first=False)) is ex.__Dummy__


def test_obj_to_function():
    f = to_function("dummy_for_test")
    assert f is dummy_for_test
    f = to_function(dummy_for_test)
    assert f is dummy_for_test
    f = to_function("open")
    assert f is open
    f = to_function("tests.utils.test_convert.dummy_for_test")
    assert f is dummy_for_test
    f = to_function("triad.utils.convert.to_instance")
    assert f is to_instance
    raises(AttributeError, lambda: to_function(None))
    raises(AttributeError, lambda: to_function("asdfasdf"))
    raises(AttributeError, lambda: to_function("BaseClass"))

    assert builtins.min is not min
    assert to_function("min", first=True) is builtins.min
    assert to_function("min", first=False) is min


def test_to_bool():
    raises(TypeError, lambda: to_bool(None))
    assert to_bool("TRUE")
    assert to_bool(True)
    assert to_bool("1")
    assert to_bool(1)
    assert to_bool("Yes")
    assert not to_bool("FALSE")
    assert not to_bool(False)
    assert not to_bool("0")
    assert not to_bool(0)
    raises(TypeError, lambda: to_bool("x"))


def test_to_datetime():
    raises(TypeError, lambda: to_datetime(None))
    dt = datetime.now()
    assert dt == to_datetime(dt)
    assert dt == to_datetime(str(dt))
    assert datetime(2019, 5, 18) == to_datetime("2019-05-18")
    assert datetime(2019, 5, 18, 10, 11, 12) == to_datetime("2019-05-18 10:11:12")
    assert datetime(2019, 5, 18) == to_datetime(date(2019, 5, 18))
    raises(TypeError, lambda: to_datetime("x"))
    raises(TypeError, lambda: to_datetime(123))


def test_to_timedelta():
    raises(TypeError, lambda: to_timedelta(None))
    dt = timedelta(days=2)
    assert dt == to_timedelta(dt)
    assert dt == to_timedelta("2d")
    assert dt == to_timedelta("48h")
    dt = timedelta(days=2, minutes=1)
    assert dt == to_timedelta("2 day 1 min")
    assert dt == to_timedelta("2d1m")
    dt = pd.Timedelta('2d')
    assert timedelta(days=2) == to_timedelta(dt)
    raises(TypeError, lambda: to_timedelta("x"))
    assert timedelta() == to_timedelta(0)
    assert timedelta(seconds=2.5) == to_timedelta(2.5)
    assert timedelta(seconds=2.1) == to_timedelta(np.float64(2.1))
    assert timedelta(seconds=2) == to_timedelta(np.int32(2))
    assert timedelta.max == to_timedelta("Max")
    assert timedelta.max == to_timedelta("InF")
    assert timedelta.min == to_timedelta("mIn")
    assert timedelta.min == to_timedelta("-InF")


def test_as_type():
    assert 10 == as_type(10, int)
    assert 10 == as_type("10", int)
    assert 1 == as_type(1.1, int)
    assert "10" == as_type(10, str)
    assert not as_type(False, bool)
    assert not as_type("no", bool)
    assert as_type("a:int", Class2).s == Class2("a:int").s
    assert as_type(None, Class2).s == Class2(None).s
    assert timedelta(days=2) == as_type('2d', timedelta)
    assert datetime(2019, 5, 18) == as_type("2019-05-18", datetime)


# This is for test_obj_to_function
def dummy_for_test():
    pass


# This is to test str_to_function with first=False
def min() -> bool:
    return True


# This is to test *_to_type with first=False
class __Dummy__(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
