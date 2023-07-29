# Import necessary libraries
from flask import Flask, render_template
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import dash_html_components as html
import sqlite3
import numpy as np
import warnings
warnings.filterwarnings('ignore')


app = Flask(__name__) # Initialize the Flask app
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
dash_app = dash.Dash(__name__, server=app) # Initialize the Dash app


# create connection with the database
conn = sqlite3.connect(r'project_diamond')

#Import All Diamond data from sqlite3 database
query = 'SELECT * FROM all_diamonds' 
diamonds = pd.read_sql_query(query, conn)

# Import the lab and natural diamond data from database
query1 = 'SELECT * FROM natural_diamond_yearly' 
natural_diamond_yearly = pd.read_sql_query(query1, conn)

query2 = 'SELECT * FROM lab_diamond_yearly' 
lab_diamond_yearly = pd.read_sql_query(query2, conn)

# Import the ranking data
query3 = 'SELECT * FROM natural_diamond_ranking' 
natural_diamond_ranking = pd.read_sql_query(query3, conn)

query4 = 'SELECT * FROM lab_diamond_ranking' 
lab_diamond_ranking = pd.read_sql_query(query4, conn)


# Process the diamond data
df1 = natural_diamond_yearly.drop(["unit", "data source"], axis=1)
df2 = lab_diamond_yearly.drop(["unit"], axis=1)

# Read map data
query5 = 'SELECT * FROM mines_map' 
mines_map = pd.read_sql_query(query5, conn)

# Create the map visualization
df = mines_map.drop(["FIPSCODE", "COWCODE"], axis=1)
fig_map = px.scatter_geo(df,
                         lat='LAT',
                         lon='LONG',
                         color="COUNTRY",
                         hover_name="COUNTRY")


# Create the diamond visualization using a table
# This table will have an update menu to switch between natural and lab-grown diamonds data

headerColor = 'grey'
rowEvenColor = 'lightgrey'
rowOddColor = 'white'
dataframe_filter = go.layout.Updatemenu(
    buttons=list([
        dict(
            args=[{'cells.values': [[df1['Country'], df1['2016'], df1['2017'], df1['2018'], df1['2019'], df1['2020']]]}],
            label='Natural Diamonds',
            method='update'
        ),
        dict(
            args=[{'cells.values': [[df2['Country'], df2['2016'], df2['2017'], df2['2018'], df2['2019'], df2['2020']]]}],
            label='Lab-Grown Diamonds',
            method='update'
        )
    ]),
    direction='down',
    showactive=True,
)
# Create the table with natural diamonds data as the initial data
fig_diamond = go.Figure(data=[go.Table(
    columnwidth=[70, 50, 50, 50, 50, 50],
    header=dict(
        values=list(df1.columns),
        line_color='darkslategray',
        fill_color=headerColor,
        align=['left', 'center'],
        font=dict(color='white', size=12)
    ),
    cells=dict(
        values=[df1['Country'], df1['2016'], df1['2017'], df1['2018'], df1['2019'], df1['2020']],
        line_color='darkslategray',
        # 2-D list of colors for alternating rows
        fill_color=[[rowOddColor, rowEvenColor, rowOddColor, rowEvenColor, rowOddColor] * 5],
        align=['left', 'center'],
        font=dict(color='darkslategray', size=12)
    ))
])

# Add the dataframe filter to the layout
fig_diamond.update_layout(
    updatemenus=[dataframe_filter],
    showlegend=False,
    title=dict(
        text='Natural vs Lab-Grown Diamonds Production (2016-20)',
        x=0.5)
)

# Create additional bar chart figures for diamond rankings

fig = px.bar(lab_diamond_ranking.head(10), y='Country', x='Production 2020',
             hover_data=['Rank 2020', 'Share in %'],
             labels={'Production 2020': 'Production (caret)'}, height=500,
            title="Ranking based on Production (2020)")

fig2 = px.bar(natural_diamond_ranking.head(10), y='Country', x='Production 2020',
              hover_data=['Rank 2020', 'Share in %'],
              labels={'Production 2020': 'Production (caret)'}, height=500,
            title="Ranking based on Production (2020)")
        
figPie = px.pie(lab_diamond_ranking.head(10), values='Share in %', names='Country',
               height=477)
figPie.update_layout(title='Market Share', title_x=0.4)
fig2Pie = px.pie(natural_diamond_ranking.head(10), values='Share in %', names='Country',
            height=477)
fig2Pie.update_layout(title='Market Share', title_x=0.4)


# figPie.show()
# fig2Pie.show()

# Create the box plot using Plotly
fig_box = px.box(diamonds, x='type', y='ppc', title='Price-per-Carat by Diamond Type', color_discrete_sequence=px.colors.qualitative.Set1)

# Update the axes labels
fig_box.update_xaxes(title_text='Type')
fig_box.update_yaxes(title_text='Price-per-Carat')

#Scatter
# Convert 'clarity' column to a categorical type and reorder the categories
diamonds['clarity'] = diamonds['clarity'].astype('category')
diamonds['clarity'].cat.reorder_categories(['IF', 'VVS1', 'VVS2', 'VS1', 'VS2', 'SI1', 'SI2', 'I1'])

