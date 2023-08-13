import os
import sys
import json
from database import *

# python cli_db.py push {year} {month} {day} {event_string}
if __name__ == "__main__":
    match sys.argv[1]:
        case "push":
            year = int(sys.argv[2])
            month = int(sys.argv[3])
            day = int(sys.argv[4])
            event = json.loads(sys.argv[5])

            db = CalendarDB(os.path.join(ROOT))

            db.year(year).month(month).add_event(day, event)
