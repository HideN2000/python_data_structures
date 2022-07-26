#-*- coding: utf-8 -*-
import os
import pytest
import random
from string import ascii_lowercase
from typing import Tuple, List
import sys
sys.setrecursionlimit(200000)

from src.data_structure.set import MultiSet

@pytest.mark.xfail()
def test_ill_defined_op() -> None:
    '''test: ill_defined operator func (FAIL)'''
    size = 100
    #ill-defined operator
    S = MultiSet[int](operator=lambda x, y: x // size <= y // size, init_e=-1)

    #randomized_insert_order
    insert_order = [i for i in range(size)]
    random.shuffle(insert_order)

    for x in S:
        S.add(x)

    #not sorted because of ill-defined operator
    assert [x for x in S] == [i for i in range(size)]


@pytest.mark.small
def test_example() -> None:
    '''test: basic multiset example'''
    S: MultiSet[int] = MultiSet[int](
        operator=lambda x, y: x <= y, init_e=1 << 60)

    #insert from 1 to 5
    insert_order = [5, 3, 1, 2, 4]
    delete_order = [1, 4, 2, 5, 3]

    #insert
    for x in insert_order:
        S.add(x)

    #test basic attribute
    assert len(S) == S.max == 5
    assert S.min == 1
    assert [x for x in S] == [i for i in range(1, 5 + 1)]

    #delete
    for x in delete_order:
        S.remove(x)

    assert S.min == S.max == S.e


@pytest.mark.small
def test_kth_element() -> None:
    '''test: kth element of S'''
    size = 100
    S_elements: List[int] = []
    S = MultiSet[int](operator=lambda x, y: x <= y, init_e=-1)

    #randomized_insert_order
    insert_order = [i for i in range(size)]
    random.shuffle(insert_order)

    for x in insert_order:
        S.add(x)
        S_elements = sorted(S_elements + [x])
        assert len(S) == len(S_elements)
        #test kth element
        for i in range(len(S)):
            assert S[i] == S_elements[i]

    #randomized_delete_order
    delete_order = [i for i in range(size)]
    random.shuffle(delete_order)
    for x in delete_order:
        S.remove(x)
        S_elements.remove(x)
        S_elements.sort()
        assert len(S) == len(S_elements)
        #test kth element
        for i in range(len(S)):
            assert S[i] == S_elements[i]


@pytest.mark.small
def test_delete_non_exisent() -> None:
    '''test: erase non-existent element from MultiSet'''

    S: MultiSet[Tuple[int, str]] = MultiSet[Tuple[int, str]](
        operator=lambda x, y: x <= y, init_e=(1 << 60, 'nil'))

    for i, char in enumerate(ascii_lowercase):
        S.add((i, char))

    for i, char in enumerate(ascii_lowercase):
        S.add((i, char))

    #remove from empty S
    with pytest.raises(AssertionError):
        S.remove((-1, 'non-existent-element'))


class TestRandom():
    @pytest.mark.small
    @pytest.mark.parametrize('size', [1, 2, 5, 10, 20, 50, 100])
    def test_small_random(self, size: int) -> None:
        '''test: small random'''
        S: MultiSet[int] = MultiSet[int](
            operator=lambda x, y: x < y, init_e=-1)

        #randomized_insert_order
        insert_order = [i for i in range(size)]
        random.shuffle(insert_order)

        for x in insert_order:
            S.add(x)

        #check if sorted
        assert [x for x in S] == [i for i in range(size)]

        #randomize_delete_order
        delete_order = [i for i in range(size)]
        random.shuffle(delete_order)

        for x in delete_order:
            S.remove(x)

        assert not S

    @pytest.mark.large
    @pytest.mark.parametrize('size', [10000, 20000, 50000, 100000])
    def test_large_random(self, size: int) -> None:
        '''test: large random input'''

        S: MultiSet[int] = MultiSet[int](
            operator=lambda x, y: x < y, init_e=-1)

        #randomized_insert_order
        insert_order = [i for i in range(size)]
        random.shuffle(insert_order)

        for x in insert_order:
            S.add(x)

        #check if sorted
        assert [x for x in S] == [i for i in range(size)]

        #randomize_delete_order
        delete_order = [i for i in range(size)]
        random.shuffle(delete_order)

        for x in delete_order:
            S.remove(x)

        assert not S

    @pytest.mark.large
    @pytest.mark.parametrize('size', [10000, 20000, 50000])
    def test_random_same_value(self, size: int) -> None:
        '''test: large random same input(FIXED)'''

        S: MultiSet[int] = MultiSet[int](
            operator=lambda x, y: x < y, init_e=-1)

        #insert_same_value_multiple_times
        insert_order = [1 for i in range(size)]

        for x in insert_order:
            S.add(x)

        #check if sorted
        assert [x for x in S] == [1 for i in range(size)]

        #delete_same_value_multiple_times
        delete_order = [1 for i in range(size)]

        for x in delete_order:
            S.remove(x)

        assert not S
