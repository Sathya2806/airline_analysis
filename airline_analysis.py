import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('/content/expanded_flight_data.csv')
print(df.head())
df['arr_delay'] = df['arr_delay'].fillna(0)
df['status'] = df['status'].fillna('Unknown')
conn = sqlite3.connect('flights.db')
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS flights")
cursor.execute("""
CREATE TABLE flights (
    flight_id INTEGER PRIMARY KEY,
    carrier TEXT,
    origin TEXT,
    destination TEXT,
    status TEXT,
    arr_delay INTEGER
)
""")
df.to_sql('flights', conn, if_exists='append', index=False)
conn.commit()
query_on_time = """
SELECT 
  (COUNT(CASE WHEN status = 'On-Time' THEN 1 END) * 100.0) / COUNT(*) AS on_time_arrival_rate
FROM flights;
"""
print("On-Time Arrival Rate:")
print(pd.read_sql_query(query_on_time, conn))
query_avg_delay = """
SELECT AVG(arr_delay) AS avg_delay_duration FROM flights;
"""
print("Average Delay Duration:")
print(pd.read_sql_query(query_avg_delay, conn))
query_cancel = """
SELECT 
  (COUNT(CASE WHEN status = 'Cancelled' THEN 1 END) * 100.0) / COUNT(*) AS cancellation_rate
FROM flights;
"""
print("Cancellation Rate:")
print(pd.read_sql_query(query_cancel, conn))
query_route_delay = """
SELECT 
  origin, destination, AVG(arr_delay) AS avg_route_delay
FROM flights
GROUP BY origin, destination;
"""
print("Route Delay Index:")
route_delay_df = pd.read_sql_query(query_route_delay, conn)
print(route_delay_df)
carrier_on_time = df[df['status'] == 'On-Time'].groupby('carrier').size()
total_flights = df.groupby('carrier').size()
punctuality = (carrier_on_time / total_flights) * 100
punctuality.plot(kind='bar', figsize=(10, 6), color='skyblue')
plt.title('Carrier Punctuality (%)')
plt.ylabel('On-Time Arrival Rate')
plt.xlabel('Carrier')
plt.xticks(rotation=45)
plt.show()
# pivot_table = route_delay_df.pivot("origin", "destination", "avg_route_delay") # Old code
pivot_table = route_delay_df.pivot_table(index="origin", columns="destination", values="avg_route_delay")
plt.figure(figsize=(12,8))
sns.heatmap(pivot_table, annot=True, cmap="coolwarm", fmt=".1f")
plt.title("Average Delay per Route (in minutes)")
plt.show()
conn.close()