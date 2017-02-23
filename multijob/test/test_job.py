# pylint: disable=missing-docstring,invalid-name,unused-variable

import multijob.job

def describe_private_dict_list_product():

    def it_returns_dicts_with_each_combination():
        dict_of_lists = dict(
            alpha=['a', 'b', 'c'],
            digit=[1, 2, 3],
            symbol=['*', '+'])

        expected = [
            dict(alpha='a', digit=1, symbol='*'),
            dict(alpha='a', digit=1, symbol='+'),
            dict(alpha='a', digit=2, symbol='*'),
            dict(alpha='a', digit=2, symbol='+'),
            dict(alpha='a', digit=3, symbol='*'),
            dict(alpha='a', digit=3, symbol='+'),
            dict(alpha='b', digit=1, symbol='*'),
            dict(alpha='b', digit=1, symbol='+'),
            dict(alpha='b', digit=2, symbol='*'),
            dict(alpha='b', digit=2, symbol='+'),
            dict(alpha='b', digit=3, symbol='*'),
            dict(alpha='b', digit=3, symbol='+'),
            dict(alpha='c', digit=1, symbol='*'),
            dict(alpha='c', digit=1, symbol='+'),
            dict(alpha='c', digit=2, symbol='*'),
            dict(alpha='c', digit=2, symbol='+'),
            dict(alpha='c', digit=3, symbol='*'),
            dict(alpha='c', digit=3, symbol='+'),
        ]

        # pylint: disable=protected-access
        actual = list(multijob.job._dict_list_product(dict_of_lists))

        assert actual == expected

    def GIVEN_empty_dict_THEN_returns_empty_dict():
        # pylint: disable=protected-access
        assert list(multijob.job._dict_list_product(dict())) == [dict()]
