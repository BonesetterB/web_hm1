from ab_classes import (
    Name,
    Phone,
    Email,
    Birthday,
    Record,
    AddressBook,
    Address,
    NotePad,
    SendingContact,
    SendingAddress,
    SendingEmail,
    SendingBirthday,
    SendingCongrat,
    SendingNote,
    SendingTag,
    SendingPhone,
)

from functools import wraps
import json
import os
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
from abc import abstractmethod, ABC


dir_path = os.path.dirname(__file__)


def input_error(func):
    @wraps(func)
    def wrapper(*args):
        try:
            result = func(*args)
            return result

        except TypeError as err:
            if func.__name__ == "add_birthday":
                if languages:
                    return "enter name and birthday"
                else:
                    return "введіть ім'я та день народження"
            if func.__name__ == "add_email":
                if languages:
                    return "enter name and e-mail"
                else:
                    return "введіть ім'я та e-mail"
            return err

        except AttributeError:
            if languages:
                return "Check the correctness of data inputs and if contact was created"
            else:
                return "Перевірте правильність вводу даних та чи створений контакт"

        except ValueError as err:
            return err

        except IndexError as err:
            return err

    return wrapper


def greet(*args):
    if languages:
        return "Hello, I am your personal MemoMind bot assistant. How can I help?"
    else:
        return "Вітаю, я Ваш персональний бот-помічник MemoMind  Чим можу допомогти?"


def add_contact(book: AddressBook, contact: Name, *params):
    @input_error
    def inner_add_contact():
        contact_l = [contact,]
        phone, email, address = None, None, []
        phone_regex = r"^(\+?\d{1,3})? ?(\d{2,3}) ?(\d{2,3}) ?(\d{2}) ?(\d{2})$"

        for i, param in enumerate(params):
            if "@" in param:
                email = Email(param) if "@" in param else "-"
            elif re.match(phone_regex, param):
                phone = Phone(param)
            else:
                if i > 1:  #name can be mximum 3 words
                    address.append(param)
                else:
                    contact_l.append(param)
                    
        contact_str = " ".join(contact_l)
        contact_new = Name(contact_str)
        address_str = " ".join(address)
        address = Address(address_str) if address_str else "-"
        email_display = email.value if email else "-"
        rec_new = Record(contact_new, phone, email, address if address_str else None)
        interface=SendingContact(contact,phone,email_display,address)
        if contact_new.value not in book.keys():
            book.add_record(rec_new)
            return interface.sending(languages)
        else:
            rec = book.get(contact)
            if phone:
                rec.add_phone(phone)
            if email:
                rec.add_email(email)
            if address_str:
                rec.add_address(address)
            return interface.sendADd(languages)

    return inner_add_contact()


@input_error
def add_address(book: AddressBook, contact: str, *address):
    x = " ".join(address)
    address_new = Address(x)
    rec = book.get(contact)
    rec.add_address(address_new)
    inter=SendingAddress(contact,x)
    return inter.sending(languages)


@input_error
def add_email(book: AddressBook, contact: str, email: str):
    email_new = Email(email)
    rec = book.get(contact)
    rec.add_email(email_new)
    interface=SendingEmail(contact,email)
    return interface.sending(languages)
    

@input_error
def add_birthday(book: AddressBook, contact: str, birthday: str):
    b_day = Birthday(birthday)
    rec = book.get(contact)
    rec.add_birthday(b_day)
    inter=SendingBirthday(contact,b_day)
    return inter.sending(languages)

@input_error
def congrat(book: AddressBook, days: int):
    if days == "":
        if languages:
            raise ValueError("Enter number of days")
        else:
            raise ValueError("Введіть число днів")
    output = ""
    for contact in book.values():
        if contact.days_to_birthday() <= int(days):
            output += str(contact)
    inter=SendingCongrat(days,output)
    return inter.sending(languages)


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
            if languages:
                phone_new = Phone(
                    input(voice("If you want to add a phone number, enter the number:"))
                )
            else:
                phone_new = Phone(
                    input(voice("Якщо хочете додати телефон введіть номер:"))
                )
        else:
            phone_new = Phone(phone)
        rec.add_phone(phone_new)
        inter=SendingPhone(contact,phone_new)
        return inter.sendingChange(languages)
    else:
        if len(rec.phones) == 1:
            num = 1
        if len(rec.phones) > 1:
            if languages:
                num = int(
                    input(voice("Which one do you want to change (enter index):"))
                )
            else:
                num = int(input(voice("Який ви хочете змінити (введіть індекс):")))
        if not phone:
            if languages:
                phone_new = Phone(input(voice("Please enter a new number:")))
            else:
                phone_new = Phone(input(voice("Будь ласка введіть новий номер:")))
        else:
            phone_new = Phone(phone)
        old_phone = rec.phones[num - 1]
        rec.edit_phone(phone_new, num)
        inter=SendingPhone(contact,phone_new)
        return inter.sendingChange(languages)

