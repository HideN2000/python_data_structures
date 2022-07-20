#-*- coding: utf-8 -*-
import os
import pytest
import sys
import time
from typing import Generator


@pytest.fixture(autouse=True, scope='session')
def add_include_path() -> None:
    '''add pwd to sys.path'''
    INCLUDE_PATH = os.path.abspath("..")
    sys.path.append(INCLUDE_PATH)


@pytest.fixture(autouse=True, scope='session')
def footer_session_scope() -> Generator[None, None, None]:
    '''report the time at the end of aa session'''
    yield
    now = time.time()
    print('-'*10)
    print(f'finished : {time.strftime("%d %b %X", time.localtime(now))}')
    print('-'*10)


@pytest.fixture(autouse=True)
def footer_function_scope() -> Generator[None, None, None]:
    '''report execute durations after each funciton.'''
    start = time.time()
    yield
    end = time.time()
    delta = (end - start) * 1000
    print(f'\ntest duaration : {round(delta, 3)} (ms)')
