from ab_classes import Name, Phone, Email, Birthday, Record, AddressBook, Adress
from functools import wraps
import json
from pathlib import Path
import re
import sort_folder


PAGE = 10
db_file_name = ""


def input_error(func):
    @wraps(func)
    def wrapper(*args):
        try:
            result = func(*args)
            return result

        except TypeError as err:
            if func.__name__ == "add" or func.__name__ == "change":
                message = "Введіть ім'я та номер телефону будь ласка. мінімальна довжина номеру телефону {} цифр. Максимальна {}. Літери не дозволяються"
                return message.format(Phone.min_len, Phone.max_len)
            if func.__name__ == "add_birthday":
                return "введіть ім'я та день народження"
            if func.__name__ == "add_email":
                return "введіть ім'я та e-mail"
            return err

        except AttributeError:
            return "Введіть ім'я контакту, або такий контакт не існує"

        except ValueError as err:
            return err

        except IndexError as err:
            return err

    return wrapper


@input_error
def greet(*args):
    return "Вітаню, чим можу допомогти?"


@input_error
def add(book: AddressBook, contact: str, phone: str = None):
    contact_new = Name(contact)
    phone_new = Phone(phone) if phone else None
    rec_new = Record(contact_new, phone_new)

    if contact_new.value not in book.keys():
        book.add_record(rec_new)
        return f'Додано контакт "{contact}" з телефоном: {phone}'
    else:
        book.get(contact_new.value).add_phone(phone_new)
        return f'Для існуючого контакту "{contact}" додано номер телефону: {phone}'


@input_error
def add_adress(book: AddressBook, contact: str, *adress):
    x = " ".join(adress)
    adress_new = Adress(x)
    rec = book.get(contact)
    rec.add_adress(adress_new)
    return f'Для існуючого контакту "{contact}" додано адресу: {x}'


@input_error
def add_email(book: AddressBook, contact: str, email: str):
    email_new = Email(email)
    rec = book.get(contact)
    rec.add_email(email_new)
    return f'Для існуючого контакту "{contact}" додано e-mail: {email}'


@input_error
def add_birthday(book: AddressBook, contact: str, birthday: str):
    b_day = Birthday(birthday)
    rec = book.get(contact)
    rec.add_birthday(b_day)
    return f'Для існуючого контакту "{contact}" додано день народження: {b_day}'


@input_error
def congrat(book: AddressBook, days: int):
    if days == "":
        raise ValueError("Введіть число днів")
    output = ""
    for contact in book.values():
        if contact.days_to_birthday() <= int(days):
            output += str(contact)
    text = (
        f"день народження у наступних контактів:\n{output}"
        if output
        else "ні в кого з контактів не має дня народження"
    )
    return f"В період наступних {days} днів {text}"


@input_error
def change(
    book: AddressBook,
    contact: str,
    phone: str = None,
):
    rec = book.get(contact)

    print(rec.show_phones())

    if not rec.phones:
        if not phone:
            phone_new = Phone(input("Якщо хочете додати телефон введіть номер:"))
        else:
            phone_new = Phone(phone)
        rec.add_phone(phone_new)
        return f'Змінено номер телефону на {phone_new} для контакту "{contact}"'

    else:
        if len(rec.phones) == 1:
            num = 1
        if len(rec.phones) > 1:
            num = int(input("Який ви хочете змінити (введіть індекс):"))
        if not phone:
            phone_new = Phone(input("Будь ласка введіть новий номер:"))
        else:
            phone_new = Phone(phone)
        old_phone = rec.phones[num - 1]
        rec.edit_phone(phone_new, num)
        return f'Змінено номер телефону {old_phone} на {phone_new} для контакту "{contact}"'


@input_error
def del_phone(book: AddressBook, contact: str, phone=None):
    rec = book.get(contact)

    if phone:
        for i, p in enumerate(rec.phones):
            if p == phone:
                num = i + 1
        else:
            raise ValueError("Цей контакт не має такого номеру телефону")
    else:
        print(rec.show_phones())
        if len(rec.phones) == 1:
            num = 1
            ans = None
            while ans != "y":
                ans = input(
                    f"Контакт {rec.name} має тільки 1 телефон {rec.phones[0]}.\
                        Ви впевнені? (Y/N)"
                ).lower()
        else:
            num = int(input("який ви хочете видалити (введіть індекс):"))
    return f"Телефон {rec.del_phone(num)} видалено!"


