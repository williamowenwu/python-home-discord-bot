import json
import time
import gspread
import gspread.exceptions
import datetime
import constants

TOTAL_AMOUNT_CELL = 'D6'
TOTAL_HOURS_CELL = 'D7'
COLUMN_OFFSET = 2

class SheetsManager:
    def __init__(self, user: str) -> None:
        # open the service account and grab the data
        self.sa = gspread.service_account(filename="discord-connection.json")
        self.sheet_info_dict = self.get_sheet_info()
        self.user = user

        today = datetime.date.today()
        month_str = today.strftime("%B")
        year_str = today.strftime("%Y")

        try: # open the year sheet
            self.sh = self.sa.open(f"{user} {year_str}")
        except gspread.exceptions.SpreadsheetNotFound as e:
            print(f"Spreadsheet '{user} {year_str}' doesn't exist")
            # create and share the spreadsheet
            self.sh = self.sa.create(f"{user} {year_str}")
            self.sh.share(constants.WILL_EMAIL, perm_type='user', role='writer')
            self.sh.share(constants.JIN_EMAIL, perm_type='user', role='writer')
            self.reset_sheets_info()
            print(f"Sucessfully created spreadsheet {user} {year_str}!")

        try:
            self.worksheet = self.sh.worksheet(f"{month_str}")
        except gspread.exceptions.WorksheetNotFound as e:
            print(f"Worksheet {month_str} not found")
            # create the worksheet
            self.worksheet = self.sh.add_worksheet(title=f"{month_str}", rows=1000, cols=28)
            self.reset_sheets_info()
            print(f"Created worksheet {month_str}")
        
        self.sheet_link = f"https://docs.google.com/spreadsheets/d/{self.sh.id}"

    def write_to_sheet_info(self) -> None:
        with open("data.json", "w") as f:
            json.dump(self.sheet_info_dict, f)

    def get_sheet_info(self) -> dict:
        try:
            with open("data.json", "r") as f:
                sheet_info_dict = json.load(f)
        except FileNotFoundError as e:
            print("File not found\n",e)
            exit()
        except json.decoder.JSONDecodeError as e: # empty file
            print("JSONDecodeError:", e)
            today = datetime.date.today()
            with open("config.json", "r") as file:
                config = json.load(file)

            column_names = config["column_names"]
            self.worksheet.append_row(column_names)

            today = datetime.date.today()

            self.sheet_info_dict = config["sheet_info_dict"]
            self.sheet_info_dict["current_week"] = (today.day - 1) // 7 + 1
            self.sheet_info_dict["current_month"] = today.month
            self.write_to_sheet_info()

            self.sheet_info_dict = sheet_info_dict
        return sheet_info_dict


    def reset_sheets_info(self) -> None:
        self.worksheet.clear()

        with open("config.json", "r") as file:
            config = json.load(file)

        column_names = config["column_names"]
        self.worksheet.append_row(column_names)

        today = datetime.date.today()

        self.sheet_info_dict = config["sheet_info_dict"]
        self.sheet_info_dict["current_week"] = (today.day - 1) // 7 + 1
        self.sheet_info_dict["current_month"] = today.month
        self.sheet_info_dict["current_year"] = today.year
        self.write_to_sheet_info()
        print(self.sheet_info_dict)
    
    def add_income(self, total_amount, hours_worked):
        # Get today's date
        today = datetime.date.today()
        day_of_month = today.day
        week_of_month = (day_of_month - 1) // 7 + 1

        # Create a list with the new row data
        new_row = [today.strftime("%m/%d/%Y"), f"${total_amount}", hours_worked]

        # Add the new row to the worksheet
        self.worksheet.append_row(new_row)
        
        self.sheet_info_dict.update({
            key: self.sheet_info_dict.get(key, 0) + value
            for key, value in {
                "amount_sum": total_amount,
                "hours_sum": hours_worked,
                "total_week_hours": total_amount,
                "total_week_amount": hours_worked,
                "last_row": 1
            }.items()
        })

        total_week_amount = self.sheet_info_dict.get("total_week_hours")
        total_week_hours = self.sheet_info_dict.get("total_week_amount")
        week_column = chr(ord('D') + week_of_month - 1) #clever way to get the correct columns for the week
        self.worksheet.update_acell(f"{week_column}2", f"Amount: {total_week_amount:.2f}")
        self.worksheet.update_acell(f"{week_column}3", f"Hours: {total_week_hours:.2f}")

        print("New row added successfully!")


    def add_income_with_index(self, total_amount, hours_worked):
        today = datetime.date.today()
        day_of_month = today.day
        week_of_month = (day_of_month - 1) // 7 + 1

        new_row = [today.strftime("%m/%d/%Y"), f"${total_amount}", hours_worked]

        week_column = chr(ord('A') + COLUMN_OFFSET + week_of_month) #clever way to get the correct columns for the week

        # batch clear
        self.worksheet.batch_clear([f'{week_column}2:{week_column}5'])
        self.worksheet.batch_clear([f'D7:D8'])

        self.worksheet.insert_row(new_row, index=self.sheet_info_dict.get("last_row"))

        # Increase the proper values
        self.sheet_info_dict.update({
            key: self.sheet_info_dict.get(key, 0) + value
            for key, value in {
                "amount_sum": total_amount,
                "hours_sum": hours_worked,
                "total_week_hours": hours_worked,
                "total_week_amount": total_amount,
                "days_worked": 1,
                "last_row": 1
            }.items()
        })

        self.sheet_info_dict.update({
            "week_avg_amount": self.sheet_info_dict["total_week_amount"]/self.sheet_info_dict["days_worked"],
            "week_avg_hours": self.sheet_info_dict["total_week_hours"]/self.sheet_info_dict["days_worked"]
        })

        week_vals = [
            f"Amount: {self.sheet_info_dict['total_week_amount']:.2f}",
            f"Hours: {self.sheet_info_dict['total_week_hours']:.2f}",
            f"Avg Amount: {self.sheet_info_dict['week_avg_amount']:.2f}",
            f"Avg Hours: {self.sheet_info_dict['week_avg_hours']:.2f}"
        ]

        time.sleep(.5)
        cell_list = self.worksheet.range(f'{week_column}2:{week_column}5')

        for i, cell in enumerate(cell_list):
            if i < len(week_vals):
                cell.value = week_vals[i]
            else:
                cell.value = ""  # Clear any remaining cells

        total_vals = [
            f"Total Amount: {self.sheet_info_dict['amount_sum']:.2f}",
            f"Total Hours: {self.sheet_info_dict['hours_sum']:.2f}"
        ]

        time.sleep(.5)
        total_list = self.worksheet.range(f'D7:D8')

        for i, cell in enumerate(total_list):
            if i < len(total_vals):
                cell.value = total_vals[i]
            else:
                cell.value = ''

        self.worksheet.update_cells(cell_list)
        self.worksheet.update_cells(total_list)

        # reset the weekly variables
        if week_of_month != self.sheet_info_dict.get("current_week"):
            print("welcome to a the new week!")
            self.sheet_info_dict["total_week_hours"] = 0
            self.sheet_info_dict["total_week_amount"] = 0
            self.sheet_info_dict["days_worked"] = 0

        self.write_to_sheet_info()
        print("Sucessfully added new income!")


    def del_income_with_index(self):
        if (self.sheet_info_dict["last_row"] <= 1):
            return

        today = datetime.date.today()

        day_of_month = today.day
        week_of_month = (day_of_month - 1) // 7 + 1

        self.sheet_info_dict["last_row"] = self.sheet_info_dict.get("last_row", 2) - 1

        _,amount_earned, hours_worked,*_ = self.worksheet.row_values(self.sheet_info_dict.get("last_row", 2))

        amount_earned = amount_earned.replace("$", "")
        
        self.sheet_info_dict.update({
            key: self.sheet_info_dict.get(key, 0) - value
            for key, value in {
                "amount_sum": float(amount_earned),
                "hours_sum": float(hours_worked),
                "total_week_hours": float(hours_worked),
                "total_week_amount": float(amount_earned),
                "days_worked": 1
            }.items()
        })

        if self.sheet_info_dict['days_worked'] >= 1:
            self.sheet_info_dict.update({
                "week_avg_amount": self.sheet_info_dict["total_week_amount"]/self.sheet_info_dict["days_worked"],
                "week_avg_hours": self.sheet_info_dict["total_week_hours"]/self.sheet_info_dict["days_worked"]
            })
        else:
            self.sheet_info_dict.update({
                "week_avg_amount": 0,
                "week_avg_hours": 0,
                "week_avg_amount": 0,
                "week_avg_hours": 0
            })
            # no previous values, clear the sheet
            if self.sheet_info_dict['amount_sum'] == 0 and self.sheet_info_dict['hours_sum'] == 0:
                self.worksheet.clear()

                with open("config.json", "r") as file:
                    config = json.load(file)
                
                column_names = config["column_names"]
                self.worksheet.append_row(column_names)
                return

        self.worksheet.delete_row(self.sheet_info_dict.get("last_row", 2))

        week_column = chr(ord('A') + COLUMN_OFFSET + week_of_month)
        self.worksheet.batch_clear([f'{week_column}2:{week_column}5'])

        week_vals = [
            f"Amount: {self.sheet_info_dict['total_week_amount']:.2f}",
            f"Hours: {self.sheet_info_dict['total_week_hours']:.2f}",
            f"Avg Amount: {self.sheet_info_dict['week_avg_amount']:.2f}",
            f"Avg Hours: {self.sheet_info_dict['week_avg_hours']:.2f}"
        ]

        cell_list = self.worksheet.range(f'{week_column}2:{week_column}5')

        for i, cell in enumerate(cell_list):
            cell.value = week_vals[i]

        self.worksheet.update_cells(cell_list)

        self.write_to_sheet_info()
        print("Sucessfully deleted recently added column")