# Create the scatter plot using Plotly
fig_scatter = px.scatter(diamonds, x='clarity', y='ppc', color='type', facet_col='type', facet_col_wrap=1,
                 labels={'ppc': 'Price-per-Carat ($)'})

# Update the layout
fig_scatter.update_layout(title='Price-per-Carat vs Clarity', showlegend=False)

# Update the marker size for the scatter plot
fig_scatter.update_traces(marker=dict(size=5))

# 
diamonds['color'] = diamonds['color'].astype('category')
diamonds['color'].cat.reorder_categories(['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'])

fig_scatter2 = px.scatter(diamonds, x='color', y='ppc', color='type', facet_col='type', facet_col_wrap=2,
                 labels={'ppc': 'Price-per-Carat ($)'})

# Update the layout
fig_scatter2.update_layout(title='Price-per-Carat vs Color', showlegend=False)
fig_scatter2.update_traces(marker_size=5)
#

diamonds['cut'] = diamonds['cut'].astype('category')
diamonds['cut'].cat.reorder_categories(['Ideal', 'Excellent', 'Very Good', 'Good', 'Fair'])

fig_scatter3 = px.scatter(diamonds, y='cut', x='ppc', color='type', facet_col='type', facet_col_wrap=1,
                 labels={'ppc': 'Price-per-Carat ($)'})

# Update the layout
fig_scatter3.update_layout(title='Price-per-Carat vs Cut', showlegend=False)
fig_scatter3.update_traces(marker_size=5)

dash_app.layout = html.Div([
    html.H1("Diamond Project", style={'text-align': 'center','background-color': 'darkgray', 'color': 'white', 'margin-top':'-7px'}),
      html.Div([
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': country, 'value': country} for country in df['COUNTRY'].unique()],
            multi=True,
            style={'width': '200px', }
        ),   
    html.H1("Diamond Mines Map", style={'display': 'flex','margin-left':'25%','margin-top':'-0.5px'})
    ], style={'display': 'flex'}),
    html.Div([   
         dcc.Graph(id='geo-graph', figure=fig_map, style={'width': '100%', 'display': 'inline-block'}),
    ], style={'text-align': 'center'}),
     html.Div([
         html.H1("Lab-Grown Diamonds", style={'display': 'flex','margin-left':'40%','margin-top':'-0.5px'}),
         dcc.Graph(id='bar-chart1', figure=fig, style={'width': '50%', 'display': 'inline-block'}),
         dcc.Graph(id='Pie-chart1', figure=figPie, style={'width': '50%', 'display': 'inline-block'}),
        
            
    ], style={'text-align': 'center'}),
    html.Div([
         html.H1("Natural Diamonds", style={'display': 'flex','margin-left':'37%','margin-top':'-0.5px'}),
        dcc.Graph(id='bar-chart2', figure=fig2, style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='Pie-chart2', figure=fig2Pie, style={'width': '50%', 'display': 'inline-block'}),
    ], style={'text-align': 'center'}),
     html.Div([
        dcc.Graph(id='diamond-graph', figure=fig_diamond, style={'width': '100%', 'display': 'inline-block'}),
    ], style={'text-align': 'center'}),
     html.Div([
         html.H1("Natural VS Lab-Grown Diamonds", style={'display': 'flex','margin-left':'40%','margin-top':'-0.5px'}),
        dcc.Graph(id='boxplot', figure=fig_box, style={'width': '80%', 'display': 'inline-block'}),
    ], style={'text-align': 'center'}),
      html.Div([
        dcc.Graph(id='scatter-plot', figure=fig_scatter, style={'width': '80%', 'display': 'inline-block'}),
    ], style={'text-align': 'center'}),
     html.Div([
        dcc.Graph(id='scatter-plot2', figure=fig_scatter2, style={'width': '80%', 'display': 'inline-block'}),
    ], style={'text-align': 'center'}),
      html.Div([
        dcc.Graph(id='scatter-plot3', figure=fig_scatter3, style={'width': '80%', 'display': 'inline-block'}),
    ], style={'text-align': 'center'}),
],style={'text-align': 'center'})


@dash_app.callback(
    dash.dependencies.Output('geo-graph', 'figure'),
    [dash.dependencies.Input('country-dropdown', 'value')]
)
def update_graph(selected_countries):
    if not selected_countries:
        filtered_df = df
    else:
        filtered_df = df[df['COUNTRY'].isin(selected_countries)]
    updated_fig = px.scatter_geo(filtered_df,
                                 lat='LAT',
                                 lon='LONG',
                                 color="COUNTRY",
                                 hover_name="COUNTRY")
    return updated_fig

@app.route('/')
def index():
   return render_template('index.html',
                           map_section=fig_map.to_html(full_html=False),
                           lab_grown_diamonds_section=fig.to_html(full_html=False),
                           natural_diamonds_section=fig2.to_html(full_html=False),
                           diamond_section=fig_diamond.to_html(full_html=False),
                           bar_charts_section=figPie.to_html(full_html=False),
                           scatter_plot_section=fig_scatter.to_html(full_html=False),
                           scatter_plot2_section=fig_scatter2.to_html(full_html=False),
                           scatter_plot3_section=fig_scatter3.to_html(full_html=False))

if __name__ == '__main__':
    app.run(debug=True)
