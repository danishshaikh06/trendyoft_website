import mysql.connector

# Replace with your Railway credentials
conn = mysql.connector.connect(
    host="tramway.proxy.rlwy.net",
    port=46519,
    user="root",
    password="aovRSZDWQkuabXAaqkVVgRKrTqHWySPf",
    database="railway"
)

# Cursor to execute queries
cursor = conn.cursor()
cursor.execute("SHOW TABLES")

print("📦 Tables in Railway DB:")
for (table_name,) in cursor.fetchall():
    print(" -", table_name)

cursor.close()
conn.close()