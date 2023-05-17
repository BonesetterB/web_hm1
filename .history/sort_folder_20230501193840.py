from pathlib import Path

# import pkgutil  #ПОКИ ЩЕ НЕ ВИДАЛЯТИ - ЗГОДИТЬСЯ ПРИ ПАКУВАННІ В СКРИПТА В ПАКЕТ!!!
import shutil
from translit import normalize
import json

CATEGORIES = {}
found_files = {}

known_types = []
unknown_types = []
deleted_folders = []


def read_config():
    global CATEGORIES
    # ПОКИ ЩЕ НЕ ВИЛАЛЯТИ - ЗГОДИТЬСЯ ПРИ ПАКУВАННІ В СКРИПТА В ПАКЕТ!!!
    # cfg = pkgutil.get_data(__package__, "config.txt")
    # cfg_str = cfg.decode("utf-8")
    # with open("config.txt") as cfg:
    #     cfg_str = cfg.read()

    with open("config.JSON") as cfg:
        cfg_data = json.load(cfg)
        CATEGORIES = cfg_data["FILETYPES"]
        for key in CATEGORIES:
            found_files.update({key: []})


def scan_folder(path: Path):
    contents = [x for x in path.iterdir()]
    for item in contents:
        is_unknown = True
        if item.is_file():
            ext = item.suffix[1:].upper()

            for name, types in CATEGORIES.items():
                if ext in types:
                    found_files[name].append(item)
                    known_types.append(ext)
                    is_unknown = False
                    break

            if is_unknown:
                unknown_types.append(ext)

        else:
            if item.name not in CATEGORIES.keys():
                scan_folder(item)
            else:
                continue


def move_files(files_list: list, target_path: Path, new_folder_name: str) -> list:
    output_list = []
    new_dir = target_path / new_folder_name
    try:
        new_dir.mkdir()
    except FileExistsError:
        pass
    for file in files_list:
        new_name = normalize(file.name)
        output_list.append(new_name)
        try:
            file.rename(f"{new_dir}\{new_name}")
        except FileExistsError:
            file.unlink()  # delete doubles
    return output_list


def unpack_files(target_path: Path):
    arc_dir = target_path / "archives"
    files = [x for x in arc_dir.iterdir()]

    for file in files:
        new_name = normalize(file.name).split(".")[0]
        new_dir = arc_dir  # / new_name
        try:
            new_dir.mkdir()
            shutil.unpack_archive(file, new_dir)
        except (FileExistsError, shutil.ReadError):
            pass
        try:
            file.unlink()  # delete unpacked archive
        except FileNotFoundError:
            pass


def del_empty_folders(path: Path):
    folders = [x for x in path.iterdir() if x.is_dir()]
    for item in folders:
        if item.name not in CATEGORIES.keys():
            if len(list(Path(item).iterdir())) == 0:
                deleted_folders.append(item.name)
                item.rmdir()
            else:
                del_empty_folders(item)
        else:
            continue


def normalize_all(path: Path):
    try:
        items = [x for x in path.iterdir()]
    except FileNotFoundError:
        return None
    for item in items:
        if item.is_file():
            new_name = item.parent / normalize(item.name)
            item.rename(new_name)
        else:
            if item.name not in CATEGORIES.keys():
                new_name = item.parent / normalize(item.name)
                item.rename(new_name)
                normalize_all(item)
            else:
                continue


def report_category(category: str, files_lst: list):
    print(f'Знайдено файлів в категорії "{category.capitalize()}": ', len(files_lst))


def main(work_path):
    read_config()

    if not work_path:
        return "Будь ласка вкажіть цільовий шлях в параметрах"

    path = Path(work_path)

    if not path.exists():
        return "Вказаний шлях не існує"

    scan_folder(path)

    found_known = set(known_types)
    found_unknown = set(unknown_types)

    # create folders only for found file types
    for category in found_files.keys():
        if len(found_files.get(category)) > 0:
            report_category(
                category, move_files(found_files.get(category), path, str(category))
            )

    # unpack archives if found any
    if len(found_files.get("archives")) > 0:
        unpack_files(path)

    del_empty_folders(path)

    normalize_all(path)
    output = f"""Знайдено файли відомих типів: {', '.join(f for f in found_known)}. Dсього {len(known_types)} файлів.
Знайдено файли невідомих типів: {', '.join(f for f in found_unknown)}. всього {len(unknown_types)} файлів.
Видалено порожніх тек {len(deleted_folders)}"""

    return output


if __name__ == "__main__":
    main()
