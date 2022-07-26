#-*- coding: utf-8 -*-
from collections import deque
from dataclasses import dataclass, field, InitVar
from typing import Callable, Generator, Any, Generic, TypeVar


T = TypeVar('T')
U = TypeVar('U')


class Iterator(Generic[U]):
    #BLACK = 0, RED = 1
    key: U
    _par: Any = None
    _left: Any = None
    _right: Any = None
    _subtree_size: int = 1
    _color: bool = False

    def __init__(self, key: U) -> None:
        self.key = key
        self._par = self._left = self._right = None
        self._subtree_size = 1
        self._color = False  # BLACK


@dataclass
class MultiSet(Generic[T]):
    '''
    Reference: 
        Introduction to Algorithms, Third Edition
    ---
    [en]
        Python Multiset (red-black-tree.ver)

        Args:
            T        := type of element                             <ex> int, Tuple[int, str]
            operator := comp function of T(MUST BE WELL-DEFINED!)   <ex> lambda x, y: x <= y
            init_e   := sentinel key                              <ex> 1 << 64, (-1, 'nil')

        Example:
            (1)
                set : MultiSet[int] = MultiSet(operator=lambda x, y : x <= y, init_e=-1)
            (2)
                def comp(lh : Tuple[int, str], rh : Tuple[int, str]) -> bool:
                    if lh[0] != rh[0]:
                        return lh[0] < rh[0]
                    return lh[1] < rh[1]
                
                set : MultiSet[Tuple[int, str]] = MultiSet(operator=comp, init_e=(-1, 'nil'))
        Note:
            ・operator must be WELL-DEFINED (otherwise UNDEFINED)
            ・init_e must not be added.
    ---
    [ja]
        Pythonにおける順序付き集合 (赤黒木による実装)

        パラメータ:
            T        := 順序付きsetで取り扱うオブジェクトの型.            <例> int, Tuple[int, str]
            operator := オブジェクトの比較オペレータ.WELL-DEFINEDを要請   <例> lambda x, y: x <= y
            init_e   := 番兵値(nil値の代わりに用いられる).               <例> 1 << 64, (-1, 'nil')

        使用例:
            (1)
                set : MultiSet[int] = MultiSet(operator=lambda x, y : x <= y, init_e=-1)
            (2)
                def comp(lh : Tuple[int, str], rh : Tuple[int, str]) -> bool:
                    if lh[0] != rh[0]:
                        return lh[0] < rh[0]
                    return lh[1] < rh[1]
                
                set : MultiSet[Tuple[int, str]] = MultiSet(operator=comp, init_e=(-1, 'nil'))

        注意:
            ・operator がWELL-DEFINEDでない場合の動作は未定義.
            ・init_e が要素として追加されることがあってはいけない.
    '''
    operator: InitVar[Callable[[T, T], bool]]
    init_e: InitVar[T]

    _root: Iterator[T] = field(init=False)
    _nil: Iterator[T] = field(init=False)
    _nilval: T = field(init=False)
    _op: Callable[[T, T], bool] = field(init=False)
    _size: int = 0

    def __post_init__(self, operator: Callable[[T, T], bool], init_e: T) -> None:
        self._op = (operator if operator(init_e, init_e)
                    else lambda x, y: not operator(y, x))
        self._nilval = init_e

        self._nil = Iterator[T](self._nilval)
        self._nil._subtree_size = 0

        self._root = self._nil
        self._root._par = self._root._left = self._root._right = self._nil

    def __bool__(self) -> bool:
        return self._size > 0

    def __contains__(self, x: T) -> bool:
        ptr, op = self._root, self._op
        while ptr != self._nil and ptr.key != x:
            if op(x, ptr.key):
                ptr = ptr._left
            else:
                ptr = ptr._right
        return ptr.key == x

    def __getitem__(self, k: int) -> T:
        assert type(k) == int
        if k < 0:
            k += self._size
        if k < 0 or k >= self._size:
            raise IndexError
        return self.__kth_element(k + 1)

    def __iter__(self) -> Generator[T, None, None]:
        if self._size == 0:
            return
        que = deque([(self._root, False)])
        while que:
            u, trace_back = que.pop()
            if not trace_back:
                que.append((u, True))
                if (ul := u._left) != self._nil:
                    que.append((ul, False))
            else:
                if (ur := u._right) != self._nil:
                    que.append((ur, False))
                yield u.key

    def __len__(self) -> int:
        return self._size

    @property
    def e(self) -> T:
        '''init_e in O(1)'''
        return self._nilval

    @property
    def max(self) -> T:
        '''max-element in O(log)'''
        ptr = self._root
        while (pr := ptr._right) != self._nil:
            ptr = pr
        return ptr.key

    @property
    def min(self) -> T:
        '''min-element in O(log)'''
        ptr = self._root
        while (pl := ptr._left) != self._nil:
            ptr = pl
        return ptr.key

    def clear(self) -> None:
        '''clear the MultiSet in O(1)'''
        self._root = self._nil
        self._size = self._root._subtree_size
        self._root._par = self._root._left = self._root._right = self._nil

    def find_address(self, val: T) -> Iterator[T]:
        '''the Iterator of given val in O(log)'''
        ptr, op = self._root, self._op
        while ptr != self._nil and val != ptr.key:
            if op(val, ptr.key):
                ptr = ptr._left
            else:
                ptr = ptr._right
        return ptr

    def less_than(self, x: T) -> int:
        '''the number of elements between [-∞, x) in O(log)'''
        if self._size == 0:
            return 0
        count, ptr, op = 0, self._root, self._op
        while ptr != self._nil:
            if op(x, ptr.key):
                ptr = ptr._left
            else:
                count += 1 + ptr._left._subtree_size
                ptr = ptr._right
        return count

    def between(self, left_x: T, right_x: T) -> int:
        '''the number of elements between [left_x, right_x) in O(log)'''
        if not self._op(left_x, right_x):
            return 0
        return self.less_than(right_x) - self.less_than(left_x)

    def prev_element(self, x: T) -> T:
        ''' the largest element smaller than x in O(log)
            if no such key found, return init_e
        '''
        if self._size == 0:
            return self._nilval
        ptr, retval, op = self._root, self._nilval, self._op
        while ptr != self._nil:
            if op(x, ptr.key):
                ptr = ptr._left
            else:
                retval, ptr = ptr.key, ptr._right
        return retval

    def next_element(self, x: T) -> T:
        ''' the smallest element larger than x in O(log)
            if no such key found, return init_e
        '''
        if self._size == 0:
            return self._nilval
        ptr, retval, op = self._root, self._nilval, self._op
        while ptr != self._nil:
            if op(ptr.key, x):
                ptr = ptr._right
            else:
                retval, ptr = ptr.key, ptr._left
        return retval

    def add(self, x: T) -> None:
        '''add x into set in O(log)'''
        self._size += 1
        z, y, v, op = self._root, self._nil, Iterator[T](x), self._op

        while z != self._nil:
            y = z
            z._subtree_size += 1
            if not op(z.key, x):
                z = z._left
            else:
                z = z._right

        v._par = y

        if y == self._nil:
            self._root = v
        elif not op(y.key, x):
            y._left = v
        else:
            y._right = v

        v._color, v._left, v._right = True, self._nil, self._nil

        self.__fix_up_insert(v)

    def remove(self, x: T) -> None:
        '''remove x from set in O(log)'''
        z = self.find_address(x)

        assert z != self._nil, KeyError
        self._size -= 1
        y, y_original_color = z, z._color

        if z._left == self._nil:
            p, q = z, z._right
            while p != self._nil:
                p._subtree_size -= 1
                p = p._par
            self.__transplant(z, q)

        elif z._right == self._nil:
            p, q = z, z._left
            while p != self._nil:
                p._subtree_size -= 1
                p = p._par
            self.__transplant(z, q)

        else:
            y = z._right
            while (yl := y._left) != self._nil:
                y = yl

            p = y
            while p != self._nil:
                p._subtree_size -= 1
                p = p._par

            y._subtree_size, y_original_color, q = z._subtree_size, y._color, y._right

            if y._par == z:
                q._par = y
            else:
                self.__transplant(y, y._right)
                zr = z._right
                y._right, zr._par = zr, y

            self.__transplant(z, y)
            zl = z._left
            y._left, zl._par = zl, y
            y._color = z._color

        if not y_original_color:
            self.__fix_up_delete(q)

    def __kth_element(self, k: int) -> T:
        '''return k-th(1-indexed) smallest element in O(log)'''
        assert type(k) == int
        assert 1 <= k <= self._size, IndexError
        ptr = self._root

        while ptr != self._nil:
            lsize = ptr._left._subtree_size + 1
            if k == lsize:
                return ptr.key
            elif k < lsize:
                ptr = ptr._left
            else:
                k -= lsize
                ptr = ptr._right

        assert False  # This line should be unreachable...

    def __rotate_left(self, x: Iterator[T]) -> None:
        y = x._right
        x._right = y._left
        if (yl := y._left) != self._nil:
            yl._par = x
        y._par = x._par
        if x._par == self._nil:
            self._root = y
        elif x == (xp := x._par)._left:
            xp._left = y
        else:
            xp._right = y

        y._left, x._par = x, y

        y._subtree_size = x._subtree_size
        x._subtree_size = x._left._subtree_size + \
            x._right._subtree_size + 1

    def __rotate_right(self, x: Iterator[T]) -> None:
        y = x._left
        x._left = y._right
        if (yr := y._right) != self._nil:
            yr._par = x
        y._par = x._par
        if x._par == self._nil:
            self._root = y
        elif x == (xp := x._par)._right:
            xp._right = y
        else:
            xp._left = y

        y._right, x._par = x, y

        y._subtree_size = x._subtree_size
        x._subtree_size = x._left._subtree_size + \
            x._right._subtree_size + 1

    def __fix_up_insert(self, z: Iterator[T]) -> None:

        while (zp := z._par)._color:

            if zp == (zpp := zp._par)._left:
                y = zpp._right
                if y._color:
                    zp._color, y._color, zpp._color = \
                        False, False, True
                    z = zpp
                else:
                    if z == zp._right:
                        z = zp
                        self.__rotate_left(z)
                    zp = z._par
                    zpp = zp._par
                    zp._color, zpp._color = False, True
                    self.__rotate_right(zpp)

            else:
                y = (zpp := zp._par)._left
                if y._color:
                    zp._color, y._color, zpp._color = \
                        False, False, True
                    z = zpp
                else:
                    if z == zp._left:
                        z = zp
                        self.__rotate_right(z)
                    zp = z._par
                    zpp = zp._par
                    zp._color, zpp._color = False, True
                    self.__rotate_left(zpp)

        self._root._color = False

    def __transplant(self, u: Iterator[T], v: Iterator[T]) -> None:
        if (up := u._par) == self._nil:
            self._root = v
        elif u == up._left:
            up._left = v
        else:
            up._right = v
        v._par = up

    def __fix_up_delete(self, x: Iterator[T]) -> None:
        while x != self._root and not x._color:
            if x == (xp := x._par)._left:
                w = xp._right
                if w._color:
                    w._color, xp._color = False, True
                    self.__rotate_left(xp)
                    w = xp._right
                if not (wr := w._right)._color and not (wl := w._left)._color:
                    w._color = True
                    x = xp
                else:
                    if not wr._color:
                        wl._color, w._color = False, True
                        self.__rotate_right(w)
                        w = xp._right
                    w._color, xp._color, w._right._color = xp._color, False, False
                    self.__rotate_left(xp)
                    x = self._root
            else:
                w = xp._left
                if w._color:
                    w._color, xp._color = False, True
                    self.__rotate_right(xp)
                    w = xp._left
                if not (wl := w._left)._color and not (wr := w._right)._color:
                    w._color = True
                    x = xp
                else:
                    if not wl._color:
                        wr._color, w._color = False, True
                        self.__rotate_left(w)
                        w = xp._left
                    w._color, xp._color, w._left._color = xp._color, False, False
                    self.__rotate_right(xp)
                    x = self._root

        x._color = False
