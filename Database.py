from datetime import date
import datetime as dt
import os
from dotenv import load_dotenv


import psycopg2
load_dotenv()

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("HOST"),
            database=os.getenv("DATABASE"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            port=os.getenv("PORT")
        )


        self.cur = self.conn.cursor()

    def create_table_habits(self):
        pass
        #???


    def create_user(self, username: str, user_id: int):
        sql = """INSERT INTO users (username, chat_id) 
                          VALUES (%s, %s)"""

        self.cur.execute(sql, (username, user_id))

        self.conn.commit()

    def get_users(self):

        self.cur.execute("""SELECT * FROM users""")

        habits = self.cur.fetchall()

        if habits is not None:
            return habits
        else:
            return []

    def add_habit(self, name: str, user_id: int, repeats: int ):
        sql = """INSERT INTO habits (name, user_id, repeats) 
                          VALUES (%s, %s, %s)"""
        print(f"{self.cur.fetchall()}_______----оно")
        self.cur.execute(sql, (name, user_id, repeats))

        self.conn.commit()

        print(self.cur.fetchone())


    def get_new_habit_id(self, user_id: int):
        sql = """SELECT MAX(id) FROM habits WHERE user_id = %s"""

        self.cur.execute(sql, (user_id,))

        new_habit_id = self.cur.fetchone()

        if new_habit_id is not None:
            return new_habit_id[0]
        else:
            return None

    def add_report(self, habit_id: int, status: bool, day: date, user_id: int):
        sql = """INSERT INTO reports (habit_id, status, day, user_id)
                 VALUES (%s, %s, %s, %s)"""

        self.cur.execute(sql, (habit_id, status, day, user_id))
        self.conn.commit()


    def get_habits(self, user_id: int):
        sql = """SELECT * FROM habits WHERE user_id = %s"""

        self.cur.execute(sql, (user_id,))

        habits = self.cur.fetchall()

        if habits is not None:
            return habits
        else:
            return []


    def get_reports(self, user_id: int, date: date = date.today()):
        sql = """SELECT * FROM reports WHERE user_id = %s AND day = %s"""

        self.cur.execute(sql, (user_id, date))

        reports = self.cur.fetchall()

        if reports is not None:
            return reports
        else:
            return []

    def user_exists(self, user_id: int):
        sql = """SELECT * FROM users WHERE chat_id = %s"""

        self.cur.execute(sql, (user_id,))
        print(self.cur.rowcount)

        if self.cur.rowcount != 0:
            return True
        else:
            return False


    def status(self, habit_id: int):
        sql = """SELECT status FROM reports WHERE habit_id = %s"""

        self.cur.execute(sql, (habit_id,))

        status = self.cur.fetchall()

        if status:
            return status
        else:
            return None


    def note_habit(self, habit_id: int, status: bool):
        sql = """UPDATE reports SET status = %s WHERE habit_id = %s"""

        self.cur.execute(sql, (status, habit_id))

        self.conn.commit()


    def add_all_reports(self, user_id: int):
        for habit in self.get_habits(user_id):
            self.add_report(habit[0], status=False, day=date.today(), user_id=user_id)


    def is_habits_reports_by_today_date(self, user_id: int):
        kolvo_habits = len(self.get_habits(user_id))
        kolvo_reports = len(self.get_reports(user_id))

        if kolvo_reports == kolvo_habits:
            return True
        else:
            return False

    def update_habit(self, name: str, repeats: int, habit_id: int):
        sql = """UPDATE habits SET name = %s, repeats=%s WHERE id = %s"""

        self.cur.execute(sql, (name, repeats, habit_id))

        self.conn.commit()

    def get_habits_status_for_day(self, date: date, user_id: int):
        sql = """SELECT status FROM reports WHERE day = %s AND user_id = %s"""

        self.cur.execute(sql, (date, user_id))

        status_all = self.cur.fetchall()
        cnt = 0

        for status in status_all:
            if status[0] == True:
                cnt += 1

        if cnt == len(status_all) and status_all != []:
            return True
        else:
            return False

    def get_habits_status_for_month(self, user_id: int):
        status_spisok = []
        for i in range(31):
            status_spisok.append(self.get_habits_status_for_day(date.today() - dt.timedelta(days=i), user_id))

        return status_spisok

    def get_len_habits_status_true_for_month(self, user_id: int):
        status_cnt = 0
        for i in range(31):
            if self.get_habits_status_for_day(date.today() - dt.timedelta(days=i), user_id) == True:
                    status_cnt += 1

        return status_cnt


if __name__ == "__main__":
    db = Database()
    print(db.get_habits_status_for_month(1145169882))
    print(db.get_habits_status_for_day(date.today(), 1145169882))
    print(db.get_len_habits_status_true_for_month(1145169882))

