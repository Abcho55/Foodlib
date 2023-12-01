from db_connection import create_db_connection, execute_query

# Database credentials - replace with your own
host = "localhost"
user = "your_username"
password = "your_password"
database = "foodlib_db"

connection = create_db_connection(host, user, password, database)

# SQL queries to create tables
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE
);
"""

create_recipes_table = """
CREATE TABLE IF NOT EXISTS recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    cooking_time INT
);
"""

# Execute table creation queries
execute_query(connection, create_users_table)
execute_query(connection, create_recipes_table)