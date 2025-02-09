import psycopg2
from tabulate import tabulate
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

load_dotenv()
# Database connection settings
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def print_banner():
    print(Fore.CYAN + "=" * 40)
    print(Fore.YELLOW + "     🕹️  Personal Data Manager  🕹️ ")
    print(Fore.CYAN + "=" * 40)


def print_main_menu():
    print(Fore.GREEN + " [1] " + Fore.WHITE + "📥 Add Data")
    print(Fore.BLUE + " [2] " + Fore.WHITE + "📜 View Data")
    print(Fore.MAGENTA + " [3] " + Fore.WHITE + "✏️  Edit Personal Info")
    print(Fore.CYAN + " [4] " + Fore.WHITE + "🔍 Search Data")
    print(Fore.YELLOW + " [5] " + Fore.WHITE + "📂 Export Data to JSON")
    print(Fore.RED + " [6] " + Fore.WHITE + "🚪 Exit")
    print(Fore.CYAN + "=" * 40)


def print_add_menu():
    print(Fore.GREEN + " [1] " + Fore.WHITE + "👤 Add Personal Info")
    print(Fore.GREEN + " [2] " + Fore.WHITE + "💡 Add Project")
    print(Fore.GREEN + " [3] " + Fore.WHITE + "📅 Add Daily Log")
    print(Fore.GREEN + " [4] " + Fore.WHITE + "🔖 Add Bookmark")
    print(Fore.GREEN + " [5] " + Fore.WHITE + "✅ Add Task")
    print(Fore.RED + " [6] " + Fore.WHITE + "🔙 Back to Main Menu")
    print(Fore.CYAN + "=" * 40)


def clear_terminal():
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For Unix-based systems (Linux/macOS)
    else:
        os.system('clear')


# Connect to PostgresSQL
def connect_db():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )


# Insert into personal_info
def insert_personal_info():
    name = input("Enter your name: ")
    age = input("Enter your age: ")
    bio = input("Enter a short bio: ")

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO personal_info (name, age, bio) VALUES (%s, %s, %s)", (name, age, bio))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Personal info added!")


# Insert into projects
def insert_project():
    title = input("Enter project title: ")
    description = input("Enter project description: ")
    technologies = input("Enter technologies used (comma-separated): ").split(",")

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO projects (title, description, technologies) VALUES (%s, %s, %s)",
                (title, description, technologies))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Project added!")


# Insert into daily logs
def insert_daily_log():
    entry = input("Write your journal entry: ")

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO daily_logs (entry) VALUES (%s)", (entry,))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Daily log added!")


# Insert into bookmarks
def insert_bookmark():
    title = input("Enter bookmark title: ")
    url = input("Enter URL: ")
    tags = input("Enter tags (comma-separated): ").split(",")

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO bookmarks (title, url, tags) VALUES (%s, %s, %s)", (title, url, tags))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Bookmark added!")


# Insert into tasks
def insert_task():
    task_name = input("Enter task name: ")
    due_date = input("Enter due date (YYYY-MM-DD) or leave blank: ")
    status = "TODO"

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (task_name, due_date, status) VALUES (%s, %s, %s)",
                (task_name, due_date or None, status))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Task added!")


# View data from any table
def view_data(table):
    clear_terminal()
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()

    if rows:
        print(tabulate(rows, headers=[desc[0] for desc in cur.description], tablefmt="grid"))
    else:
        print("No data found.")

    cur.close()
    conn.close()


# Edit personal info by ID
def edit_personal_info():
    view_data("personal_info")
    edit_id = input("Enter the ID of the record to edit: ")
    new_name = input("Enter the new name: ")
    new_age = input("Enter the new age: ")
    new_bio = input("Enter the new bio: ")

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("UPDATE personal_info SET name = %s, age = %s, bio = %s WHERE id = %s",
                (new_name, new_age, new_bio, edit_id))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Personal info updated!")


# Export data to JSON
def export_data():
    conn = connect_db()
    cur = conn.cursor()

    # Fetch all table names
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = [table[0] for table in cur.fetchall()]

    all_data = {}

    for table in tables:
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]

        # Convert rows into dictionaries
        table_data = []
        for row in rows:
            row_dict = {}
            for i, value in enumerate(row):
                if isinstance(value, datetime):
                    row_dict[column_names[i]] = value.isoformat()
                else:
                    row_dict[column_names[i]] = value
            table_data.append(row_dict)

        all_data[table] = table_data  # Store each table's data

    cur.close()
    conn.close()

    # Write to JSON file
    with open("database_export.json", "w") as json_file:
        json.dump(all_data, json_file, indent=4)

    print("✅ All tables exported successfully to database_export.json!")


# Search data in any table
def search_data():
    table = input("Enter table name to search (personal_info, projects, daily_logs, bookmarks, tasks): ")
    # print the columns of the table
    view_data(table)

    column = input(f"Enter the column name to search in {table}: ")
    keyword = input(f"Enter the keyword to search in {column}: ")

    conn = connect_db()
    cur = conn.cursor()

    query = f"SELECT * FROM {table} WHERE {column} ILIKE %s"
    cur.execute(query, (f"%{keyword}%",))
    rows = cur.fetchall()

    if rows:
        print(tabulate(rows, headers=[desc[0] for desc in cur.description], tablefmt="grid"))
    else:
        print("No matching data found.")

    cur.close()
    conn.close()


# CLI Menu
def main():
    while True:
        print_banner()
        print_main_menu()

        choice = input(Fore.YELLOW + "💾 Choose an option: " + Style.BRIGHT)

        if choice == "1":  # Add Data Submenu
            while True:
                clear_terminal()
                print_banner()
                print_add_menu()
                sub_choice = input(Fore.YELLOW + "➕ Choose what to add: " + Style.BRIGHT)

                if sub_choice == "1":
                    insert_personal_info()
                elif sub_choice == "2":
                    insert_project()
                elif sub_choice == "3":
                    insert_daily_log()
                elif sub_choice == "4":
                    insert_bookmark()
                elif sub_choice == "5":
                    insert_task()
                elif sub_choice == "6":
                    clear_terminal()
                    break
                else:
                    print(Fore.RED + "❌ Invalid choice. Try again.")

        elif choice == "2":
            print(Fore.BLUE + "📜 Table names:")
            print(Fore.CYAN + "(personal_info, projects, daily_logs, bookmarks, tasks)" + Style.BRIGHT)
            table_name = input(Fore.BLUE + "📜 Enter table name to view: " + Style.BRIGHT)
            view_data(table_name)
        elif choice == "3":
            edit_personal_info()
        elif choice == "4":
            search_data()
        elif choice == "5":
            export_data()
        elif choice == "6":
            print(Fore.RED + "\n👋 Goodbye, see you next time!\n")
            break
        else:
            print(Fore.RED + "❌ Invalid choice. Please try again.\n")


if __name__ == "__main__":
    main()
