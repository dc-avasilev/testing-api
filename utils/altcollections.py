from copy import deepcopy

from deepdiff import DeepDiff


ARRAYS = (list, tuple, set)


class ExtDict(dict):
    """
    Расширение базового словаря. Новые возможности:
    - возможность доступа и добавления ключей через точечную нотацию.
        То есть можно добавить как ключ (d['key'] = 1), а можно - как атрибут:
        d.key1 = 2. Доступ после этого будет возможен как через ключ,
        так и через атрибут: d['key'] или d.key. Для тех, кому надоело писать
        скобочки и кавычки. При этом выгодное отличие от данных в виде объектов -
        сохранение плюшек словаря: методы keys и items, итератор, update и т.д.
    - поддержка операции умножения. При этом возвращается новый экземпляр
        ExtDict, у которого все значения умножены на предоставленное число.
        Удобно, когда нужно увеличить все значения в словаре на что-то одно.
        Прочие арифметические операции пока не поддерживаются за ненадобностью,
        но, может будет добавлено в будущем.
    - новый метод crop: возвращает НОВЫЙ экземпляр ExtDict,
        из которого выкинут соответствующий ключ.
        Нужно для однострочников. Метод оригинального словаря pop меняет
        исходный словарь, поэтому требуется создавать экземпляр словаря,
        потом делать в нём pop отдельной строкой, а потом уже использовать
        получившийся результат. А в ExtDict можно сделать так:
        `return cls.date_time(**ExtDict(locals()).crop('cls')`
        Здесь мы из словаря locals выкидываем ключ 'cls' и сразу же
        к получившемуся результату применяем date_time(). Это удобно,
        потому что не нужно заводить отдельную переменную вроде
        "params = locals()" - у нас автоматически создаётся копия,
        из которой при применении метода crop опять же возвращается копия.
        В случае с pop нам бы вернулось значение удаляемого ключа, что далеко
        не всегда нужно.
    - новый метод add: расширение метода update, которое позволит не изменять
        исходный словарь, а возвращать новый экземпляр с изменениями.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # All inner dictionaries will be recursively converted to ExtDict.
        for key, value in self.items():
            self[key] = value

    def __deepcopy__(self, memo):
        return self.__class__(deepcopy(dict(self), memo=memo))

    def __getattr__(self, item):
        return ExtDict.__getitem__(self, item, _called_as_attr=True)

    def __setattr__(self, key, value):
        self[key] = value

    def __getitem__(self, item, *, _called_as_attr=False):
        if item in self.keys():
            return self.get(item)
        if _called_as_attr:
            raise AttributeError(
                f"Instance of class {self.__class__.__name__} "
                f"does not have attribute '{item}'")
        else:
            raise KeyError(item)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, RecursiveConverter(value, self.__class__))

    def __mul__(self, other):
        """
        Returns new instance of ExtDict instantiated from 'self' where all
        values of root keys are multiplied on value of 'other' (not recursive).
        """
        new = self.copy()
        for key, value in new.items():
            try:
                new[key] = value * other
            except TypeError:
                raise TypeError(f"can't multiply value of key '{key}' "
                                f"by non-int of type '{type(other).__name__}'")
        return new

    def crop(self, *keys):
        """Deletes provided keys from the dictionary and returns new ExtDict."""
        new = self.copy()
        for key in keys:
            new.pop(key)
        return new

    def add(self, __m=None, /, **kwargs):
        """Return new copy of ExtDict and add provided dictionary to it."""
        new = self.copy()
        new.update(__m, **kwargs)
        return new

    def replace(self, key, value):
        """Return new copy of ExtDict and replace provided key in it."""
        new = self.copy()
        new[key] = value
        return new

    def update(self, __m=None, /, **kwargs) -> None:
        if __m:
            dict.update(self, RecursiveConverter(__m, self.__class__),
                        **RecursiveConverter(kwargs, self.__class__))
        else:
            dict.update(self, **RecursiveConverter(kwargs, self.__class__))

    def copy(self):
        """Works as copy.deepcopy()"""
        return self.__class__(self)

    def sort(self, reverse=False):
        """Return new instance and recursively sort all dictionaries keys
        and arrays inside it."""
        return RecursiveSort(self, __reverse__=reverse)


class TupleDict(ExtDict):
    """
    - добавлена возможность доступа по срезу и индексу непосредственно к значениям
        (их порядок сохраняется), то есть:
            d['key'] = 1
            d['key1'] = 2
        d[0] вернёт 1, который мы выше добавили
        d[:] вернёт кортеж (1, 2).
        У этого есть побочный эффект:
        невозможно обратиться к ключам, имеющим тип int, поскольку такие обращения
        автоматически считаются обращением по индексу. Но кто в реальной жизни
        использует словари с int в качестве ключей? Встречается редко.
        И, если встретится, всегда можно использовать обычный словарь :)
    - новый метод crop_astuple: возвращает кортеж из значений словаря,
        из которого убрано значение, соответствующее ключу словаря, переданному методу.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, item, *, _called_as_attr=False):
        if type(item) in (int, slice):
            return tuple(self.values())[item]
        else:
            return super().__getitem__(item, _called_as_attr=False)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            raise TypeError(f'Integers cannot be added as '
                            f'{self.__class__.__name__} keys')
        else:
            super().__setitem__(key, value)

    def crop_astuple(self, *keys):
        """Deletes provided keys from the dictionary and
        returns tuple of values of new TupleDict."""
        return self.crop(*keys)[:]


