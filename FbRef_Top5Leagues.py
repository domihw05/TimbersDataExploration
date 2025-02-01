from unidecode import unidecode
import pandas as pd
import numpy as np
import requests
from io import StringIO
import matplotlib.pyplot as plt

url = "https://fbref.com/en/comps/Big5/gca/players/Big-5-European-Leagues-Stats"


html_content = requests.get(url).text.replace('<!--','').replace('-->','')

players_data = pd.read_html(StringIO(html_content))

dfdata = df[1]
dfdata.head()

player_data = dfdata.drop(dfdata[dfdata.Age == 'Age'].index)

# Ensure 'Age' is numeric
player_data = player_data.astype({'Born':float,'SCA':float})

# Drop any NaN values (if conversion failed for some rows)
player_data = player_data.dropna(subset=['Born', 'SCA'])

# Plot again
plt.scatter(player_data['Born'], player_data['SCA'], color = 'blue', marker = 'o',label='Data Points')
plt.xlabel("Born")
plt.ylabel("SCA")
plt.title("Year Born versus SCA")
plt.legend()
plt.show()



