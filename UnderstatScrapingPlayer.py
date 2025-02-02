#import modules and packages
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import streamlit as st

import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import matplotlib.font_manager as font_manager


def json_to_df(data):
    minute = []
    player = []
    h_a = []
    situation = []
    season = []
    shotType = []
    match_id = []
    h_team = []
    a_team = []
    h_goals = []
    a_goals = []
    player_assisted = []
    lastAction = []
    x = []
    y = []
    xg = []
    result = []

    for idx in range(len(data)):
        for key in data[idx]:
            if key == 'X':
                x.append(data[idx][key])
            if key == 'Y':
                y.append(data[idx][key])
            if key == 'xG':
                xg.append(data[idx][key])
            if key == 'result':
                result.append(data[idx][key])
            if key == 'shotType':
                shotType.append(data[idx][key])
            if key == 'minute':
                minute.append(data[idx][key])
            if key == 'player':
                player.append(data[idx][key])
            if key == 'h_a':
                h_a.append(data[idx][key])
            if key == 'situation':
                situation.append(data[idx][key])
            if key == 'season':
                season.append(data[idx][key])
            if key == 'match id':
                match_id.append(data[idx][key])
            if key == 'h_team':
                h_team.append(data[idx][key])
            if key == 'a_team':
                a_team.append(data[idx][key])
            if key == 'h_goals':
                h_goals.append(data[idx][key])
            if key == 'a_goals':
                a_goals.append(data[idx][key])
            if key == 'player_assisted':
                player_assisted.append(data[idx][key])
            if key == 'lastAction':
                lastAction.append(data[idx][key])

    col_names = ['minute','result','x','y','xg','player','h_a','situation',
                 'season','shotType','match_id','h_team','a_team','h_goals',
                 'a_goals', 'player_assisted', 'lastAction']
    df = pd.DataFrame([minute,result, x,y,xg,player,h_a,situation,
                       season,shotType,match_id,h_team, a_team,h_goals, 
                       a_goals, player_assisted, lastAction],index = col_names)
    df = df.T
    df = df.astype({'x':float,'y':float,'xg':float})

    return df

def parse_data():
    # scrape single game shots
    base_url = 'https://understat.com/player/'


    #id = str(input(f'Please enter the player id: '))
    #url = base_url + id
    url = 'https://understat.com/player/8418' #JM42

    res = requests.get(url)
    soup = BeautifulSoup(res.content,'lxml')

    # find scripts to find shots data (INSPECT)

    scripts = soup.find_all('script')

    # get only shots data

    #strings = scripts[1].string #MATCH
    strings = scripts[3].string #PLAYER

    # strip symbols so we only have the json data

    ind_start = strings.index("('")+2
    ind_end = strings.index("')")

    json_data = strings[ind_start:ind_end]
    json_data = json_data.encode('utf8').decode('unicode_escape')

    # convert string to json format

    data = json.loads(json_data)  

    
    df = json_to_df(data)

    # Create the data frame
    return df