@input_error
def change_email(
    book: AddressBook,
    contact: str,
    email: str = None,
):
    if contact not in book:
        if languages:
            return f'The contact "{contact}" is not in the address book'
        else:
            return f'Контакт "{contact}" відсутній в адресній книзі'

    rec = book.get(contact)

    if not email:
        if languages:
            email_new = input("If you want to change the e-mail, enter a new address: ")
        else:
            email_new = input("Якщо хочете змінити e-mail введіть нову адресу: ")
    else:
        email_new = email

    rec.change_email(email_new)
    inter=SendingEmail(contact,email_new)
    return inter.sendChange(languages)


@input_error
def change_birthday(book: AddressBook, contact: str, birthday: str):
    rec = book.get(contact)
    new_birthday = Birthday(birthday)
    rec.change_birthday(new_birthday)
    inter=SendingBirthday(contact,new_birthday)
    return inter.sendChange(languages)

@input_error
def change_address(book: AddressBook, contact: str, *address):
    x = " ".join(address)
    address_new = Address(x)
    rec = book.get(contact)
    inter=SendingAddress(contact,address_new)
    if not rec.address:
        if not x:
            if languages:
                address_new = Address(
                    input(voice("If you want to add an address, enter it:"))
                )
            else:
                address_new = Address(
                    input(voice("Якщо хочете додати адресу, введіть її:"))
                )
        else:
            address_new = Address(x)
        rec.add_address(address_new)
        return inter.sending(languages)
    else:
        if not x:
            if languages:
                address_new = Address(input(voice("Please enter a new address:")))
            else:
                address_new = Address(input(voice("Будь ласка, введіть нову адресу:")))
        else:
            address_new = Address(x)
        old_address = rec.address
        rec.change_address(address_new)
        return inter.sendChange(languages,old_address)


@input_error
def del_phone(book: AddressBook, contact: str, phone=None):
    rec = book.get(contact)
    rec.del_phone()
    inter=SendingPhone(contact)
    return inter.sendDel(languages)


@input_error
def del_email(book: AddressBook, *args):
    contact = " ".join(args)
    rec = book.get(contact)
    rec.email = None
    interface=SendingEmail(contact)
    return interface.sending(languages)


@input_error
def del_contact(book: AddressBook, *args):
    contact = " ".join(args)
    rec = book.get(contact)
    if not rec:
        raise AttributeError
    ans = None
    interface=SendingContact(book.remove_record(contact))
    while ans != "y":
        if languages:
            ans = input(f"Are you sure you want to delete {contact}? (Y/N)").lower()
        else:
            ans = input(
                f"Ви впевнені що хочете видалити контакт {contact}? (Y/N)"
            ).lower()
    return interface.sendDel(languages)


@input_error
def del_birthday(book: AddressBook, *args):
    contact = " ".join(args)
    rec = book.get(contact)
    rec.birthday = None
    inter=SendingBirthday(contact)
    return inter.sendChange(languages)


@input_error
def del_address(book: AddressBook, *args):
    contact = " ".join(args)
    rec = book.get(contact)
    rec.address = None
    interface=SendingAddress(contact)
    return interface.sendDel(languages)


def load_data(book1: AddressBook, notebook: NotePad):
    global db_file_name, note_file_name, PAGE, languages
    with open(os.path.join(dir_path, "config.JSON")) as cfg:
        cfg_data = json.load(cfg)
        db_file_name = os.path.join(dir_path, cfg_data["PhoneBookFile"])
        note_file_name = os.path.join(dir_path, cfg_data["NoteBookFile"])
        PAGE = cfg_data["Page"]
        languages = True if cfg_data["Language"] == "eng" else False
        
    if Path(db_file_name).exists():
        book1.load_from_file(db_file_name)
    if Path(note_file_name).exists():
        notebook.load_from_file(note_file_name)
    pass


@input_error
def phone(book: AddressBook, *args):
    contact = " ".join(args)
    rec = book.get(contact)
    if languages:
        return f'Contact "{contact}". {rec.show_phones()}'
    else:
        return f'Контакт "{contact}". {rec.show_phones()}'


def save_data(book: AddressBook, notebook: NotePad):
    book.save_to_file(db_file_name)
    notebook.save_to_file(note_file_name)