@input_error
def del_email(book: AddressBook, *args):
    contact = " ".join(args)
    rec = book.get(contact)
    rec.email = None
    return f"Контакт {contact}, e-mail видалено"


@input_error
def del_contact(book: AddressBook, *args):
    contact = " ".join(args)
    rec = book.get(contact)
    if not rec:
        raise AttributeError
    ans = None
    while ans != "y":
        ans = input(f"Are you sure to delete contact {contact}? (Y/N)").lower()
    return f"Контакт {book.remove_record(contact)} Видалено!"


@input_error
def del_birthday(book: AddressBook, *args):
    contact = " ".join(args)
    rec = book.get(contact)
    rec.birthday = None
    return f"Контакт {contact}, день народження видалений"


@input_error
def del_adress(book: AddressBook, *args):
    contact = " ".join(args)
    rec = book.get(contact)
    rec.adress = None
    return f"Контакт {contact}, адреса видалена"


@input_error
def phone(book: AddressBook, *args):
    contact = " ".join(args)
    rec = book.get(contact)
    return f'Контакт "{contact}". {rec.show_phones()}'


@input_error
def show_all(book: AddressBook, *args):
    if len(book) <= PAGE:
        return book.show_all()
    else:
        gen_obj = book.iterator(PAGE)
        for i in gen_obj:
            print(i)
            print("*" * 50)
            input("Нажміть будь-яку клавішу")
        x = book.lening()
        return f"Всього: {x} контактів."


@input_error
def search(book: AddressBook, *args):
    pattern = " ".join(args)
    if len(pattern) < 3:
        return "довжина рядка для пошуку >= 3"
    result = book.search(pattern)
    if not result:
        return "не знайдено"
    matches = ""
    for i in result:
        matches += str(i)
    frags = matches.split(pattern)
    highlighted = ""
    for i, fragment in enumerate(frags):
        highlighted += fragment
        if i < len(frags) - 1:
            highlighted += "\033[42m" + pattern + "\033[0m"
    return f"Found {len(result)} match(es):\n" + highlighted


@input_error
def sort_targ_folder(book: AddressBook, *args):
    target_path = " ".join(args)
    return sort_folder.main(target_path)


@input_error
def help(*args):
    with open("README.md", "rb") as help_file:
        output = help_file.read().decode("utf-8")
        return output


@input_error
def exit(book: AddressBook, *args):
    global is_ended
    is_ended = True
    book.save_to_file(db_file_name)
    return "До побачення"


@input_error
def no_command(*args):
    return "Такої команди немає"


COMMANDS = {
    "hello": greet,
    "add email": add_email,
    "add b_day": add_birthday,
    "add adress": add_adress,
    "add": add,
    "congrat": congrat,
    "change": change,
    "phone": phone,
    "show all": show_all,
    "search": search,
    "del adress": del_adress,
    "del phone": del_phone,
    "del b_day": del_birthday,
    "del email": del_email,
    "del contact": del_contact,
    "sort folder": sort_targ_folder,
    "close": exit,
    "good bye": exit,
    "exit": exit,
    "help": help,
}


@input_error
def command_parser(line: str):
    line_prep = " ".join(line.split())
    for k, v in COMMANDS.items():
        if line_prep.lower().startswith(k + " ") or line_prep.lower() == k:
            return v, re.sub(k, "", line_prep, flags=re.IGNORECASE).strip().rsplit(" ")
    return no_command, []


is_ended = False


def main():
    book1 = AddressBook()
    global db_file_name
    with open("config.JSON") as cfg:
        cfg_data = json.load(cfg)
        db_file_name = cfg_data["PhoneBookFile"]

    if Path(db_file_name).exists():
        book1.load_from_file(db_file_name)

    print("Добрий день!", f"доступні команди: {', '.join(k for k in COMMANDS.keys())}")

    while not is_ended:
        s = input(">>>")

        command, args = command_parser(s)
        print(command(book1, *args))


if __name__ == "__main__":
    main()
