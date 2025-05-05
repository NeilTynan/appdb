import pymysql

conn = None


def connect():
	global connect
	conn = pymysql.connect(host="localhost", user="root", password="root", db="school", cursorclass=pymysql.cursors.DictCursor)



def main():
	array = []

	display_menu()
	
	while True:
		choice = input("Enter choice: ")
		
		if (choice == "1"):
			print("View Directors & Films")
			display_menu()
		elif (choice == "2"):
			print(array)
			display_menu()
		elif (choice == "3"):
			find_gt_in_array(array)
			display_menu()
		elif (choice == "7"):
			break;
		else:
			display_menu()
			


def display_menu():
    print("")
    print("MENU")
    print("=" * 4)
    print("1 - View Directors & Films")
    print("2 - View Actors by Month of Birth")
    print("3 - Add New Actor")
    print("4 - View Married Actors")
    print("5 - Add Actor Marriage")
    print("6 - View Studios")
    print("7 - Exit Application")

if __name__ == "__main__":
	main()