def print_shot_map(df):

    # Scale x and y coordinates properly
    df['x'] = df['x'] * 100
    df['y'] = df['y'] * 100

    player_name = df['player'][0]

    # Black color
    background_color = '#0C0D0E'

    font_path = 'Fonts/Poppins/Poppins-Medium.ttf'
    font_props = font_manager.FontProperties(fname=font_path)

    fig = plt.figure(figsize=(8,12))
    fig.patch.set_facecolor(background_color)

    ax1 = fig.add_axes([0,.7,1,.2]) # Top left, bottom left, width, height
    ax1.set_facecolor(background_color)
    ax1.set_xlim(0,1)
    ax1.set_ylim(0,1)

    # TITLE

    # PLAYER NAME
    ax1.text(
        x=0.5,
        y=0.9,
        s=player_name,
        fontsize = 25,
        fontproperties = font_props,
        fontweight = 'bold',
        color = 'white',
        ha = 'center'
    )

    # PLAYER
    ax1.text(
        x=0.5,
        y=0.75,
        s=f'Career Shot Chart',
        fontsize = 16,
        fontproperties = font_props,
        fontweight = 'bold',
        color = 'white',
        ha = 'center'
    )

    ax1.text(
        x=0.25,
        y=0.5,
        s=f'Low Quality Chance',
        fontsize = 12,
        fontproperties = font_props,
        fontweight = 'bold',
        color = 'white',
        ha = 'center'
    )

    ax1.scatter(
        x = 0.37,
        y = 0.53,
        s = 100,
        color = background_color,
        edgecolor = 'white',
        linewidth = 0.8
    )

    ax1.scatter(
        x = 0.42,
        y = 0.53,
        s = 200,
        color = background_color,
        edgecolor = 'white',
        linewidth = 0.8
    )
    ax1.scatter(
        x = 0.48,
        y = 0.53,
        s = 300,
        color = background_color,
        edgecolor = 'white',
        linewidth = 0.8
    )
    ax1.scatter(
        x = 0.54,
        y = 0.53,
        s = 400,
        color = background_color,
        edgecolor = 'white',
        linewidth = 0.8
    )
    ax1.scatter(
        x = 0.6,
        y = 0.53,
        s = 500,
        color = background_color,
        edgecolor = 'white',
        linewidth = 0.8
    )

    ax1.text(
        x=0.75,
        y=0.5,
        s=f'High Quality Chance',
        fontsize = 12,
        fontproperties = font_props,
        fontweight = 'bold',
        color = 'white',
        ha = 'center'
    )

    # GOAL VS NO GOAL

    ax1.text(
        x=0.45, 
        y=0.27, 
        s=f'Goal', 
        fontsize=10, 
        fontproperties=font_props, 
        color='white', 
        ha='right'
    )
    ax1.scatter(
        x=0.47, 
        y=0.3, 
        s=100, 
        color='Green', 
        edgecolor='white', 
        linewidth=.8,
        alpha=.7
    )


    ax1.scatter(
        x=0.53, 
        y=0.3, 
        s=100, 
        color=background_color, 
        edgecolor='white', 
        linewidth=.8
    )

    ax1.text(
        x=0.55, 
        y=0.27, 
        s=f'No Goal', 
        fontsize=10, 
        fontproperties=font_props, 
        color='white', 
        ha='left'
    )

    ax1.set_axis_off()


    ax2 = fig.add_axes([0.05,.27,.9,.5]) # Top, left, width, height
    ax2.set_facecolor(background_color)

    pitch = VerticalPitch(
        pitch_type='opta',
        half = True,
        pitch_color = background_color,
        pad_bottom=0.5,
        line_color = 'white',
        linewidth = 0.75,
        axis = True,
        label = True
    )

    pitch.draw(ax = ax2)

    for x in df.to_dict(orient='records'):
        pitch.scatter(
            x['x'],
            x['y'],
            s=300 * x['xg'],
            color = 'green' if x['result'] == 'Goal' else background_color,
            ax = ax2,
            alpha = 0.7,
            linewidth = 0.8,
            edgecolor = 'white'
        )

    ax2.set_axis_off()

    # Toggle only 2024 season
    #df = df[df['season'] == '2024']

    total_shots = df.shape[0]
    total_goals = df[df['result'] == 'Goal'].shape[0]
    total_xG = df['xg'].sum()
    xG_per_shot = total_xG / total_shots

    ax3 = fig.add_axes([0,.2,1,.05]) # Top left, bottom left, width, height
    ax3.set_facecolor(background_color)

    ax3.text(x=0.25,y=0.6,s='Shots',fontsize = 20, fontproperties = font_props,
         fontweight='bold',color='white',ha = 'center')
    
    ax3.text(x = 0.25,y=0.1, s=f"{total_shots}",fontsize=16,
            fontproperties = font_props,color='green',ha='center')

    ax3.text(x=0.42,y=0.6,s='Goals',fontsize = 20, fontproperties = font_props,
            fontweight='bold',color='white',ha = 'center')
    ax3.text(x = 0.42,y=0.1, s=f"{total_goals}",fontsize=16,
            fontproperties = font_props,color='green',ha='center')

    ax3.text(x=0.55,y=0.6,s='xG',fontsize = 20, fontproperties = font_props,
            fontweight='bold',color='white',ha = 'center')
    ax3.text(x = 0.55,y=0.1, s=f"{total_xG:.2f}",fontsize=16,
            fontproperties = font_props,color='green',ha='center')

    ax3.text(x=0.69,y=0.6,s='xG/Shot',fontsize = 20, fontproperties = font_props,
            fontweight='bold',color='white',ha = 'center')
    ax3.text(x = 0.69,y=0.1, s=f"{xG_per_shot:.2f}",fontsize=16,
            fontproperties = font_props,color='green',ha='center')
    
    goals_only = df[df['result'] == 'Goal']
    top_assisters = goals_only['player_assisted'].value_counts().head(5)
    top_assists = top_assisters.tolist()
    top_assisters = top_assisters.index.tolist()

    ax3.text(x=0.5,y=-1,s='Top Assisters',fontsize = 20, fontproperties = font_props,
            fontweight='bold',color='white',ha = 'center')

    for idx in range(3):
        # Only print if valid index
        if idx < len(top_assisters): 
            name = top_assisters[idx]
            assists = top_assists[idx]

            ax3.text(x = 0.365,y=-1.5 - (idx*0.4), s=f"{idx+1}. {name} - {assists:.0f} assists",fontsize=12,
                fontproperties = font_props,color='white',ha='left')
            
    ax3.set_axis_off()

    #STREAMLIT SHIT
    #st.pyplot(fig)

def app():
    # Streamlit UI
    st.title("Player Assist Visualization")

    player_id = st.text_input("Enter Player ID")
    season = st.selectbox("Select Season", ["2021", "2022", "2023"])

    if st.button("Generate Visualization"):
        data = parse_data()

        print_shot_map(data)

if __name__ == '__main__':
    df = parse_data()

    print_shot_map(df)

    plt.savefig("player_visualization.png", dpi=300)  # Higher dpi for better quality
    plt.close()  # Close the figure to free memory
    #app()
