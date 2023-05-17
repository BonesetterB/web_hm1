from ab_classes import (
    Name,
    Phone,
    Email,
    Birthday,
    Record,
    AddressBook,
    Address,
    NotePad,
)
from functools import wraps
import json
from pathlib import Path
import pyttsx3
from notebook import (
    WITH_NOTES,
    add_note,
    add_tag,
    change_note,
    change_note_stat,
    show_notes,
    search_note,
    del_note,
)
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
            if func.__name__ == "add_birthday":
                return "введіть ім'я та день народження"
            if func.__name__ == "add_email":
                return "введіть ім'я та e-mail"
            return err

        except AttributeError:
            return "Перевірте правильність набору даних:"

        except ValueError as err:
            return err

        except IndexError as err:
            return err

    return wrapper


def greet(*args):
    return "Вітаю, я Ваш персональний бот-помічник MemoMind 1.0.0. Чим можу допомогти?"


def add_contact(book: AddressBook, contact: Name, *params):
    @input_error
    def inner_add_contact():
        contact_new = Name(contact)
        phone, email, address = None, None, []
        phone_regex = r"^(\+?\d{1,3})? ?(\d{2,3}) ?(\d{2,3}) ?(\d{2}) ?(\d{2})$"

        for i, param in enumerate(params):
            if "@" in param:
                email = Email(param)
            elif re.match(phone_regex, param):
                phone = Phone(param)
            else:
                address.append(param)

        address_str = " ".join(address)
        address = Address(address_str) if address_str else None
        rec_new = Record(contact_new, phone, email, address)

        if contact_new.value not in book.keys():
            book.add_record(rec_new)
            return f"Додано контакт '{contact}' з телефоном: {phone}, електронною поштою: {email} та адресою: {address}"
        else:
            rec = book.get(contact)
            if phone:
                rec.add_phone(phone)
            if email:
                rec.add_email(email)
            if address:
                rec.add_address(address)
            return f"Для існуючого контакту '{contact}' додано номер телефону: {phone}, електронну пошту: {email} та адресу: {address}"

    return inner_add_contact()


@input_error
def add_address(book: AddressBook, contact: str, *adres):
    x = " ".join(adres)
    address_new = Address(x)
    rec = book.get(contact)
    rec.add_adress(address_new)
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
        f"день народження в наступних контактів:\n{output}"
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
            phone_new = Phone(input(voice("Якщо хочете додати телефон введіть номер:")))
        else:
            phone_new = Phone(phone)
        rec.add_phone(phone_new)
        return f'Змінено номер телефону на {phone_new} для контакту "{contact}"'

    else:
        if len(rec.phones) == 1:
            num = 1
        if len(rec.phones) > 1:
            num = int(input(voice("Який ви хочете змінити (введіть індекс):")))
        if not phone:
            phone_new = Phone(input(voice("Будь ласка введіть новий номер:")))
        else:
            phone_new = Phone(phone)
        old_phone = rec.phones[num - 1]
        rec.edit_phone(phone_new, num)
        return f'Змінено номер телефону {old_phone} на {phone_new} для контакту "{contact}"'


@input_error
def change_email(
    book: AddressBook,
    contact: str,
    email: str = None,
):
    if contact not in book:
        return f'Контакт "{contact}" відсутній в адресній книзі'

    rec = book.get(contact)

    if not email:
        email_new = input(voice("Якщо хочете змінити e-mail введіть нову адресу: "))
    else:
        email_new = email

    rec.change_email(email_new)
    return f'Змінено e-mail контакту "{contact}" на {email_new}'


@input_error
def change_birthday(book: AddressBook, contact: str, birthday: str):
    rec = book.get(contact)
    new_birthday = Birthday(birthday)
    rec.change_birthday(new_birthday)
    return f'Змінено дату народження на {new_birthday} для контакту "{contact}"'


@input_error
def change_address(book: AddressBook, contact: str, *address):
    x = " ".join(address)
    address_new = Address(x)
    rec = book.get(contact)

    if not rec.adress:
        if not x:
            address_new = Address(
                input(voice("Якщо хочете додати адресу, введіть її:"))
            )
        else:
            address_new = Address(x)
        rec.add_address(address_new)
        return f'Додано адресу {address_new} для контакту "{contact}"'
    else:
        if not x:
            address_new = Address(input(voice("Будь ласка, введіть нову адресу:")))
        else:
            address_new = Address(x)
        old_address = rec.adress
        rec.change_address(address_new)
        return f'Змінено адресу {old_address} на {address_new} для контакту "{contact}"'