def show_all(book: AddressBook, *args):
    if len(book) <= PAGE:
        return book.show_all()
    else:
        gen_obj = book.iterator(PAGE)
        for i in gen_obj:
            if languages:
                print(i)
                print("*" * 50)
                input("Press any key")
            else:
                print(i)
                print("*" * 50)
                input("Нажміть будь-яку клавішу")
        x = book.lening()
        if languages:
            return f"Total: {x} contacts."
        else:
            return f"Всього: {x} контактів."


@input_error
def search(book: AddressBook, *args):
    pattern = " ".join(args)
    if len(pattern) < 3:
        if languages:
            return "search string length >= 3"
        else:
            return "довжина рядка для пошуку >= 3"
    result = book.search(pattern)
    if not result:
        if languages:
            return "not found"
        else:
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
    if languages:
        return f"Found {len(result)} matches:\n" + highlighted
    else:
        return f"Знайдено {len(result)} збігів:\n" + highlighted


@input_error
def sort_targ_folder(book: AddressBook, *args):
    target_path = " ".join(args)
    return sort_folder.main(target_path)


def voice(content, *yes):
    sound
    engine = pyttsx3.init("sapi5")
    if sound:
        engine.say(content)
        engine.runAndWait()
    return content


def help(*args):
    if languages:
        with open(os.path.join(dir_path, "README.md"), "rb") as help_file:
            output = help_file.read().decode("utf-8")
            return output
    else:
        with open(os.path.join(dir_path, "README.ua.md"), "rb") as help_file:
            output = help_file.read().decode("utf-8")
            return output


def exit(book: AddressBook, notebook: NotePad, *args):
    global is_ended
    is_ended = True
    save_data(book, notebook)
    if languages:
        return voice("Good bye") if sound else "Good bye"
    else:
        return "До побачення"


def no_command(*args):
    if languages:
        return "There is no such command"
    else:
        return "Такої команди немає"


def off_sound(book, *args):
    global sound
    sound = False
    if languages:
        return "Sound off"
    else:
        return "В український версії читання вголос поки що не доступне"


def on_sound(book, *args):
    global sound
    if languages:
        sound = True
        return "Sound on"
    else:
        return "В український версії читання вголос поки ще не доступне"


@input_error
def language(book, *args):
    global languages
    with open(os.path.join(dir_path, "config.JSON"), "r") as cfg:
        cfg_data = json.load(cfg)
    if languages:
        x = input("Choose language: English or Ukrainian?(eng/ukr)>>> ")
    else:
        x = input("Виберіть мову: англійська або українська?(eng/ukr)>>> ")
    if "e" in x or "E" in x:
        with open(os.path.join(dir_path, "config.JSON"), "w") as cfg:
            cfg_data["Language"] = "eng"
            json.dump(cfg_data, cfg)
            return (
                "The language was successfully selected. To apply pease restart the bot"
                if languages
                else "Мова виводу на екран була успішно вибрана. Зміниться після перезапуску боту"
            )
    else:
        with open(os.path.join(dir_path, "config.JSON"), "w") as cfg:
            cfg_data["Language"] = "ukr"
            json.dump(cfg_data, cfg)
            return (
                "The language was successfully selected. To apply pease restart the bot"
                if languages
                else "Мова виводу на екран була успішно вибрана. Зміниться після перезапуску боту"
            )


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
    "sound off": off_sound,
    "sound on": on_sound,
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
    "lang": language,
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
languages = True  # True=En, False=Ukraine


def main():
    
    book1 = AddressBook()
    notebook = NotePad()
    load_data(book1, notebook)
    if languages:
        print(
            "MemoMind \n",
            f"Available commands: {', '.join(k for k in COMMANDS.keys())}",
        )
    else:
        print(
            "MemoMind \n",
            f"Доступні команди: {', '.join(k for k in COMMANDS.keys())}",
        )
    
    while not is_ended:   
        s = input(">>>")
        command, args = command_parser(s)
        if languages:
            if sound:
                if command == exit:
                    print(command(book1, notebook), *args)
                elif command == sort_targ_folder:
                    print(command(book1), *args)
                elif command == help:
                    print(command(book1, notebook), *args)
                else:
                    print(
                        voice(
                            command(
                                (notebook if command in WITH_NOTES else book1), *args
                            )
                        )
                    )
            else:
                if command == exit:
                    print(command(book1, notebook), *args)
                else:
                    print(
                        command((notebook if command in WITH_NOTES else book1), *args)
                    )
        else:
            if command == exit:
                print(command(book1, notebook), *args)
            else:
                print(command((notebook if command in WITH_NOTES else book1), *args))


if __name__ == "__main__":
    main()
