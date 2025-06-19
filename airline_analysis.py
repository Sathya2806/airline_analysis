import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('expanded_flight_data.csv')
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
import pandas as pd
import sqlite3

# Connect to the existing database
conn = sqlite3.connect('flights.db')

# Query: Number of delayed flights (arr_delay > 0) by carrier
query_delayed_by_carrier = """
SELECT 
  carrier,
  COUNT(*) AS delayed_flights_count,
  AVG(arr_delay) AS avg_delay_for_delayed_flights
FROM flights
WHERE arr_delay > 0
GROUP BY carrier
ORDER BY delayed_flights_count DESC;
"""
print("Delayed Flights Stats by Carrier:")
print(pd.read_sql_query(query_delayed_by_carrier, conn))
print("\n")

# Query: Number of cancelled flights by carrier
query_cancelled_by_carrier = """
SELECT 
  carrier,
  COUNT(*) AS cancelled_flights_count
FROM flights
WHERE status = 'Cancelled'
GROUP BY carrier
ORDER BY cancelled_flights_count DESC;
"""
print("Cancelled Flights by Carrier:")
print(pd.read_sql_query(query_cancelled_by_carrier, conn))
print("\n")

# Query: Filter and show details of delayed flights (arr_delay > 0)
query_delayed_flights_detail = """
SELECT flight_id, carrier, origin, destination, arr_delay, status
FROM flights
WHERE arr_delay > 0 AND status <> 'Cancelled'
ORDER BY arr_delay DESC
LIMIT 20;
"""
print("Sample Delayed Flights (arr_delay > 0, not cancelled):")
print(pd.read_sql_query(query_delayed_flights_detail, conn))
print("\n")

# Query: Filter and show details of cancelled flights
query_cancelled_flights_detail = """
SELECT flight_id, carrier, origin, destination, arr_delay, status
FROM flights
WHERE status = 'Cancelled'
ORDER BY flight_id DESC
LIMIT 20;
"""
print("Sample Cancelled Flights:")
print(pd.read_sql_query(query_cancelled_flights_detail, conn))
print("\n")

conn.close()

import numpy as np
import matplotlib.pyplot as plt

# Example data: replace with your actual counts
statuses = ['Cancelled', 'On-time', 'Delayed']
delta_counts = [12, 15, 8]
united_counts = [10, 8, 6]
american_counts = [11, 5, 5]

# Bar width and positions
bar_width = 0.25
x = np.arange(len(statuses))

# Plotting
fig, ax = plt.subplots(dpi=120)
rects1 = ax.bar(x - bar_width, delta_counts, bar_width, label='Delta')
rects2 = ax.bar(x, united_counts, bar_width, label='United')
rects3 = ax.bar(x + bar_width, american_counts, bar_width, label='American')

# Labels and title
ax.set_xlabel('Flight Status')
ax.set_ylabel('Number of Flights')
ax.set_title('Flight Status Distribution by Airline')
ax.set_xticks(x)
ax.set_xticklabels(statuses)
ax.legend()

# Annotate bars with counts
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

plt.tight_layout()
plt.show()

