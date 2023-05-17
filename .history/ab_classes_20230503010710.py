from collections import UserDict
from datetime import datetime
from itertools import islice
import pickle
import re


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self.value)

    def __eq__(self, other):
        return self.value == other.value


class Note:
    def __init__(self, text, tag=None, done=False):
        self.day = datetime.today()
        self.done = done
        self.done_date = None
        self.text = text
        self.tag_list = [tag] if tag else []

    def add_tag(self, tag):
        if tag not in self.tag_list:
            self.tag_list.append(tag)
            self.tag_list.sort()

    def __repr__(self) -> str:
        return str(self.text)

    def __eq__(self, other):
        return self.text == other.text


class HashTag:
    def __init__(self, tag) -> None:
        if "#" in tag:
            self.text = tag
        else:
            self.text = "#" + tag

    def __repr__(self) -> str:
        return self.text

    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text


class NotePad:
    def load_from_file(self, note_file):
        try:
            with open(note_file, "rb") as db:
                self.note_list = pickle.load(db)
        except EOFError:
            pass

    def save_to_file(self, note_file):
        with open(note_file, "wb") as db:
            pickle.dump(self.note_list, db)

    note_list = []

    def add_note(self, note):
        i = 0
        for rec in self.note_list:
            if len(note.tag_list) <= len(rec.tag_list):
                i = self.note_list.index(rec) + 1
        self.note_list.insert(i, note)

    def change_note(self, note, new_note):
        for rec in self.note_list:
            if str(note) == str(rec):
                rec.text = new_note

    def change_status(self, note):
        for rec in self.note_list:
            if note == rec:
                rec.done = True
                rec.done_date = datetime.today().date()

    def delete(self, note):
        self.note_list.remove(note)

    def sorting(self):
        self.note_list.sort(key=lambda note: len(note.tag_list), reverse=True)


class Name(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if not (value.isnumeric() or len(value) < 2):  # Name validation
            self.__value = value
        else:
            raise ValueError(
                "Ім'я не може складатись тільки з цифр та мінімальна довжина імені 2 символа."
            )


class Birthday(Field):
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        try:
            self._value = datetime.strptime(value, "%d.%m.%Y")  # Date validaiton "."
        except ValueError:
            try:
                self._value = datetime.strptime(
                    value, "%d/%m/%Y"
                )  # Date validaiton "/"
            except ValueError:
                raise ValueError("використовуйте формат дати ДД.ММ.РРРР або ДД/ММ/РРРР")

    def __str__(self) -> str:
        return datetime.strftime(self._value, "%d.%m.%Y")


class Email(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        pattern = (
            # Email validation
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        if re.match(pattern, value):
            self.__value = value
        else:
            raise ValueError("Невірний формат e-mail")


class Address(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class Phone(Field):
    min_len = 8
    max_len = 13

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, number):
        number = re.sub("\D+", "", number)
        if len(number) == 12:
            number = "+" + number
        elif len(number) == 10:
            number = "+38" + number
        elif len(number) == 9:
            number = "+380" + number
        else:
            raise ValueError(
                f"\nВи ввели невірний формат номера.\n Спробуйте знову!\n Мінімальна к-сть символів:{Phone.min_len}.\n Максимальна:{Phone.max_len}."
            )

        self.__value = number


class Record:
    def __init__(
        self,
        name: Name,
        phone: Phone = None,
        email: Email = None,
        adress: Address = None,
        birthday: Birthday = None,
    ):
        self.name = name
        self.phones = []
        if phone:
            self.phones.append(phone)
        self.birthday = birthday
        self.email = email
        self.adress = adress

    def __str__(self):
        line = "{}: Телефони: {}; E-mail: {}; Дата народження: {}; Адреса: {} \n"
        return line.format(
            self.name,
            ", ".join([str(phone) for phone in self.phones]),
            self.email,
            self.birthday,
            self.adress,
        )

    def __repr__(self):
        line = "{}: Телефони: {}; E-mail: {}; Дата народження: {}; Адреса: {} \n"
        return line.format(
            self.name,
            ", ".join([str(phone) for phone in self.phones]),
            self.email,
            self.birthday,
            self.adress,
        )

    def days_to_birthday(self) -> int:
        if not self.birthday:
            return 1000000
        today = datetime.today()
        compare = self.birthday.value.replace(year=today.year)
        days = int((compare - today).days)
        if days >= 0:
            return days
        else:
            days = int((compare.replace(year=today.year + 1) - today).days)
            return days

    def add_email(self, email: Email):
        if not self.email:
            self.email = email
        else:
            raise IndexError("E-mail вже введений")

    def add_phone(self, phone: Phone):
        if phone in self.phones:
            raise IndexError("Цей номер телефону вже існує")
        self.phones.append(phone)

    def add_adress(self, adres: Address):
        if not self.adress:
            self.adress = adres
        else:
            raise IndexError("Адреса вже введена")

    def add_birthday(self, birthday: Birthday):
        if not self.birthday:
            self.birthday = birthday
        else:
            raise IndexError("День народження вже введений")

    def show_phones(self):
        if not self.phones:
            return "В цього контакта не має телефонів"
        elif len(self.phones) == 1:
            return f"Поточний номер телефону {self.phones[0]}"
        else:
            output = "В цього контакта декілька телефонів:\n"
            for i, phone in enumerate(self.phones, 1):
                output += f"{i}: {phone} "
            return output

    def change_email(self, email: str):
        self.email = Email(email)

    def show_email(self):
        if not self.email:
            return "В цього контакта немає e-mail"
        else:
            return f"Поточний e-mail {self.email}"

    def change_birthday(self, new_birthday: Birthday):
        if not self.birthday:
            raise IndexError("Дата народження ще не введена")
        self.birthday = new_birthday

    def change_address(self, new_address: Address):
        if not self.adress:
            self.adress = new_address
            return f"Додано адресу {new_address}"
        else:
            old_address = self.adress
            self.adress = new_address
            return f"Змінено адресу з {old_address} на {new_address}"

    def del_phone(self, num=1):
        if not self.phones:
            raise IndexError("В цього контакта не має збережених телефонів")
        else:
            return self.phones.pop(num - 1)

    def edit_phone(self, phone_new: Phone, num=1):
        if not self.phones:
            raise IndexError("В цього контакта не має збережених телефонів")
        else:
            self.phones.pop(num - 1)
            self.phones.insert(num - 1, phone_new)


class AddressBook(UserDict):
    def load_from_file(self, filename):
        try:
            with open(filename, "rb") as db:
                self.data = pickle.load(db)
        except EOFError:
            pass

    def save_to_file(self, filename):
        with open(filename, "wb") as db:
            pickle.dump(self.data, db)

    def add_record(self, record: Record):
        self.data.update({record.name.value: record})

    def remove_record(self, contact: str):
        return self.data.pop(contact)

    def lening(self):
        return len(self.data)

    def iterator(self, page):
        start = 0
        while True:
            output = ""
            for i in islice(self.data.values(), start, start + page):
                output += str(i)
            if not output:
                break
            yield output
            start += page

    def show_all(self):
        output = ""
        for contact in self.data.values():
            output += str(contact)
        output += f"Всього: {len(self.data)} контактів."
        return output

    def search(self, pattern: str) -> list:
        found_recs = []
        for contact in self.data.values():
            if pattern in str(contact):
                found_recs.append(contact)
        return found_recs
