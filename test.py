import json

def get_data() -> dict:
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError as e:
        print("File not found\n",e)
        exit()

def set_data(data: dict) -> dict:
    data["last_row"] = 0
    with open("data.json", "w") as f:
        json.dump(data, f)
    return data

def write_json(data: dict) -> dict:
    data["last_row"] += 1
    print(data)
    with open("data.json", "w") as f:
        json.dump(data, f)
    return data

def read_json():
        with open("data.json", "r") as f:
            data = json.load(f)
            print(data)

def main():
    data = get_data()
    try:
        ans = input("What do you want to do?\n"
                    "1. Reset last row\n"
                    "2. Increment last row\n"
                    "3. Read last row\n"
                    "Enter your choice (1, 2 or 3): ")
        choice = int(ans)
        if choice not in [1, 2, 3]:
            raise ValueError("Invalid choice. Please enter a number between 1 and 3.")

        # Execute the appropriate action based on the user's choice
        if choice == 1:
            data = set_data(data)
        elif choice == 2:
            data = write_json(data)
        else:
            read_json()
    except ValueError as e:
        print("Error:", e)
        exit()
        # Write your code to handle the ValueError here, if needed.
    except Exception as e:
        print("An error occurred:", e)
        exit()
    print("Sucessful!")

if __name__ == '__main__':
    print("hi")
