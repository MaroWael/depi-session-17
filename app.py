from dash import Dash, html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load and preprocess data
df = pd.read_csv('train.csv')
df.drop(['Row ID', 'Country', 'Customer Name'], axis=1, inplace=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='mixed')
df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed')
df['Postal Code'] = df['Postal Code'].fillna('05401').astype('str')

# Add state abbreviations
state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'District of Columbia': 'DC',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL',
    'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
    'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI',
    'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT',
    'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND',
    'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
    'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA',
    'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}
df['State Code'] = df['State'].map(state_abbrev)

# Prepare data for visualizations
daily_sales = df.groupby('Order Date')['Sales'].sum().reset_index()
daily_sales['Year'] = daily_sales['Order Date'].dt.year
daily_sales['Month'] = daily_sales['Order Date'].dt.month
daily_sales['DayOfYear'] = daily_sales['Order Date'].dt.dayofyear

monthly_sales = daily_sales.groupby(['Year', 'Month'])['Sales'].sum().reset_index()
yearly_sales = daily_sales.groupby('Year')['Sales'].sum().reset_index()
category_sales = df.groupby('Category')['Sales'].sum().reset_index()
state_sales = df.groupby(['State', 'State Code', 'Region'])['Sales'].sum().reset_index()

# May 2-8 analysis
may_mask = (daily_sales['Order Date'].dt.month == 5) & (daily_sales['Order Date'].dt.day >= 2) & (daily_sales['Order Date'].dt.day <= 8)
may_sales = daily_sales[may_mask]
may_yearly_avg = may_sales.groupby('Year')['Sales'].mean().reset_index(name='avg_sales')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Sales Analytics Dashboard For USA", className="text-center mb-4"),
            html.Hr()
        ])
    ]),
    
    # Key Metrics Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"${df['Sales'].sum():,.0f}", className="card-title"),
                    html.P("Total Sales", className="card-text")
                ])
            ], color="primary", outline=True)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{df['Customer ID'].nunique():,}", className="card-title"),
                    html.P("Unique Customers", className="card-text")
                ])
            ], color="info", outline=True)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{df['State'].nunique()}", className="card-title"),
                    html.P("States", className="card-text")
                ])
            ], color="success", outline=True)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{len(df):,}", className="card-title"),
                    html.P("Total Orders", className="card-text")
                ])
            ], color="warning", outline=True)
        ], width=3)
    ], className="mb-4"),
    
    # Charts Row 1
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=px.line(
                    yearly_sales,
                    x='Year',
                    y='Sales',
                    title='Annual Sales Trend',
                    markers=True
                ).update_layout(height=400)
            )
        ], width=6),
        dbc.Col([
            dcc.Graph(
                figure=px.bar(
                    category_sales.sort_values('Sales', ascending=False),
                    x='Category',
                    y='Sales',
                    title='Sales by Category',
                    color='Sales',
                    color_continuous_scale='Blues'
                ).update_layout(height=400)
            )
        ], width=6)
    ], className="mb-4"),
    
    # Charts Row 2
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=px.choropleth(
                    state_sales,
                    locations='State Code',
                    locationmode='USA-states',
                    color='Sales',
                    scope='usa',
                    hover_name='State',
                    hover_data={'Region': True},
                    title='Sales by State',
                    color_continuous_scale='Reds'
                ).update_layout(height=500)
            )
        ], width=12)
    ], className="mb-4"),
    
    # Charts Row 3
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=px.bar(
                    monthly_sales,
                    x='Month',
                    y='Sales',
                    animation_frame='Year',
                    title='Monthly Sales by Year (Animated)',
                    labels={'Month': 'Month', 'Sales': 'Sales ($)'}
                ).update_layout(height=400)
            )
        ], width=6),
        dbc.Col([
            dcc.Graph(
                figure=px.bar(
                    may_yearly_avg,
                    x='Year',
                    y='avg_sales',
                    title='Average Sales During May 2-8 by Year',
                    color='avg_sales',
                    color_continuous_scale='Greens'
                ).update_layout(height=400)
            )
        ], width=6)
    ], className="mb-4"),
    
    
], fluid=True)


if __name__ == '__main__':
    app.run(debug=True)