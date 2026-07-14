import sqlite3
import pandas as pd

conn = sqlite3.connect('scholars.db')
df = pd.read_sql_query('SELECT * FROM scholars', conn)
conn.close()

df.to_csv('data/schwarzman_scholars_dataset.csv', index=False)
