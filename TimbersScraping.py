import numpy as np
import requests
import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt

url = "https://fbref.com/en/squads/d076914e/Portland-Timbers-Stats"

html_content = requests.get(url).text.replace('<!--','').replace('-->','')

players_data = pd.read_html(StringIO(html_content))

players_data = players_data[0]

players_data.columns = players_data.columns.droplevel(0)

summary_data = players_data[30:]

players_data = players_data[0:30]

cols = players_data.columns.to_list()
count = 0
for i in range(len(cols)):
    if cols[i] == 'G+A':
        count += 1
        if count == 2:  # Change only the SECOND occurrence
            cols[i] = 'G+A_Per90'

# Step 3: Assign the updated column names
players_data.columns = cols

#Now, lets plot some squad statistics.

# Clear figures and axes

plt.clf()
plt.cla()


# Filter out NAs

players_data = players_data.dropna(axis = 0, how = 'any',subset = ["Min","G+A"])

# Ensure 'Min' and 'G+A' are numeric

players_data = players_data.astype({'Min':float,'G+A':float,'Player':str})

# Use matplotlib to plot

plt.plot(players_data['Min'], players_data['G+A'],color = 'blue',marker = 'o',linestyle = '',label='Data Points')

#NEED TO FIGURE OUT TWO COLUMNS WITH SAME NAME
print(players_data.loc[0,'G+A'])


for i in range(27):
  #print(players_data.loc[i,'G+A'])
  if (players_data.loc[i,'G+A'] >= 13.0):  # Adjust as needed
    plt.text(players_data.loc[i,'Min'], players_data.loc[i,'G+A'], players_data.loc[i,'Player'], fontsize=9, ha='right', color='red')

plt.xlabel("Min")
plt.ylabel("G+A")
plt.title("Year Born versus SCA")
plt.show()
