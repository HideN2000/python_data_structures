#-*- coding: utf-8 -*-
from collections import deque
from dataclasses import dataclass, field, InitVar
from typing import Callable, Generator, Any, Generic, TypeVar


T = TypeVar('T')
U = TypeVar('U')


@dataclass
class TreeNode(Generic[U]):
    #BLACK = 0, RED = 1
    value: U
    _par: Any = None
    _left: Any = None
    _right: Any = None
    _subtree_size: int = 1
    _color: bool = False


@dataclass
class MultiSet(Generic[T]):
    '''
    Reference: 
        Introduction to Algorithms, Third Edition

    Python Multiset (red-black-tree.ver)

    Args:
        T        := type of element                             <ex> int, Tuple[int, str]
        operator := comp function of T(MUST BE WELL-DEFINED!)   <ex> lambda x, y: x <= y
        init_e   := sentinel value                              <ex> 1 << 64, (-1, 'nil')

    Example:
        (1)
            set : MultiSet[int] = MultiSet(operator = lambda x, y : x <= y, init_e = -1)
        (2)
            def comp(lh : Tuple[int, str], rh : Tuple[int, str]) -> bool:
                if lh[0] != rh[0]:
                    return lh[0] < rh[0]
                return lh[1] < rh[1]
            
            set : MultiSet[Tuple[int, str]] = MultiSet(operator = comp, init_e = (-1, 'nil'))
    '''
    operator: InitVar[Callable[[T, T], bool]]
    init_e: InitVar[T]

    _root: TreeNode[T] = field(init=False)
    _nil: TreeNode[T] = field(init=False)
    _nilval: T = field(init=False)
    _op: Callable[[T, T], bool] = field(init=False)
    _size: int = 0

    def __post_init__(self, operator: Callable[[T, T], bool], init_e: T) -> None:
        self._op = operator
        self._nilval = init_e

        self._nil = TreeNode[T](self._nilval)
        self._nil._subtree_size = 0

        self._root = self._nil
        self._root._par = self._root._left = self._root._right = self._nil

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
                yield u.value

    def __getitem__(self, k: int) -> T:
        #return S[k] := k-th smallest element
        assert type(k) == int
        if k < 0:
            k += self._size
        if k < 0 or k >= self._size:
            raise IndexError
        return self.kth_element(k + 1)

    @property
    def e(self) -> T:
        '''return init_e in O(1)'''
        return self._nilval

    @property
    def size(self) -> int:
        '''return set size in O(1)'''
        return self._size

    @property
    def empty(self) -> bool:
        '''return set is empty in O(1)'''
        return self._size == 0

    def __find_address(self, val: T) -> TreeNode[T]:
        ptr, op = self._root, self._op
        while ptr != self._nil and val != ptr.value:
            if op(val, ptr.value):
                ptr = ptr._left
            else:
                ptr = ptr._right
        return ptr

    def find(self, x: T) -> bool:
        '''return (if x in set) in O(log)'''
        ptr, op = self._root, self._op
        while ptr != self._nil and ptr.value != x:
            if op(x, ptr.value):
                ptr = ptr._left
            else:
                ptr = ptr._right
        return ptr.value == x

    @property
    def min(self) -> T:
        '''return min-element in O(log)'''
        ptr = self._root
        while (pl := ptr._left) != self._nil:
            ptr = pl
        return ptr.value

    @property
    def max(self) -> T:
        '''return max-element in O(log)'''
        ptr = self._root
        while (pr := ptr._right) != self._nil:
            ptr = pr
        return ptr.value

    def kth_element(self, k: int) -> T:
        '''return k-th(1-indexed) smallest element in O(log)'''
        assert type(k) == int
        assert 1 <= k <= self._size, IndexError
        ptr = self._root

        while ptr != self._nil:
            lsize = ptr._left._subtree_size + 1
            if k == lsize:
                return ptr.value
            elif k < lsize:
                ptr = ptr._left
            else:
                k -= lsize
                ptr = ptr._right
        raise NotImplementedError
        #IMPLEMENT ERROR

    def count_less_than(self, x: T) -> int:
        '''return the number of elements between [-∞, x) in O(log)'''
        if self._size == 0:
            return 0
        count, ptr, op = 0, self._root, self._op
        while ptr != self._nil:
            if op(x, ptr.value):
                ptr = ptr._left
            else:
                count += 1 + ptr._left._subtree_size
                ptr = ptr._right
        return count

    def count_range(self, left_x: T, right_x: T) -> int:
        '''return the number of X between [left_x, right_x) in O(log)'''
        if not self._op(left_x, right_x):
            return 0
        return self.count_less_than(right_x) - self.count_less_than(left_x)

    def prev_element(self, x: T) -> T:
        ''' return the largest element which are smaller than x in O(log)
            if no such value found, return init_e
        '''
        if self._size == 0:
            return self._nilval
        ptr, retval, op = self._root, self._nilval, self._op
        while ptr != self._nil:
            if op(x, ptr.value):
                ptr = ptr._left
            else:
                retval, ptr = ptr.value, ptr._right
        return retval

    def next_element(self, x: T) -> T:
        ''' return the smallest element are larger than x in O(log)
            if no such value found, return init_e
        '''
        if self._size == 0:
            return self._nilval
        ptr, retval, op = self._root, self._nilval, self._op
        while ptr != self._nil:
            if op(ptr.value, x):
                ptr = ptr._right
            else:
                retval, ptr = ptr.value, ptr._left
        return retval

    def insert(self, x: T) -> None:
        '''insert (x) into set in O(log)'''
        self._size += 1
        z, y, v, op = self._root, self._nil, TreeNode[T](x), self._op

        while z != self._nil:
            y = z
            z._subtree_size += 1
            if not op(z.value, x):
                z = z._left
            else:
                z = z._right

        v._par = y

        if y == self._nil:
            self._root = v
        elif not op(y.value, x):
            y._left = v
        else:
            y._right = v

        v._color, v._left, v._right = True, self._nil, self._nil

        self.__fix_up_insert(v)

    def delete(self, x: T) -> None:
        '''erase (x) from set in O(log)'''
        z = self.__find_address(x)

        assert z != self._nil, ValueError
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

    def __rotate_left(self, x: TreeNode[T]) -> None:
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

    def __rotate_right(self, x: TreeNode[T]) -> None:
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

    def __fix_up_insert(self, z: TreeNode[T]) -> None:

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

    def __transplant(self, u: TreeNode[T], v: TreeNode[T]) -> None:
        if (up := u._par) == self._nil:
            self._root = v
        elif u == up._left:
            up._left = v
        else:
            up._right = v
        v._par = up

    def __fix_up_delete(self, x: TreeNode[T]) -> None:
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
