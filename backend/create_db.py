import mysql.connector

mydb = mysql.connector.connect(
	host="mysql-db",
	user="root",
	passwd = "admin",
	)
	

my_cursor = mydb.cursor()

my_cursor.execute("CREATE DATABASE PTR")



    