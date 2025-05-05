import pymysql
import calendar

conn = None

def connect():
    global conn
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        db="appdbproj",
        cursorclass=pymysql.cursors.DictCursor
    )

def display_menu():
    print("\nMENU")
    print("=" * 4)
    print("1 - View Directors & Films")
    print("2 - View Actors by Month of Birth")
    print("3 - Add New Actor")
    print("4 - View Married Actors")
    print("5 - Add Actor Marriage")
    print("6 - View Studios")
    print("7 - Exit Application")

def view_directors():
    global conn
    if not conn:
        connect()

    name = input("Enter Director Name: ").strip()

    query = """select d.DirectorName, f.FilmName, s.StudioName 
               from director d 
               join film f on d.DirectorID = f.FilmDirectorID 
               join studio s on f.FilmStudioID = s.StudioID
               where d.DirectorName like %s
               order by d.DirectorName asc;"""
        
    director = f"%{name}%"  
    cursor = conn.cursor()
    cursor.execute(query, (director,))
    
    # Referenced ChatGPT - "How to clean up the results from this data query"
    print(f"\n{'Director':<30} {'Film':<40} {'Studio':<30}")
    print("="*100)
        
    found = False
    for x in cursor:
        found=True
        print(f"{x['DirectorName']:<30} {x['FilmName']:<40} {x['StudioName']:<30}")
            
    if not found:
        print("No directors found of that name found")
        
    cursor.close()

    display_menu()


def actors_dob():
    global conn
    if not conn:
        connect()

    month = input("Enter Month: ").strip()
    
    num = None
    if month.isdigit():
        num = int(month)
        if not (1 <= int(num) <= 12):
            return
    else:
        abrv = {calendar.month_abbr[i]: i for i in range(1, 13)}
        if month in abrv:
            month = abrv[month]
        else:
            print("Invalid entry. Use first 3 letters in the correct case (e.g. Jan).")
            return

    query = """select ActorName, date_format(ActorDOB, '%%Y-%%c-%%e') as DOB, ActorGender 
               from actor
               where Month(ActorDOB) = %s
               order by ActorName asc;"""
        
    cursor = conn.cursor()
    cursor.execute(query, (month,))
    
    results = cursor.fetchall()
    
    
    print(f"\n{'Actor':<30} {'DOB':<40} {'Gender':<30}")
    print("="*100)
    
    for row in results:    
        print(f"{row['ActorName']:<30} {row['DOB']:<40} {row['ActorGender']:<30}")
    
    cursor.close()

    display_menu()


def add_actor():
    global conn
    if not conn:
        connect()
    
    cursor = conn.cursor()
    
    while True:
        Actor_ID = input("Actor ID: ").strip()
        cursor.execute("SELECT COUNT(*) as count from actor where ActorID = %s", (Actor_ID,))
        if cursor.fetchone()['count'] > 0:
            print("*** Error *** Actor ID already exists.")
        else:
            break
    Name = input("Name: ").strip()
    DOB = input("DOB: ").strip()
    Gender = input("Gender: ").strip()
    while True:
        Country_ID = input("Country ID: ").strip()
        cursor.execute("SELECT COUNT(*) as count from country where CountryID = %s", (Country_ID,))
        if cursor.fetchone()['count'] == 0:
            print("*** Error *** Country ID does not exist.")
        else:
            break

    query = "insert into actor (ActorID, ActorName, ActorDOB, ActorGender, ActorCountryID) values (%s, %s, %s, %s, %s)"
    val = (Actor_ID, Name, DOB, Gender, Country_ID)
        
    cursor = conn.cursor()
    try:
        cursor.execute(query, val)
        conn.commit()
        print("Actor added successfully.")
    except Exception as e:
        print("Error inserting actor:", e)
        conn.rollback()
    finally:
        cursor.close()

    display_menu()

# Referenced ChatGPT - "How to ensure that in a Python file referencing a MySQL database any new entries in the MySQL database will not be shown in the results of the python file, after the first time the user pulls across the results, until the user exits and restarts the application"

cache = None

def view_studio():
    global conn, cache
    
    if cache is None:
        if not conn:
            connect()

        query = """select StudioID, StudioName 
                   from studio
                   order by StudioID asc;"""
            
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
    
    
    print(f"\n{'StudioID':<15} {'StudioName':85}")
    print("="*100)
    
    for row in results:    
        print(f"{row['StudioID']:<15} {row['StudioName']:<85}")

    display_menu()


def main():
    display_menu()
    
    while True:
        choice = input("Enter choice: ")
        
        if choice == "1":
            view_directors()
        elif choice == "2":
            actors_dob()
        elif choice == "3":
            add_actor()
        elif choice == "4":
            married_actor()
        elif choice == "5":
            add_marriage()
        elif choice == "6":
            view_studio()
        elif choice == "7":
            print("Exiting application.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()