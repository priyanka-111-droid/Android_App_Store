import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output
import numpy as np

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

    # Treemap
    dcc.Graph(id='treemap', config={'displayModeBar': False}),

    # 12. Icicle graph
    dcc.Graph(id='icicle-graph', config={'displayModeBar': False}),

    # 13. Heatmap
    dcc.Graph(id='heatmap', config={'displayModeBar': False}),

    # 14. Cluster Matrix
    dcc.Graph(id='cluster-matrix', config={'displayModeBar': False}),

    # 15. 3D Scatter Plot
    dcc.Graph(id='scatter-3d', config={'displayModeBar': False}),

    # 16. Line Chart
    dcc.Graph(id='line-chart', config={'displayModeBar': False}),

    # 17. Bar Chart
    dcc.Graph(id='bar-chart', config={'displayModeBar': False}),

        # 18. Violin Plot
    dcc.Graph(id='violin-plot', config={'displayModeBar': False}),

    # 19. Bubble Chart
    dcc.Graph(id='bubble-chart', config={'displayModeBar': False}),

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
    Output('treemap', 'figure'),
    Output('icicle-graph', 'figure'),
    Output('heatmap', 'figure'),
    Output('cluster-matrix', 'figure'),
    Output('scatter-3d', 'figure'),
    Output('line-chart', 'figure'),
    Output('bar-chart', 'figure'),
    Output('violin-plot', 'figure'),
    Output('bubble-chart', 'figure'),
    Input('category-dropdown', 'value')
)

