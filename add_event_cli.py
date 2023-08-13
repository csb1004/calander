import os
import sys
import json
from database import *

# python add_event_cli.py {year} {month} {day} {event_string}
if __name__ == "__main__":
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    day = int(sys.argv[3])
    event = json.loads(sys.argv[4])

    db = CalendarDB(os.path.join(ROOT))

    db.year(year).month(month).add_event(day, event)