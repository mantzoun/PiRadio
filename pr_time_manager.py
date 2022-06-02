import datetime

class time_manager:
    counter = 0
    char = [":", " "]
    my_dt = ""
    my_tm = ""

    def reset(self):
        self.my_dt = ""
        self.my_tm = ""

    # Return current date, only if it has changed since the last query
    # otherwise, return None.
    def get_date(self):
        new_dt = datetime.date.today().strftime("%d/%m/%Y").center(16)
        if new_dt != self.my_dt:
            self.my_dt = new_dt
            return self.my_dt
        else:
            return None

    # Return current date, only if it has changed since the last query
    # otherwise, return None. Current implementaion will never return None.
    def get_time(self):
        self.counter += 1

        new_tm = datetime.datetime.now().strftime("%H" + self.char[self.counter % 2] + "%M").center(16)
        if new_tm != self.my_dt:
            self.my_tm = new_tm
            return self.my_tm
        else:
            return None
