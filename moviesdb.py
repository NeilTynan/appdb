# Import Libraries
import pymysql
from neo4j import GraphDatabase
import calendar

# Set database connections to None to prevent them being referenced before assignment
conn = None
driver = None

# MySql Database connection -  Based off course materials (Topic 10 - Video 3)
def connect():
    global conn
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        db="appdbproj",
        cursorclass=pymysql.cursors.DictCursor
    )

# Neo4j Database connection - Based off course materials (Topic 11 - Video 3)
def conn_neo4j():
    global driver
    url = "neo4j://localhost:7687"
    driver = GraphDatabase.driver(url, auth=("neo4j", "neo4jneo4j"), max_connection_lifetime=1000)

# Display menu - Based off course materials (Q2.py) 
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

# View Directors Function 
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
    
    actors = cursor.fetchall()
    
    
    print(f"\n{'Actor':<30} {'DOB':<40} {'Gender':<30}")
    print("="*100)
    
    for row in actors:    
        print(f"{row['ActorName']:<30} {row['DOB']:<40} {row['ActorGender']:<30}")
    
    cursor.close()

    display_menu()


# Add Actor Function

def add_actor():
    global conn
    if not conn:
        connect()
    
    cursor = conn.cursor()
    
    while True:
        Actor_ID = input("Actor ID: ").strip()
        cursor.execute("select count(*) as valid from actor where ActorID = %s", (Actor_ID,))
        if cursor.fetchone()['valid'] > 0:
            print(f"*** Error *** {Actor_ID} already exists.")
        else:
            break
    Name = input("Name: ").strip()
    DOB = input("DOB: ").strip()
    Gender = input("Gender: ").strip()
    while True:
        Country_ID = input("Country ID: ").strip()
        cursor.execute("select count(*) as valid from country where CountryID = %s", (Country_ID,))
        if cursor.fetchone()['valid'] == 0:
            print(f"*** Error *** {Country_ID} does not exist.")
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


# View Studio Function
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
        studios = cursor.fetchall()
        cursor.close()
    
    print(f"\n{'StudioID':<15} {'StudioName':85}")
    print("="*100)
    
    for row in studios:    
        print(f"{row['StudioID']:<15} {row['StudioName']:<85}")

    display_menu()


def married_actor():
    global driver
    if not driver:
        conn_neo4j()
    if not conn:
        connect()
    
    actor_id = int(input("Enter Actor ID: ").strip())

    with driver.session() as session:
        query = """match (a:Actor {ActorID: $ActorID})-[r:MARRIED_TO]-(b:Actor)
                   return a.ActorID as ActorID1, b.ActorID as ActorID2"""
        married = session.run(query, ActorID=actor_id)
        actors = list(married)

        if not actors:
            print("This actor is not married.")
        else:
            actor1 = actors[0]["ActorID1"]
            actor2 = actors[0]["ActorID2"]

            cursor = conn.cursor()

            cursor.execute("select ActorID, ActorName from actor where ActorID = %s", (actor1,))
            actor1 = cursor.fetchone()
            cursor.execute("select ActorID, ActorName from actor where ActorID = %s", (actor2,))
            actor2 = cursor.fetchone()

            cursor.close()
            print(f"These actors are married: \n{actor1['ActorID']:<5} {actor1['ActorName']:<95} \n{actor2['ActorID']:<5} {actor2['ActorName']:<95}")

    display_menu()


def add_marriage():
    global driver
    if not driver:
        conn_neo4j()
    if not conn:
        connect()
    
    actor1 = int(input("Enter Actor ID: ").strip())
    actor2 = int(input("Enter Actor ID: ").strip())

    cursor = conn.cursor(pymysql.cursors.DictCursor) # referenced ChatGPT here - Prompt "Why are these two print statemnts not returning anything?"
    
    cursor.execute("select count(*) as valid from actor where ActorID = %s", (actor1,))
    act1 = cursor.fetchone()

    if act1['valid'] == 0:
        print(f"Actor {actor1} does not exist.")    
        return display_menu()
 
    cursor.execute("select count(*) as valid from actor where ActorID = %s", (actor2,))
    act2 = cursor.fetchone()

    if  act2['valid'] == 0:
        print(f"Actor {actor2} does not exist.")
        return display_menu()
    
    if actor1 == actor2:
        print("An actor cannot marry him/herself.")
        return display_menu()

    with driver.session() as session:
        query = """match (a:Actor {ActorID: $actor1})-[:MARRIED_TO]-(b:Actor)
                   return count(*) as married1"""

        marraiges1 = session.run(query, actor1=actor1, actor2=actor2)
        married1 = marraiges1.single()["married1"]

        query = """match (a:Actor {ActorID: $actor2})-[:MARRIED_TO]-(b:Actor)
                   return count(*) as married2"""
        
        marraiges2 = session.run(query, actor1=actor1, actor2=actor2)
        married2 = marraiges2.single()["married2"]

        if  married1:
            print(f"Actor {actor1} is already married.")
            return display_menu()
        elif married2:
            print(f"Actor {actor2} is already married.")
            return display_menu()
        else:
            create_query = """match (a:Actor {ActorID: $ActorID1}), (b:Actor {ActorID: $ActorID2})
                              create (a)-[:MARRIED_TO]->(b)"""
            session.run(create_query, ActorID1=actor1, ActorID2=actor2)
            print(f"Actor {actor1} is now married to Actor {actor2}.")
        
    cursor.close()
    display_menu()

# Display menu - Based off course materials (Q2.py) 

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