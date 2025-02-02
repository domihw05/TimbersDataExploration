#import modules and packages
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import matplotlib.font_manager as font_manager


def json_to_df(data):
    x = []
    y = []
    xg = []
    team = []
    result = []
    title = ""

    data_away = data['a']
    data_home = data['h']

    for idx in range(len(data_home)):
        for key in data_home[idx]:
            if key == 'X':
                x.append(data_home[idx][key])
            if key == 'Y':
                y.append(data_home[idx][key])
            if key == 'xG':
                xg.append(data_home[idx][key])
            if key == 'result':
                result.append(data_home[idx][key])
            if key == 'h_team':
                team.append(data_home[idx][key])
                title = data_home[idx][key]

    first_time = True
    for idx in range(len(data_away)):
        for key in data_away[idx]:
            if key == 'X':
                x.append(data_away[idx][key])
            if key == 'Y':
                y.append(data_away[idx][key])
            if key == 'xG':
                xg.append(data_away[idx][key])
            if key == 'result':
                result.append(data_away[idx][key])
            if key == 'a_team':
                team.append(data_away[idx][key])
                if first_time:
                    title += ' vs ' + data_away[idx][key]
                    first_time = False

    col_names = ['x','y','xg','team','result']
    df = pd.DataFrame([x,y,xg,team,result],index = col_names)
    df = df.T
    df = df.astype({'x':float,'y':float,'xg':float})

    return df, title

def parse_data():
    # scrape single game shots
    base_url = 'https://understat.com/match/'


    id = str(input(f'Please enter the match id: '))
    url = base_url + id
    url = 'https://understat.com/player/8418' #JM42

    res = requests.get(url)
    soup = BeautifulSoup(res.content,'lxml')

    # find scripts to find shots data (INSPECT)

    scripts = soup.find_all('script')

    # get only shots data

    #strings = scripts[1].string #MATCH
    strings = scripts[3].string #PLAYER

    print(strings)

    # strip symbols so we only have the json data

    ind_start = strings.index("('")+2
    ind_end = strings.index("')")

    json_data = strings[ind_start:ind_end]
    json_data = json_data.encode('utf8').decode('unicode_escape')

    # convert string to json format

    data = json.loads(json_data)  

    
    df, title = json_to_df(data)

    # Create the data frame
    return df, title

def print_shot_map(df, title):

    # Scale x and y coordinates properly
    df['x'] = df['x'] * 100
    df['y'] = df['y'] * 100



    # Black color
    background_color = '#0C0D0E'

    font_path = 'Fonts/Arvo-Regular.ttf'
    font_props = font_manager.FontProperties(fname=font_path)

    fig = plt.figure(figsize=(8,10))
    fig.patch.set_facecolor(background_color)

    ax1 = fig.add_axes([0,.7,1,.2]) # Top left, bottom left, width, height
    ax1.set_facecolor(background_color)
    ax1.set_xlim(0,1)
    ax1.set_ylim(0,1)

    # TITLE

    ax1.text(
        x=0.5,
        y=0.85,
        s=title,
        fontsize = 20,
        fontproperties = font_props,
        fontweight = 'bold',
        color = 'white',
        ha = 'center'
    )

    # GOAL VS NO GOAL

    ax1.text(
        x=0.15, 
        y=0.41, 
        s=f'Goal', 
        fontsize=10, 
        fontproperties=font_props, 
        color='white', 
        ha='right'
    )

    ax1.text(
        x=0.15, 
        y=0.31, 
        s=f'Home', 
        fontsize=10, 
        fontproperties=font_props, 
        color='white', 
        ha='right'
    )
    

    ax1.text(
        x=0.15, 
        y=0.21, 
        s=f'Away', 
        fontsize=10, 
        fontproperties=font_props, 
        color='white', 
        ha='right'
    )

    ax1.scatter(
        x=0.18, 
        y=0.44, 
        s=80, 
        color= background_color, 
        edgecolor='gold', 
        linewidth=1.6,
        alpha=.7
    )

    ax1.scatter(
        x=0.18, 
        y=0.34, 
        s=100, 
        color='red', 
        alpha=.7
    )

    ax1.scatter(
        x=0.18, 
        y=0.24, 
        s=100, 
        color='royalblue', 
        alpha=0.7
    )

    

    ax1.set_axis_off()


    ax2 = fig.add_axes([0.05,.25,.9,.5]) # Top left, bottom left, width, height
    ax2.set_facecolor(background_color)

    pitch = VerticalPitch(
        pitch_type='opta',
        half = True,
        pitch_color = background_color,
        pad_bottom=0.1,
        line_color = 'white',
        linewidth = 0.75,
        axis = True,
        label = True
    )

    pitch.draw(ax = ax2)

    team1 = df['team'][0]

    for x in df.to_dict(orient='records'):
        pitch.scatter(
            x['x'],
            x['y'],
            s=300 * x['xg'],
            color = 'red' if x['team'] == team1 else 'royalblue',
            ax = ax2,
            alpha = 0.7,
            linewidth = 1.6,
            edgecolor = 'gold' if x['result'] == 'Goal' else background_color
        )



    ax2.set_axis_off()

if __name__ == '__main__':
    df, title = parse_data()

    print_shot_map(df, title)

    plt.show()