from math import *


WIDTH, HEIGHT = 1920, 1080


class Point2d:
    def __init__(self, x : int, y : int):
        if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:
            self._x = x
            self._y = y
        else:
            raise ValueError('точка за пределами экрана!')
    
    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, val: int) -> None:
        if isinstance(val, int):
            if 0 <= val <= WIDTH:
                self._x = val
            else:
                raise ValueError('точка за пределами экрана!')
        else:
            raise TypeError

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, val: int) -> None:
        if isinstance(val, int):
            if 0 <= val <= HEIGHT:
                self._y = val
            else:
                raise ValueError('точка за пределами экрана!')
        else:
            raise TypeError
    
    def __eq__(self, other) -> bool:
        if self._x == other._x and self._y == other._y:
            return True
        return False
    
    def __repr__(self) -> str:
        return f'(x = {self._x};\ty = {self._y})'
    
    def __str__(self) -> str:
        return f'point : ({self._x}, {self._y})'


class Vector2d:
    def __init__(self, x : float = None, y : float = None):
        if x and y:
            self._x = x
            self._y = y
    
    @classmethod
    def from_points_constr(cls, start : Point2d = None, end : Point2d = None) -> 'Vector2d':
            return Vector2d(end._x - start._x, end._y - start._y)

    
    def __get_item__(self, index) -> float:
        if index == 0:
            return self._x
        if index == 1:
            return self._y
        raise IndexError('в векторе нет столько значений!')
    
    def _set_item_(self, index, value):
        if index == 0:
            self._x = value
        if index == 1:
            self._y = value
        raise IndexError('в векторе нет столько значений!')
    
    def __iter__(self):
        self._index = 0
        return self
    
    def __next__(self):
        if self._index < 2:
            item = self.__get_item__(self._index)
            self._index += 1
            return item
        else:
            raise StopIteration
        
    def __eq__(self, other):
        if abs(self._x / other._x - self._y / other._y) < 2e-10:
            return True
        return False
    
    def __repr__(self) -> str:
        return f'x = {self._x}; y = {self._y})'
    
    def __str__(self) -> str:
        return f'vector : ({self._x}, {self._y})'
    
    def __abs__(self) -> float:
        return sqrt(self._x ** 2 + self._y ** 2)
    
    def __add__(self, other) -> 'Vector2d':
        return Vector2d(x = self._x + other._x, y = self._y + other._y)

    def __sub__(self, other) -> 'Vector2d':
        return Vector2d(x = self._x - other._x, y = self._y - other._y)

    def __mul__(self, num : int) -> 'Vector2d':
        return Vector2d(x = num * self._x, y = num * self._y)
    
    def __truediv__(self, num : int) -> 'Vector2d':
        if num != 0:
            return Vector2d(x = num / self._x, y = num / self._y)
        raise ZeroDivisionError('деление на 0!')
    
    def __scalar_mul__(self, other) -> float:
        return self._x * other._x + self._y * other._y
    
    @staticmethod
    def scalar_mul(vec1 : 'Vector2d', vec2 : 'Vector2d') -> float:
        return vec1._x * vec2._x + vec1._y * vec2._y
    
    def __vec_mul__(self, other) -> float:
        return self._x * other._y - self._y * other._x
    
    @staticmethod
    def vec_mul(vec1, vec2) -> float:
        return vec1._x * vec2._y - vec1._y * vec2._x
    
    def __cross_mul__(self, other1, other2) -> float:
        return self.__abs__() * other1.__vec_mul__(other2)
    
    @staticmethod
    def cross_mul(vec1, vec2, vec3) -> int:
        return abs(vec1) * Vector2d.vec_mul(vec2, vec3)

if __name__ == '__main__':
    point1 = Point2d(30, 40)
    point2 = Point2d(80, 20)
    point2.x = 100
    # point3 = Point2d(2000, 4000)
    vec1 = Vector2d.from_points_constr(Point2d(6, 5), Point2d(2, 2))
    vec2 = Vector2d(-1, 4)
    vec3 = Vector2d.from_points_constr(point1, point2)
    
    print(point1)
    print(point2)
    print(point1 == point2)
    print(repr(point1))
    print()

    print([(vec1, abs(vec1)), (vec2, abs(vec2)), (vec3, abs(vec3))], end = '\n')
    print(vec1 == vec2)
    print(vec1 + vec2)
    print(vec1 - vec2)
    print(vec1 * 3)
    print(vec1 / 3)
    print()

    # статически
    print(vec1.__scalar_mul__(vec2))
    print(vec1.__vec_mul__(vec2))
    print(vec1.__cross_mul__(vec2, vec3))
    print()
    # инстансом
    print(Vector2d.scalar_mul(vec1, vec2))
    print(Vector2d.vec_mul(vec1, vec2))
    print(Vector2d.cross_mul(vec1, vec2, vec3))
