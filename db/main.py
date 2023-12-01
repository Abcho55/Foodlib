from db_connection import create_db_connection, execute_query, execute_read_query

# Database credentials - replace with your own
host = "localhost"
user = "your_username"
password = "your_password"
database = "foodlib_db"

# Establish database connection
connection = create_db_connection(host, user, password, database)

# Sample insert query
insert_user_query = """
INSERT INTO users (username, email)
VALUES ('john_doe', 'john@example.com');
"""

execute_query(connection, insert_user_query)

# Sample read query
select_users_query = "SELECT * FROM users;"
users = execute_read_query(connection, select_users_query)

for user in users:
    print(user)