class ExtendedList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def crop(self, __index: int = ...):
        new = self.copy()
        new.pop(__index)
        return new

    def add(self, item):
        new = self.copy()
        new.append(item)
        return new

    def copy(self):
        return deepcopy(self)


class _RecursiveConverter:
    """Using convert() method one can convert dictionaries recursively."""

    default_destination = ExtDict

    def __init__(self):
        self.dest_class = self.default_destination

    def __call__(self, source, dest_class=default_destination):
        self.dest_class = dest_class
        return self._check_type(source)

    def _check_type(self, value):
        if hasattr(value, 'keys'):
            return self._convert_dict(value)
        elif isinstance(value, ARRAYS):
            return self._convert_array(value)
        return value

    def _convert_dict(self, dictionary):
        result = self.dest_class(dictionary)
        for key, value in result.items():
            result[key] = self._check_type(value)
        return result

    def _convert_array(self, array):
        return type(array)([self._check_type(item) for item in array])


class _RecursiveSort:
    """
    Обеспечивает рекурсивную сортировку по алфавиту сложных вложенных структур.
    Сортировке подвергаются ключи словаря и элементы последовательностей.
    Если последовательность нельзя отсортировать, она остаётся несортированной.
    На вход принимает следующие аргументы:
    - позиционные аргументы: названия ключей вложенных словарей или
        элементов последовательности, при обнаружении которых в словаре
        или последовательности соответствующая структура будет исключена из сортировки.
        Чтобы структура была исключена, в ней должны находиться все переданные элементы.
    - именованные аргументы: список пар ключ=значение, при обнаружении которых
        внутри вложенного словаря алгоритм не будет сортировать ключи этого словаря.
        Чтобы словарь был исключён, в нём должны находиться все переданные пары.
    - параметр __reverse__ (по умолчанию False): при значении True сортировка
        осуществляется в обратном порядке.
    """

    def __init__(self):
        self._exclude_items = set()
        self._exclude_pairs = []
        self._exclude_all = False
        self._reverse = False

    def __call__(self, data, *args, __reverse__=False, __exclude_all__=False):
        self._exclude_items = {x for x in args if not isinstance(x, ARRAYS)}
        self._exclude_pairs = [tuple(x) for x in args if isinstance(x, ARRAYS)]
        self._exclude_all = __exclude_all__
        self._reverse = __reverse__
        return self._check_type(data)

    def _check_type(self, value):
        if hasattr(value, 'keys'):
            return self._sort_dict(value)
        elif isinstance(value, ARRAYS):
            return self._sort_array(value)
        return value

    def _check_items_exist(self, data):
        try:
            if self._exclude_all:
                if set(data) & self._exclude_items == self._exclude_items:
                    return True
            else:
                for item in self._exclude_items:
                    if item in set(data):
                        return True
        except TypeError:
            return True
        return False

    def _check_pairs_exist(self, data):
        i = 0
        for pair in self._exclude_pairs:
            if pair in data.items():
                if not self._exclude_all:
                    return True
                i += 1
        return i > 0 and i == len(self._exclude_pairs)

    def _sort_dict(self, data):
        match = 0
        if self._check_items_exist(data):
            match += 1
        if self._check_pairs_exist(data):
            match += 1
        result = data.items()
        if (match == 0) or (self._exclude_all and match < 2):
            result = sorted(result, reverse=self._reverse)
        return type(data)(
            [(key, self._check_type(value)) for key, value in result])

    def _sort_array(self, array):
        match = False
        if self._exclude_items:
            match = self._check_items_exist(array)
        result = ([self._check_type(item) for item in array])
        if not match:
            try:
                result = sorted(result, reverse=self._reverse)
            except TypeError:
                pass
        return type(array)(result)


class DictDiff(DeepDiff):
    """Allows to compare two instances of custom dictionaries and basic dict"""

    def __init__(self, *args, **kwargs):
        if 'ignore_type_in_groups' not in kwargs:
            kwargs['ignore_type_in_groups'] = [
                (dict, ExtDict),
                (dict, TupleDict),
                (ExtDict, TupleDict)
            ]
        super().__init__(*args, **kwargs)


RecursiveConverter = _RecursiveConverter()
RecursiveSort = _RecursiveSort()
