
import sqlite3
 
# Connecting to sqlite
connection_obj = sqlite3.connect('db.sqlite3')
 
# cursor object
cursor_obj = connection_obj.cursor()

# Add a new column to geek table
# del_column = "ALTER TABLE catalog_book DROP COLUMN UserName"
new_column = """   UPDATE catalog_book
   SET path_to_file = '/books/text_onegin.txt'
   WHERE id = 1;"""
cursor_obj.execute(new_column)

# Display table
data = cursor_obj.execute("SELECT * FROM catalog_book")
print('GEEK Table:')
for row in data:
    print(row)
 
connection_obj.commit()
 
# Close the connection
connection_obj.close()