import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output

# Load and clean the data
df_apps = pd.read_csv('apps.csv')
df_apps_clean = df_apps.dropna().drop_duplicates()
df_apps_clean['Installs'] = df_apps_clean['Installs'].str.replace(',', '').astype(int)
df_apps_clean['Price'] = df_apps_clean['Price'].str.replace('$', '').astype(float)
df_apps_clean['Revenue_Estimate'] = df_apps_clean['Installs'] * df_apps_clean['Price']

# Create a Dash app
app = dash.Dash(__name__)

# Get unique categories for the dropdown
categories = df_apps_clean['Category'].unique()
# Add an option for All Categories
categories = ['All Categories'] + list(categories)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("Google Play Store Apps Dashboard"),
    
    # Dropdown to select a category
    dcc.Dropdown(
        id='category-dropdown',
        options=[{'label': category, 'value': category} for category in categories],
        value='All Categories'  # Default selection
    ),
    
    # Pie chart for Content Rating
    dcc.Graph(id='content-rating-pie', config={'displayModeBar': False}),
    
    # Bar chart for the number of apps per category (vertical)
    dcc.Graph(id='top-category-bar', config={'displayModeBar': False}),
    
    # Horizontal bar chart for category popularity
    dcc.Graph(id='category-popularity-bar', config={'displayModeBar': False}),
    
    # Scatter plot for category concentration
    dcc.Graph(id='category-concentration-scatter', config={'displayModeBar': False}),
    
    # Bar chart for the number of apps per genre
    dcc.Graph(id='top-genres-bar', config={'displayModeBar': False}),
    
    # Grouped bar chart for free vs paid apps by category
    dcc.Graph(id='free-vs-paid-by-category', config={'displayModeBar': False}),
    
    # Box plot for downloads of free vs paid apps
    dcc.Graph(id='downloads-free-vs-paid', config={'displayModeBar': False}),
    
    # Box plot for revenue by app category
    dcc.Graph(id='revenue-by-category', config={'displayModeBar': False}),
    
    # Box plot for median price for paid apps
    dcc.Graph(id='median-price-paid-apps', config={'displayModeBar': False}),

    # Sunburst chart for top genres
    dcc.Graph(id='top-genres-sunburst', config={'displayModeBar': False}),

])

# Callbacks to update the charts
@app.callback(
    Output('content-rating-pie', 'figure'),
    Output('top-category-bar', 'figure'),
    Output('category-popularity-bar', 'figure'),
    Output('category-concentration-scatter', 'figure'),
    Output('top-genres-bar', 'figure'),
    Output('free-vs-paid-by-category', 'figure'),
    Output('downloads-free-vs-paid', 'figure'),
    Output('revenue-by-category', 'figure'),
    Output('median-price-paid-apps', 'figure'),
    Output('top-genres-sunburst', 'figure'),
    Input('category-dropdown', 'value')
)
def update_charts(selected_category):
    if selected_category == 'All Categories':
        filtered_df = df_apps_clean
    else:
        filtered_df = df_apps_clean[df_apps_clean['Category'] == selected_category]
    
    fig1 = px.pie(
        labels=filtered_df['Content_Rating'].value_counts().index,
        values=filtered_df['Content_Rating'].value_counts().values,
        title="Content Rating",
        names=filtered_df['Content_Rating'].value_counts().index,
        hole=0.6
    )
    fig1.update_traces(textposition='inside', textfont_size=15, textinfo='percent')
    
    top10_category = filtered_df['Category'].value_counts()[:10]
    fig2 = px.bar(x=top10_category.index, y=top10_category.values, title="Number of Apps per Category")
    
    category_installs = filtered_df.groupby('Category').agg({'Installs': pd.Series.sum})
    category_installs.sort_values('Installs', ascending=True, inplace=True)
    fig3 = px.bar(x=category_installs.Installs, y=category_installs.index, orientation='h', title='Category Popularity')
    fig3.update_layout(xaxis_title='Number of Downloads', yaxis_title='Category')
    
    cat_number = filtered_df.groupby('Category').agg({'App': pd.Series.count})
    cat_merged_df = pd.merge(cat_number, category_installs, on='Category', how="inner")
    fig4 = px.scatter(cat_merged_df, x='App', y='Installs', title='Category Concentration',
                     size='App', hover_name=cat_merged_df.index, color='Installs')
    fig4.update_layout(xaxis_title="Number of Apps (Lower=More Concentrated)", yaxis_title="Installs",
                      yaxis=dict(type='log'))
    
    stack = filtered_df['Genres'].str.split(';', expand=True).stack()
    num_genres = stack.value_counts()
    fig5 = px.bar(x=num_genres.index[:15], y=num_genres.values[:15], title='Top Genres',
              hover_name=num_genres.index[:15], color=num_genres.values[:15],
              color_continuous_scale='Agsunset')

    fig5.update_layout(xaxis_title='Genre', yaxis_title='Number of Apps', coloraxis_showscale=False)
    
    df_free_vs_paid = filtered_df.groupby(["Category", "Type"], 
                                      as_index=False).agg({'App': pd.Series.count})
    fig6 = px.bar(df_free_vs_paid, x='Category', y='App', title='Free vs Paid Apps by Category', color='Type', barmode='group')
    
    # Box plot for downloads of free vs paid apps
    fig7 = px.box(filtered_df, y='Installs', x='Type', color='Type', notched=True, points='all', title='How Many Downloads are Paid Apps Giving Up?')
    fig7.update_layout(yaxis=dict(type='log'))
    
    df_paid_apps = filtered_df[filtered_df['Type'] == 'Paid']
    
    # Box plot for revenue by app category
    fig8 = px.box(df_paid_apps, x='Category', y='Revenue_Estimate', title='How Much Can Paid Apps Earn?')
    fig8.update_layout(xaxis_title='Category', yaxis_title='Paid App Ballpark Revenue', xaxis={'categoryorder': 'min ascending'}, yaxis=dict(type='log'))
    
    # Box plot for median price for paid apps
    fig9 = px.box(df_paid_apps, x='Category', y="Price", title='Price per Category')
    fig9.update_layout(xaxis_title='Category', yaxis_title='Paid App Price', xaxis={'categoryorder': 'max descending'}, yaxis=dict(type='log'))

    # Create a sunburst chart for top genres
    sunburst_data = filtered_df['Genres'].str.split(';', expand=True).stack().value_counts().reset_index()
    sunburst_data.columns = ['Genres', 'Count']

    fig10 = px.sunburst(
        sunburst_data,
        path=['Genres'],
        values='Count',
        title=f"Top Genres for {selected_category}",
    )

   

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7,fig8,fig9,fig10


if __name__ == '__main__':
    app.run_server(debug=True)



