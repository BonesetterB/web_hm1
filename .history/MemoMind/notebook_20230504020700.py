"""adding ,changing ,changing status, deleting, searching notes
, adding tag, searching by tag"""
from ab_classes import Note, NotePad, HashTag
import json
import os


with open(os.path.join("memomind", "config.JSON")) as cfg:
    cfg_data = json.load(cfg)
    languages = True if cfg_data["Language"] == "eng" else False


def input_error(func):
    def wrapper(*args):
        try:
            result = func(*args)
            return result

        except TypeError as err:
            return err

        except AttributeError:
            if languages:
                return "Check the correctness of data inputs:"
            else:
                return "Перевірте правильність набору даних:"

        except ValueError as err:
            return err

        except IndexError as err:
            return err

    return wrapper


@input_error
def add_note(notebook: NotePad, *args):
    text = f'{" ".join(args)}'
    if not text:
        if languages:
            raise ValueError("enter the note text")
        else:
            raise ValueError("введіть текст нотатки")
    record = Note(text)
    notebook.add_note(record)
    if languages:
        return "Note added"
    else:
        return "Нотатка добавлена"


@input_error
def add_tag(notebook: NotePad, note, tag):
    if not tag:
        if languages:
            raise ValueError("Enter  first_letters_of_the_note... #tag")
        else:
            raise ValueError("Введіть перші_літери_нотатки... #тег")
    rec = quick_note(notebook, note)
    rec.add_tag(HashTag(tag))
    notebook.sorting()
    if languages:
        return f'Tag "{tag}" added to record "{rec}"'
    else:
        return f'Тег "{tag}" додано до запису "{rec}"'


@input_error
def change_note(notebook: NotePad, *args):
    text = f'{" ".join(args)}'
    if not text:
        if languages:
            raise ValueError("enter part of the note text")
        else:
            raise ValueError("введіть частину тексту нотатки")
    old_note, new_note = text.split("... ")
    if old_note.startswith("#"):
        record = quick_tag(notebook, old_note)
        old_note = record
        if record:
            notebook.change_note(record, new_note)
            if languages:
                return f'"{old_note}" changed to "{new_note}"'
            else:
                return f'"{old_note}" змінено на "{new_note}"'
    record = quick_note(notebook, old_note)
    if record in notebook.note_list:
        notebook.change_note(record, new_note)
        if languages:
            return f'"{old_note}" changed to "{new_note}"'
        else:
            return f'"{old_note}" змінено на "{new_note}"'
    if languages:
        return f'Record "{record}" not found'
    else:
        return f'Запис "{record}" не знайдений'


@input_error
def change_note_stat(notebook: NotePad, *args):
    text = f'{" ".join(args)}'
    if text.startswith("#"):
        record = quick_tag(notebook, text)
        if record:
            notebook.change_status(record)
            if languages:
                return f'The status of {record} has been changed to "done"'
            else:
                return f'Статус нотатки {record} змінено на "виконано"'
    record = quick_note(notebook, text)
    if record in notebook.note_list:
        notebook.change_status(record)
        if languages:
            return f'The status of {record} has been changed to "done"'
        else:
            return f'Статус нотатки {record} змінено на "виконано"'
    if languages:
        return f'Record "{record}" not found'
    else:
        return f'Запис "{record}" не знайдений'


@input_error
def del_note(notebook: NotePad, *args):
    text = f'{" ".join(args)}'
    if not text:
        if languages:
            raise ValueError("enter part of note text or #tag")
        else:
            raise ValueError("введіть частину тексту нотатки або #тег")
    if text.startswith("#"):
        record = quick_tag(notebook, text)
        if record:
            notebook.delete(record)
            notebook.sorting()
            if languages:
                return f'"{record}" deleted successfully'
            else:
                return f'"{record}" видалений успішно'
    record = quick_note(notebook, text)
    if record in notebook.note_list:
        notebook.delete(record)
        notebook.sorting()
        if languages:
            return f'"{record}" deleted successfully'
        else:
            return f'"{record}" видалений успішно'
    if languages:
        return f'Record "{record}" not found'
    else:
        return f'Запис "{record}" не знайдений'


@input_error
def search_note(notebook: NotePad, *args):
    text = f'{" ".join(args)}'
    text = text.replace("...", "")
    list_of_notes = []
    if languages:
        error = "Record not found"
    else:
        error = "Запис не знайдений"
    if text.startswith("#"):
        tag = text.replace("#", "")
        for note in notebook.note_list:
            for hashtag in note.tag_list:
                list_of_notes.append(note) if tag in str(hashtag) else None
        if languages:
            output = (
                f"Found notes for {text}"
                + "\n"
                + f'{", ".join(str(note) for note in list_of_notes)}'
            )
        else:
            output = (
                f"Знайдені нотатки за {text}"
                + "\n"
                + f'{", ".join(str(note) for note in list_of_notes)}'
            )
        return output if len(list_of_notes) != 0 else error
    for note in notebook.note_list:
        if text in str(note):
            list_of_notes.append(note)
    if languages:
        output = (
            f"Found notes for {text}"
            + "\n"
            + f'{ ", ".join(str(note) for note in list_of_notes)}'
        )
    else:
        output = (
            f"Знайдені нотатки за {text}"
            + "\n"
            + f'{ ", ".join(str(note) for note in list_of_notes)}'
        )
    return output if len(list_of_notes) != 0 else error


def show_notes(notebook: NotePad, *args):
    line = ""
    for note in notebook.note_list:
        tags = ", ".join(str(tag) for tag in note.tag_list)
        if languages:
            line += (
                f'{tags} creation date: {note.day.strftime("%d-%m-%Y")}.Content: {str(note)}.Status {f"done.Date done {note.done_date}"if note.done else "not done"}'
                + "\n"
            )
        else:
            line += (
                f'{tags} дата створення: {note.day.strftime("%d-%m-%Y")}.Зміст: {str(note)}.Статус {f"виконано.Дата виконання {note.done_date}"if note.done else "не виконано"}'
                + "\n"
            )
    if languages:
        return "list of notes\n" + line + "end of list of notes"
    else:
        return "список нотатків\n" + line + "кінець списку нотаток"


def quick_tag(notebook: NotePad, text: str):
    for note in notebook.note_list:
        for tag in note.tag_list:
            if str(text) in str(tag):
                return note
    return None


def quick_note(notebook: NotePad, text: str):
    content = text.replace("...", "")
    for note in notebook.note_list:
        if content in str(note):
            return note
    record = Note(content)
    return record


WITH_NOTES = [
    add_note,
    add_tag,
    change_note,
    change_note_stat,
    show_notes,
    search_note,
    del_note,
]
