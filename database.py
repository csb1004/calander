import calendar
import json
import os
import pathlib
import sys
from datetime import datetime

ROOT = "calendar"


class GroupStore:
    @staticmethod
    def setup(path_str: str):
        with open(os.path.join(path_str, "group.json"), "w", encoding="utf-8") as group_file:
            json.dump({}, group_file, ensure_ascii=False)

    @staticmethod
    def new_obj(name: str) -> dict:
        return {"name": name}

    @staticmethod
    def add_new_group(path_str: str, group: dict, id_num: int):
        with open(os.path.join(path_str, "group.json"), "r", encoding="utf-8") as group_file:
            groups = json.load(group_file)
        groups[str(id_num)] = group
        with open(os.path.join(path_str, "group.json"), "w", encoding="utf-8") as group_file:
            json.dump(groups, group_file, ensure_ascii=False)


class TagStore:
    @staticmethod
    def setup(path_str: str):
        with open(os.path.join(path_str, "tag.json"), "w", encoding="utf-8") as tag_file:
            json.dump({}, tag_file, ensure_ascii=False)

    @staticmethod
    def new_obj(name: str, color: int, hide: bool) -> dict:
        return {"name": name, "color": color, "hide": hide}

    @staticmethod
    def add_new_tag(path_str: str, tag: dict, id_num: int):
        with open(os.path.join(path_str, "tag.json"), "r", encoding="utf-8") as tag_file:
            tags = json.load(tag_file)
        tags[str(id_num)] = tag
        with open(os.path.join(path_str, "tag.json"), "w", encoding="utf-8") as tag_file:
            json.dump(tags, tag_file, ensure_ascii=False)


class Event:
    @staticmethod
    def new(name: str, desc: str, target_ids: [int], tag_id: int) -> dict:
        return {"name": name, "desc": desc, "target": target_ids, "tag": tag_id}


class MonthDB:
    def __init__(self, year: int, month: int, root_path: str):
        self._year = year
        self._month = month
        self._root_path = root_path

    @property
    def _path(self):
        return os.path.join(self._root_path, str(self._year), str(self._month))

    @property
    def value(self) -> int:
        return self._month

    @staticmethod
    def setup(year: int, month: int, root_path: str):
        with open(os.path.join(root_path, str(year), str(month)), "w", encoding='utf-8') as month_file:
            json.dump(MonthDB.new_obj(year, month), month_file, ensure_ascii=False)

    def read_content(self) -> dict:
        with open(os.path.join(self._root_path, str(self._year), str(self._month)), "r",
                  encoding='utf-8') as month_file:
            return json.load(month_file)

    def write_to_file(self, content: dict):
        # content.sort(key=lambda event: event["day"])
        with open(os.path.join(self._root_path, str(self._year), str(self._month)), "w",
                  encoding='utf-8') as month_file:
            json.dump(content, month_file, ensure_ascii=False)

    @staticmethod
    def new_obj(year: int, month: int) -> dict:
        ret = {}
        for day in range(calendar.monthrange(year, month)[1]):
            ret[day + 1] = []

        return ret

    def add_event(self, day: int, event: dict):
        existing_events = self.read_content()
        existing_events[str(day)].append(event)
        self.write_to_file(existing_events)
        print("일정을 추가하였습니다.")


class YearDB:
    def __init__(self, year: int, root_path: str):
        self._year = year
        self._root_path = root_path

    @property
    def _path(self):
        return os.path.join(self._root_path, str(self._year))

    @property
    def value(self) -> int:
        return self._year

    @staticmethod
    def setup(year: int, root_path: str):
        os.mkdir(os.path.join(root_path, str(year)))

        for month in range(1, 13):
            MonthDB.setup(year, month, root_path)

    def month(self, month: int) -> MonthDB:
        return MonthDB(self._year, month, self._root_path)

    @property
    def months(self) -> list[MonthDB]:
        return [MonthDB(self._year, int(pathlib.PurePath(month_dir).name), self._root_path)
                for month_dir in os.listdir(self._path)]


class CalendarDB:
    def __init__(self, path_str: str):
        self._path = path_str

        if not os.path.exists(self._path):
            print("DB를 초기화합니다.")
            self._setup()

    @property
    def path(self) -> str:
        return self._path

    def _setup(self):
        os.mkdir(self._path)
        GroupStore.setup(self._path)
        TagStore.setup(self._path)
        for year in (datetime.now().year, datetime.now().year + 1):
            YearDB.setup(year, root_path=self._path)

    def year(self, year: int) -> YearDB:
        return YearDB(year, root_path=self._path)

    @property
    def years(self) -> list[YearDB]:
        return [YearDB(int(pathlib.PurePath(year_dir).name), self._path) for year_dir in os.listdir(self._path)]


def add_event_cli(calendar_db: CalendarDB):
    print("일정을 추가합니다.")

    year = int(input("년도를 입력하세요: "))
    month = int(input("달을 입력하세요: "))
    day = int(input("일을 입력하세요: "))

    title = input("제목을 입력하세요: ")
    print("설멍을 입력하세요. Ctrl-D 혹은 Ctrl-Z를 누르면 입력을 마칩니다.")
    desc = sys.stdin.read()

    with open(os.path.join(ROOT, "tag.json"), encoding="utf-8") as tags_file:
        tags = json.load(tags_file)

    print("선택 가능한 태그:")
    for id_num, value in tags.items():
        print(f"{id_num}: {value['name']}")

    tag_id = None
    while True:
        if tag_id in tags.keys():
            break
        else:
            tag_id = input("태그를 선택하세요: ")
    tag_id = int(tag_id)

    with open(os.path.join(ROOT, "group.json"), encoding="utf-8") as groups_file:
        groups = json.load(groups_file)

    targets = []
    while True:
        print("선택 가능한 그룹:")
        for id_num, value in groups.items():
            print(f"{id_num}: {value['name']}")

        group_id = None
        while True:
            if group_id in groups.keys():
                break
            else:
                group_id = input("일정에 추가할 그룹을 선택하세요: ")

        targets.append(int(group_id))

        # 더 선택할건가 물어보기
        add_more = None
        while True:
            if add_more == "y" or add_more == "n":
                break
            else:
                add_more = input("더 선택하시겠습니까? (y/n): ")

        if add_more == "n":
            break

    # DB에 일정 추가
    calendar_db.year(year).month(month).add_event(day, Event.new(title, desc, targets, tag_id))


def add_group_cli(path_str: str):
    name = input("그룹 이름을 입력하세요: ")
    id_num = input("그룹 고유 id를 입력하세요: ")

    GroupStore.add_new_group(path_str, GroupStore.new_obj(name), int(id_num))


def add_tag_cli(path_str: str):
    name = input("태그 이름을 입력하세요: ")
    color = input("16진수 RGB 색상을 입력하세요(예: fa3b98): ")
    id_num = input("태그 id를 입력하세요: ")

    TagStore.add_new_tag(path_str, TagStore.new_obj(name, int(color, 16), False), int(id_num))


if __name__ == "__main__":
    # 기본 달력 DB 경로
    path = os.path.join(ROOT)
    db = CalendarDB(path)

    what_to_do = None
    while True:
        if what_to_do == "a":
            add_event_cli(db)
            print()
            what_to_do = None
        elif what_to_do == "g":
            add_group_cli(path)
            print()
            what_to_do = None
        elif what_to_do == "t":
            add_tag_cli(path)
            print()
            what_to_do = None
        elif what_to_do == "q":
            break
        else:
            what_to_do = input("일정 추가(a) / 그룹 추가(g) / 태그 추가(t) / 나가기(q): ")
