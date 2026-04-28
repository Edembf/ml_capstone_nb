# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
# FLAG: Ensure the csv file is in the same directory
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Dropdown list for Launch Site selection
    html.Div([
        html.Label('Select Launch Site:'),
        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            ],
            value='ALL',
            placeholder="Select a Launch Site here",
            searchable=True
        )
    ], style={'padding': '0 20px'}),
    
    html.Br(),

    # TASK 2: Pie chart for success counts
    html.Div(dcc.Graph(id='success-pie-chart')),
    
    html.Br(),

    # TASK 3: Range slider for payload selection
    html.P("Payload range (Kg):"),
    html.Div([
        dcc.RangeSlider(
            id='payload-slider',
            min=0, 
            max=10000, 
            step=1000,
            value=[min_payload, max_payload],
            marks={i: {'label': f'{i}', 'style': {'color': '#777'}} for i in range(0, 10001, 2000)},
            tooltip={"placement": "bottom", "always_visible": True},
            allow_direct_input=False),
    ], style={'padding': '0 40px', 'margin-bottom': '40px', "color": "LightSteelBlue"}),


    # TASK 4: Scatter chart for payload vs. success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for Pie Chart
# FLAG: Callbacks must be outside the app.layout definition
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # FLAG: Pie chart for ALL sites shows total successful launches per site
        fig = px.pie(spacex_df, values='class', 
                     names='Launch Site', 
                     title='Total Success Launches by Site')
        return fig
    else:
        # FLAG: Pie chart for specific site shows Success (1) vs Failure (0)
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count values of class (0 and 1)
        df_counts = filtered_df['class'].value_counts().reset_index()
        df_counts.columns = ['class', 'count']
        fig = px.pie(df_counts, values='count', 
                     names='class', 
                     title=f'Total Success Launches for site {entered_site}')
        return fig

# TASK 4: Callback for Scatter Chart
# FLAG: Corrected multiple inputs syntax and site filtering logic
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class', 
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites'
        )
        return fig
    else:
        # FLAG: Filtering by both site and payload range
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_filtered_df, x='Payload Mass (kg)', y='class', 
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for site {entered_site}'
        )
        return fig

# Run the app
if __name__ == '__main__':
    app.run()