def update_charts(selected_category):
    if selected_category == 'All Categories':
        filtered_df = df_apps_clean
    else:
        filtered_df = df_apps_clean[df_apps_clean['Category'] == selected_category]
    

    # 1. Pie chart for Content Rating
    fig1 = px.pie(
        labels=filtered_df['Content_Rating'].value_counts().index,
        values=filtered_df['Content_Rating'].value_counts().values,
        title="Content Rating",
        names=filtered_df['Content_Rating'].value_counts().index,
        hole=0.6
    )
    fig1.update_traces(textposition='inside', textfont_size=15, textinfo='percent')
    
    # 2. Bar chart for the number of apps per category (vertical)
    top10_category = filtered_df['Category'].value_counts()[:10]
    fig2 = px.bar(x=top10_category.index, y=top10_category.values, title="Number of Apps per Category")

    # 3. Horizontal bar chart for category popularity
    fig3 = px.bar(
    filtered_df, x='Installs', y='Category', orientation='h', title='Category Popularity'
      )
    fig3.update_layout(xaxis_title='Number of Downloads', yaxis_title='Category')

      
    #4 Scatter plot
    cat_number = filtered_df['Category'].value_counts().reset_index()
    cat_number.columns = ['Category', 'App Count']
    cat_installs = filtered_df.groupby('Category')['Installs'].sum().reset_index()
    cat_merged_df = pd.merge(cat_number, cat_installs, on='Category', how="inner")

    fig4 = px.scatter(
    cat_merged_df, x='App Count', y='Installs', text='Category', title='Category Concentration',
    size='App Count', color='Category'
      )
    fig4.update_layout(xaxis_title="Number of Apps (Lower=More Concentrated)", yaxis_title="Installs", yaxis=dict(type='log'))

    # 5. Bar chart for the number of apps per genre
    stack = filtered_df['Genres'].str.split(';', expand=True).stack()
    num_genres = stack.value_counts()
    fig5 = px.bar(
        x=num_genres.index[:15], y=num_genres.values[:15], title='Top Genres',
        hover_name=num_genres.index[:15], color=num_genres.values[:15], color_continuous_scale='Agsunset'
    )
    fig5.update_layout(xaxis_title='Genre', yaxis_title='Number of Apps', coloraxis_showscale=False)

    # 6. Grouped bar chart for free vs paid apps by category
    df_free_vs_paid = filtered_df.groupby(["Category", "Type"], as_index=False).agg({'App': pd.Series.count})
    fig6 = px.bar(
        df_free_vs_paid, x='Category', y='App', title='Free vs Paid Apps by Category', color='Type', barmode='group'
    )

    # 7. Box plot for downloads of free vs paid apps
    fig7 = px.box(
        filtered_df, y='Installs', x='Type', color='Type', notched=True, points='all',
        title='How Many Downloads are Paid Apps Giving Up?'
    )
    fig7.update_layout(yaxis=dict(type='log'))



    df_paid_apps = filtered_df[filtered_df['Type'] == 'Paid']
    # 8. Box plot for revenue by app category
    fig8 = px.box(df_paid_apps, x='Category', y='Revenue_Estimate', title='How Much Can Paid Apps Earn?')
    fig8.update_layout(xaxis_title='Category', yaxis_title='Paid App Ballpark Revenue', xaxis={'categoryorder': 'min ascending'}, yaxis=dict(type='log'))

    # 9. Box plot for median price for paid apps
    fig9 = px.box(df_paid_apps, x='Category', y="Price", title='Price per Category')
    fig9.update_layout(xaxis_title='Category', yaxis_title='Paid App Price', xaxis={'categoryorder': 'max descending'}, yaxis=dict(type='log'))


    # 10. Sunburst chart for top genres
    sunburst_data = filtered_df['Genres'].str.split(';', expand=True).stack().value_counts().reset_index()
    sunburst_data.columns = ['Genres', 'Count']
    fig10 = go.Figure(go.Sunburst(
        labels=sunburst_data['Genres'],
        parents=[""] * len(sunburst_data['Genres']),
        values=sunburst_data['Count'],
        hovertemplate='%{label}<br>Count: %{value}',
    ))
    fig10.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        title=f"Top Genres for {selected_category}",
    )



    # 11. Treemap
    fig11 = px.treemap(
        filtered_df,
        path=['Category', 'Genres'],
        values='Installs',
        color='Rating',
        color_continuous_scale='Viridis',
        title='Treemap'
    )

     # 12. Icicle graph
    icicle_data = filtered_df.groupby(['Category', 'Genres']).agg({'Installs': 'sum'}).reset_index()
    fig12 = px.icicle(
        icicle_data,
        path=['Category', 'Genres'],
        values='Installs',
        title='Icicle Graph'
    )

    # 13. Heatmap
    heatmap_data = filtered_df.pivot_table(index='Category', columns='Genres', values='Installs', aggfunc=np.sum)
    fig13 = px.imshow(
        heatmap_data,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        title='Heatmap'
    )

    # 14. Cluster Matrix
    cluster_data = heatmap_data.fillna(0)
    fig14 = px.imshow(
        cluster_data,
        x=cluster_data.columns,
        y=cluster_data.index,
        title='Cluster Matrix'
    )

    # 15. 3D Scatter Plot
    fig15 = px.scatter_3d(
        filtered_df,
        x='Rating',
        y='Reviews',
        z='Installs',
        color='Genres',
        title='3D Scatter Plot'
    )
    # 16. Line Chart
    line_data = filtered_df.groupby('Last_Updated').agg({'Installs': 'sum'}).reset_index()
    fig16 = px.line(
        line_data,
        x='Last_Updated',
        y='Installs',
        title='Line Chart'
    )
    # 17. Bar Chart
    bar_data = filtered_df.groupby('Android_Ver').agg({'Installs': 'sum'}).reset_index()
    fig17 = px.bar(
        bar_data,
        x='Android_Ver',
        y='Installs',
        title='Bar Chart'
    )

    # 18. Violin Plot
    fig18 = px.violin(
        filtered_df,
        x='Content_Rating',
        y='Rating',
        box=True,
        points="all",
        title='Violin Plot'
    )

    # 19. Bubble Chart
    bubble_data = filtered_df.groupby(['Genres', 'Content_Rating']).agg({'Installs': 'sum', 'Rating': 'mean'}).reset_index()
    fig19 = px.scatter(
        bubble_data,
        x='Rating',
        y='Installs',
        size='Rating',
        color='Content_Rating',
        title='Bubble Chart'
    )




    return fig1, fig2, fig3, fig4, fig5, fig6, fig7,fig8,fig9,fig10,fig11,fig12,fig13,fig14,fig15,fig16,fig17,fig18,fig19


if __name__ == '__main__':
    app.run_server(debug=True)



