#-*- coding: utf-8 -*-
import os
import pytest
import random
import sys
from string import ascii_lowercase
from typing import Tuple, List

PARENT_PATH = os.path.abspath("..")
sys.path.append(PARENT_PATH)

from src.data_structure.set.multiset import MultiSet


@pytest.mark.small_case
def test_insert_delete_all() -> None:
    '''test: basic multiset example'''
    S: MultiSet[int] = MultiSet[int](
        operator=lambda x, y: x <= y, init_e=1 << 60)

    #insert from 1 to 5
    insert_order = [5, 3, 1, 2, 4]
    delete_order = [1, 4, 2, 5, 3]

    #insert
    for x in insert_order:
        S.insert(x)

    #test basic attribute
    assert S.size == S.max == 5
    assert S.min == 1
    assert [x for x in S] == [i for i in range(1, 5 + 1)]

    #delete
    for x in delete_order:
        S.delete(x)

    assert S.empty
    assert S.min == S.max == S.e


@pytest.mark.small_case
def test_erase_non_exisent_element() -> None:
    '''test: erase non-existent element from MultiSet'''

    S: MultiSet[Tuple[int, str]] = MultiSet[Tuple[int, str]](
        operator=lambda x, y: x <= y, init_e=(1 << 60, 'nil'))

    for i, char in enumerate(ascii_lowercase):
        S.insert((i, char))

    for i, char in enumerate(ascii_lowercase):
        S.delete((i, char))

    #remove from empty S
    with pytest.raises(AssertionError):
        S.delete((-1, 'non-existent-element'))


@pytest.mark.small_case
def test_random_operate() -> None:
    '''test: insert or delete elements in random_order'''
    S: MultiSet[int] = MultiSet[int](operator= lambda x, y : x < y, init_e=-1)

    size = 100
    #randomized_insert_order
    insert_order = [i for i in range(size)]
    random.shuffle(insert_order)

    for x in insert_order:
        S.insert(x)

    #check if sorted
    assert [x for x in S] == [i for i in range(size)]

    #randomize_delete_order
    delete_order = [i for i in range(size)]
    random.shuffle(delete_order)

    for x in delete_order:
        S.delete(x)

    assert S.empty


@pytest.mark.small_case
def test_kth_element() -> None:
    '''test kth element of S'''
    size = 100
    S_elements : List[int] = []
    S = MultiSet[int](operator=lambda x, y: x <= y, init_e=-1)

    #randomized_insert_order
    insert_order = [i for i in range(size)]
    random.shuffle(insert_order)

    for x in insert_order:
        S.insert(x)
        S_elements = sorted(S_elements + [x])
        assert S.size == len(S_elements)
        #test kth element
        for i in range(S.size):
            assert S.kth_element(i + 1) == S_elements[i]

    #randomized_delete_order
    delete_order = [i for i in range(size)]
    random.shuffle(delete_order)
    for x in delete_order:
        S.delete(x)
        S_elements.remove(x)
        S_elements.sort()
        assert S.size == len(S_elements)
        #test kth element
        for i in range(S.size):
            assert S.kth_element(i + 1) == S_elements[i]


@pytest.mark.xfail()
def test_ill_defined_operator() -> None:
    '''test ill_defined operator func (FAIL)'''
    size = 100
    #ill-defined operator
    S = MultiSet[int](operator=lambda x, y: x // size <= y // size, init_e=-1)

    #randomized_insert_order
    insert_order = [i for i in range(size)]
    random.shuffle(insert_order)

    for x in S:
        S.insert(x)
    
    #not sorted because of ill-defined operator 
    assert [x for x in S] == [i for i in range(size)]