if '__main__' == __name__:
    sa = gspread.service_account(filename="discord-connection.json")
    with open("data.json", "r") as f:
        sheet_info_dict = json.load(f)

    today = datetime.date.today()
    month = today.month
    month_str = today.strftime("%B")
    print(month_str)
    user = input("User: ")

    if month != 12:
        # open the year
        try:
            # sh = sa.open(f"{user} 2023")
            sh = sa.open("My sheet")
        except gspread.exceptions.SpreadsheetNotFound as e:
            print(f"Spreadsheet '{user} 2023' doesn't exist")
            # create and share the spreadsheet
            # sh = sa.create("Test spreadsheet")
            # sh.share(constants.EMAIL, perm_type='user', role='writer')
            print("Sucessfully created a new spreadsheet!")
            exit()
    else:
        # create new spreadsheet for the year
        print("created a new spreadsheet for the new year!")

    try: 
        worksheet = sh.worksheet(f"{month_str}")
    except gspread.exceptions.WorksheetNotFound as e:
        print(f"Worksheet {month_str} not found")
        # create the worksheet
        # worksheet = sh.add_worksheet(title=f"{month_str}", rows=1000, cols=28)
        print("created you bitch")


    # future = datetime.date(23, 1, 2)
    # future_str = future.strftime("%B %Y")