@input_error
def del_phone(book: AddressBook, contact: str, phone=None):
    rec = book.get(contact)
    rec.del_phone()
    return f"Контакт {contact}, телефон видалено"


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
        ans = input(f"Ви впевнені що хочете видалити контакт {contact}? (Y/N)").lower()
    return f"Контакт {book.remove_record(contact)} Видалено!"


@input_error
def del_birthday(book: AddressBook, *args):
    contact = " ".join(args)
    rec = book.get(contact)
    rec.birthday = None
    return f"Контакт {contact}, день народження видалений"


@input_error
def del_address(book: AddressBook, *args):
    contact = " ".join(args)
    rec = book.get(contact)
    rec.adress = None
    return f"Контакт {contact}, адреса видалена"


def load_data(book1: AddressBook, notebook: NotePad):
    global db_file_name, not_file_name
    with open("config.JSON") as cfg:
        cfg_data = json.load(cfg)
        db_file_name = cfg_data["PhoneBookFile"]
        not_file_name = cfg_data["NoteBookFile"]

    if Path(db_file_name).exists():
        book1.load_from_file(db_file_name)
        notebook.load_from_file(not_file_name)
    pass


@input_error
def phone(book: AddressBook, *args):
    contact = " ".join(args)
    rec = book.get(contact)
    return f'Контакт "{contact}". {rec.show_phones()}'


def save_data(book: AddressBook, notebook: NotePad):
    book.save_to_file(db_file_name)
    notebook.save_to_file(not_file_name)


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
    return f"Знайдено {len(result)} збігів:\n" + highlighted


@input_error
def sort_targ_folder(book: AddressBook, *args):
    target_path = " ".join(args)
    return sort_folder.main(target_path)


def voice(content, *yes):
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)
    engine.say(content)
    engine.runAndWait()
    return content


def help(*args):
    with open("README.md", "rb") as help_file:
        output = help_file.read().decode("utf-8")
        return output


def exit(book: AddressBook, notebook: NotePad, *args):
    global is_ended
    is_ended = True
    save_data(book, notebook)
    return voice("До побачення")


def no_command(*args):
    return "Такої команди немає"


def off_sound(book, *arg):
    global sound
    sound = False
    return "Звук вимкнено"


def on_sound(book, *arg):
    global sound
    sound = True
    return "Звук увімкнено"


COMMANDS = {
    "hello": greet,
    "add email": add_email,
    "add bday": add_birthday,
    "add address": add_address,
    "add contact": add_contact,
    "add note": add_note,
    "add tag": add_tag,
    "congrat": congrat,
    "change note": change_note,
    "change status": change_note_stat,
    "change address": change_address,
    "change bday": change_birthday,
    "change email": change_email,
    "change phone": change,
    "off sound": off_sound,
    "on sound": on_sound,
    "phone": phone,
    "show contacts": show_all,
    "show notes": show_notes,
    "search note": search_note,
    "search": search,
    "del note": del_note,
    "del address": del_address,
    "del phone": del_phone,
    "del bday": del_birthday,
    "del email": del_email,
    "del contact": del_contact,
    "sort folder": sort_targ_folder,
    "close": exit,
    "good bye": exit,
    "exit": exit,
    "help": help,
}


def command_parser(line: str):
    line_prep = " ".join(line.split())
    for k, v in COMMANDS.items():
        if line_prep.lower().startswith(k + " ") or line_prep.lower() == k:
            return v, re.sub(k, "", line_prep, flags=re.IGNORECASE).strip().rsplit(" ")
    return no_command, []


is_ended = False
sound = False


def main():
    book1 = AddressBook()
    notebook = NotePad()

    print(
        "MemoMind 1.0.0\n", f"доступні команди: {', '.join(k for k in COMMANDS.keys())}"
    )

    while not is_ended:
        load_data(book1, notebook)
        s = input(">>>")
        command, args = command_parser(s)
        if sound:
            if command == exit:
                print(command(book1, notebook), *args)
            elif command == help:
                print(command(book1, notebook), *args)
            else:
                print(
                    voice(
                        command((notebook if command in WITH_NOTES else book1), *args)
                    )
                )
        else:
            if command == exit:
                print(command(book1, notebook), *args)
            else:
                print(command((notebook if command in WITH_NOTES else book1), *args))
        save_data(book1, notebook)


if __name__ == "__main__":
    main()
