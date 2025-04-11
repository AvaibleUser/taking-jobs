from config import config
from gui.schedule import ScheduleGUI

if __name__ == '__main__':
    with config():
        app = ScheduleGUI()
        app.mainloop()
