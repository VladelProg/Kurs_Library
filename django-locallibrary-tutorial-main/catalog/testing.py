
import sqlite3
 
# Connecting to sqlite
connection_obj = sqlite3.connect('db.sqlite3')
 
# cursor object
cursor_obj = connection_obj.cursor()

# Add a new column to geek table
# del_column = "ALTER TABLE catalog_book DROP COLUMN UserName"
new_column = """ INSERT INTO catalog_rating (id, book_id, rating, created_at) 
VALUES (3, 2, 2, '2024-10-17 12:38:39.201375');"""
cursor_obj.execute(new_column)

# Display table

connection_obj.commit()
 
# Close the connection
connection_obj.close()