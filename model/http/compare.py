import json
from abc import (
    ABC,
    abstractmethod
)


class CompareABC(ABC):

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def __str__(self):
        pass


class CompareIgnore(CompareABC):
    def __eq__(self, other):
        return True

    def __str__(self):
        return 'CompareIgnore()'


class CompareIgnoreOrder(CompareABC):

    def __init__(self, seq, key):
        self.seq = seq
        self.key = key

    def __eq__(self, other: list):
        return sorted(self.seq, key=self.key) == sorted(other, key=self.key)

    def __str__(self):
        return f'CompareIgnoreOrder(seq={self.seq})'


class CompareEndswith(CompareABC):

    def __init__(self, postfix):
        self.postfix = postfix

    def __eq__(self, other: str):
        return other.endswith(self.postfix)

    def __str__(self):
        return f'CompareEndswith(postfix={self.postfix})'


class CompareDicts(CompareABC):

    def __init__(self, value):
        self.value = value

    def __eq__(self, other: dict):
        return self._to_str(self.value) == self._to_str(other)

    def __str__(self):
        return f'CompareDicts(value={self.value})'

    @staticmethod
    def _to_str(value: dict):
        return json.dumps(value, sort_keys=True, indent='\t')
