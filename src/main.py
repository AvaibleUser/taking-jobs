from config import config
from gui.schedule import ScheduleGUI


def main():
    with config():
        app = ScheduleGUI()
        app.mainloop()


if __name__ == '__main__':
    main()
