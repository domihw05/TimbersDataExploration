import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch


df = pd.read_csv('erling_haaland_2022_understat.csv')


# Scale x and y coordinates properly
df['X'] = df['X'] * 100
df['Y'] = df['Y'] * 100

total_shots = df.shape[0]
total_goals = df[df['result'] == 'Goal'].shape[0]
total_xG = df['xG'].sum()
xG_per_shot = total_xG / total_shots
points_average_distance = df['X'].mean()
actual_average_distance = 120 - (df['X'] * 1.2).mean()

# Creating top section of graph

# Black color
background_color = '#0C0D0E'

import matplotlib.font_manager as font_manager

font_path = 'Fonts/Arvo-Regular.ttf'
font_props = font_manager.FontProperties(fname=font_path)

fig = plt.figure(figsize=(8,12))
fig.patch.set_facecolor(background_color)

ax1 = fig.add_axes([0,.7,1,.2]) # Top left, bottom left, width, height
ax1.set_facecolor(background_color)
ax1.set_xlim(0,1)
ax1.set_ylim(0,1)

ax1.text(
    x=0.5,
    y=0.85,
    s='Erling Haaland',
    fontsize = 20,
    fontproperties = font_props,
    fontweight = 'bold',
    color = 'white',
    ha = 'center'
)

ax1.text(
    x=0.5,
    y=0.75,
    s=f'All shots in the Premier League 2022-23',
    fontsize = 14,
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

# Create scatter points
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
    color='red', 
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

# PITCH

ax2 = fig.add_axes([0.05,.25,.9,.5]) # Top left, bottom left, width, height
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

ax2.scatter(x = 90, y = points_average_distance,
            s = 100, color = 'white', linewidth = 0.8)
ax2.plot([90,90],[100,points_average_distance], color = 'white', linewidth = 2)
ax2.text(
    x = 90, y = points_average_distance - 4,
    s = f"Average Distance\n{actual_average_distance:.1f} yards",
    fontsize = 10, fontproperties = font_props,
    color = 'white', ha = 'center'
)

for x in df.to_dict(orient='records'):
    pitch.scatter(
        x['X'],
        x['Y'],
        s=300 * x['xG'],
        color = 'red' if x['result'] == 'Goal' else background_color,
        ax = ax2,
        alpha = 0.7,
        linewidth = 0.6,
        edgecolor = 'white'
    )

ax2.set_axis_off()

# STATS ON BOTTOM

ax3 = fig.add_axes([0,.2,1,.05]) # Top left, bottom left, width, height
ax3.set_facecolor(background_color)

ax3.text(x=0.25,y=0.5,s='Shots',fontsize = 20, fontproperties = font_props,
         fontweight='bold',color='white',ha = 'center')
ax3.text(x = 0.25,y=0, s=f"{total_shots}",fontsize=16,
         fontproperties = font_props,color='red',ha='center')

ax3.text(x=0.42,y=0.5,s='Goals',fontsize = 20, fontproperties = font_props,
         fontweight='bold',color='white',ha = 'center')
ax3.text(x = 0.42,y=0, s=f"{total_goals}",fontsize=16,
         fontproperties = font_props,color='red',ha='center')

ax3.text(x=0.55,y=0.5,s='xG',fontsize = 20, fontproperties = font_props,
         fontweight='bold',color='white',ha = 'center')
ax3.text(x = 0.55,y=0, s=f"{total_xG:.2f}",fontsize=16,
         fontproperties = font_props,color='red',ha='center')

ax3.text(x=0.69,y=0.5,s='xG/Shot',fontsize = 20, fontproperties = font_props,
         fontweight='bold',color='white',ha = 'center')
ax3.text(x = 0.69,y=0, s=f"{xG_per_shot:.2f}",fontsize=16,
         fontproperties = font_props,color='red',ha='center')

ax3.set_axis_off()

plt.show()