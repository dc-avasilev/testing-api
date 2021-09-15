from random import (
    choice,
    randint
)
from uuid import uuid4

from faker import Factory
from faker.providers import BaseProvider
from faker.providers.bank.ru_RU import Provider


class ExampleDataProvider(BaseProvider):
    fake = Factory.create('ru_RU')
    letters = 'абвАБВabcABC               '
    intercom_letters = '1234567890ABC#'

    def _rand_letters(self, lenth: int) -> str:
        result = str(randint(1, lenth))
        result += choice(self.letters)
        return result.strip()

    def apartment(self) -> str:
        return self._rand_letters(3000)

    def house_number(self) -> str:
        return self._rand_letters(99)

    @staticmethod
    def entrance():
        return str(randint(1, 15))

    @staticmethod
    def floor():
        return str(randint(1, 99))

    @staticmethod
    def flat_number():
        return str(randint(1, 3000))

    def intercom_code(self):
        intercom_code = str(randint(1, 9))
        for _ in range(randint(0, 5)):
            intercom_code += choice(self.intercom_letters)
        return intercom_code

    @staticmethod
    def person_count():
        return randint(1, 7)

    @staticmethod
    def change():
        change_values = [500, 1000, 2000, 5000]
        return str(choice(change_values))


class PhoneNumber:
    def __init__(self, phone):
        self._phone = str(phone)

    def __str__(self):
        return self.formatted_view

    def __eq__(self, other):
        if isinstance(other, PhoneNumber):
            return self.plain_view == other.plain_view
        elif isinstance(other, str):
            return self.plain_view == other
        else:
            return False

    @property
    def plain_view(self):
        return self._phone

    @property
    def plain_view_with_plus(self):
        return '+' + self._phone

    @property
    def short_plain_view(self):
        if len(self.plain_view) == 11:
            return self.plain_view[1:]
        else:
            return self.plain_view

    @property
    def formatted_view(self):
        formatted_phone = '+{}({}){}-{}-{}'.format(
            self._phone[0],
            self._phone[1:4],
            self._phone[4:7],
            self._phone[7:9],
            self._phone[9:]
        )
        return formatted_phone

    @property
    def short_formatted_view(self):
        formatted_phone = '({}) {}'.format(
            self._phone[1:4],
            self._phone[4:]
        )
        return formatted_phone

    @property
    def verification_code(self):
        return self.plain_view[-4:]


class PhoneNumberProvider(BaseProvider):
    phone_codes: list[str] = ['000']

    def phone(self):
        return PhoneNumber(self.numerify(f'7{choice(self.phone_codes)}###%###'))

    def phone_custome_codes(self, custome_codes: list[str] = None):
        if custome_codes:
            return PhoneNumber(
                self.numerify(
                    f'7{choice(custome_codes)}###%###'
                )
            )
        return PhoneNumber(self.numerify(f'7{choice(self.phone_codes)}###%###'))


class UUIDProvider(BaseProvider):

    @staticmethod
    def uuid() -> str:
        return str(uuid4())

    def uuid_short_code(self) -> str:
        return self.uuid().split("-")[0]

    @staticmethod
    def uuidhex() -> str:
        return uuid4().hex


class CustomeBankProvider(Provider):

    def bik_with_len(self, length=9):
        region = self.random_element(self.region_codes)
        department_code = self.numerify(
            self.random_element(self.department_code_formats))
        credit_organization_code = self.numerify(
            self.random_element(self.credit_organization_code_formats))
        bik = '04' + region + department_code + credit_organization_code
        if len(bik) <= length:
            return bik
        return bik[:length]


def get_faker():
    fake = Factory.create('ru_RU')
    fake.add_provider(ExampleDataProvider)
    fake.add_provider(PhoneNumberProvider)
    fake.add_provider(UUIDProvider)
    fake.add_provider(CustomeBankProvider)
    return fake


def get_faker_en():
    fake = Factory.create()
    fake.add_provider(ExampleDataProvider)
    fake.add_provider(PhoneNumberProvider)
    fake.add_provider(UUIDProvider)
    return fake


class Fake:
    fake = get_faker()
    fake_en = get_faker_en()

    @classmethod
    def ru(cls):
        return cls.fake

    @classmethod
    def en(cls):
        return cls.fake_en
