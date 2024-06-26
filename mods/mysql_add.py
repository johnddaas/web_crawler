import mysql.connector

def insert_data(data):
    connection = mysql.connector.connect(
        host='host_ip',
        user='DB_user',
        password='DB_password',
        database='database'
    )
    cursor = connection.cursor()

    inserted_count = 0
    for item in data:
        cursor.execute("SELECT * FROM housing WHERE 名稱 = %s", (item[1],))
        if not cursor.fetchone():

            cursor.execute("INSERT INTO house.housing (價格, 名稱, 地址, 坪數, 屋齡, 樓層, 車位) VALUES (%s, %s, %s, %s, %s, %s, %s)", item)
            inserted_count += 1


    connection.commit()
    cursor.close()
    connection.close()

    return inserted_count
