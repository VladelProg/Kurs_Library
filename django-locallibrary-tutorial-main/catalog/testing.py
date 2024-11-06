
import sqlite3
 
# Connecting to sqlite
connection_obj = sqlite3.connect('./django-locallibrary-tutorial-main/db.sqlite3')
 
# cursor object
cursor_obj = connection_obj.cursor()

# Add a new column to geek table
# del_column = "ALTER TABLE catalog_book DROP COLUMN UserName"
new_column = """ UPDATE catalog_rating
SET user = 3 
WHERE id = 3;"""
cursor_obj.execute(new_column)

# Display table

connection_obj.commit()
 
# Close the connection
connection_obj.close()