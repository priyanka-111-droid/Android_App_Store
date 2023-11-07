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
df_apps_clean = df_apps.dropna().drop_duplicates() #remove NaN,remove duplicates
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
    
    # Donut chart for Content Rating
    dcc.Graph(id='content-rating-donut', config={'displayModeBar': False}),
    
    # Bar chart for the number of apps per category (vertical)
    dcc.Graph(id='top-category-bar', config={'displayModeBar': False}),
    
    # Horizontal bar chart for category popularity
    dcc.Graph(id='category-popularity-bar', config={'displayModeBar': False}),
    
    # Scatter plot for category concentration
    dcc.Graph(id='category-concentration-scatter', config={'displayModeBar': False}),
    
    # Bar chart for the number of apps per genre
    dcc.Graph(id='top-genres-bar', config={'displayModeBar': False}),
    
    # Grouped bar chart for free vs paid apps by category
    dcc.Graph(id='free-vs-paid-by-category-groupedbar', config={'displayModeBar': False}),
    
    # Box plot for downloads of free vs paid apps
    dcc.Graph(id='downloads-free-vs-paid-box', config={'displayModeBar': False}),
    
    # Box plot for median price for paid apps
    dcc.Graph(id='median-price-paid-apps-box', config={'displayModeBar': False}),

    # Treemap for Category and Genres with colors denoting Rating
    dcc.Graph(id='category-genre-treemap', config={'displayModeBar': False}),

    # Heatmap showing Category and Genre with colors showing installs 
    dcc.Graph(id='category-genre-installs-heatmap', config={'displayModeBar': False}),

    # Bubble Chart showing relationship between rating and installs across content-rating.
    dcc.Graph(id='rating-installs-bubble', config={'displayModeBar': False}),

    # 3D Scatter Plot showing Relationship between Rating,Installs and Content rating
    dcc.Graph(id='rating-installs-category-scatter-3d', config={'displayModeBar': False}),

    # Line Chart showing number of installs over time
    dcc.Graph(id='installs-time-line', config={'displayModeBar': False}),

    # Bar chart showing Installs for different Android Versions
    dcc.Graph(id='installs-android-bar', config={'displayModeBar': False}),

    # Violin plot showing distribution of rating across different content rating categories
    dcc.Graph(id='rating-content_rating-violin', config={'displayModeBar': False}),

    # Heat map showing Category and Genres and color denoting size in MB.
    dcc.Graph(id='category-genre-size-heatmap', config={'displayModeBar': False}),

])



# Callbacks to update the charts
@app.callback(
    Output('content-rating-donut', 'figure'),
    Output('top-category-bar', 'figure'),
    Output('category-popularity-bar', 'figure'),
    Output('category-concentration-scatter', 'figure'),
    Output('top-genres-bar', 'figure'),
    Output('free-vs-paid-by-category-groupedbar', 'figure'),
    Output('downloads-free-vs-paid-box', 'figure'),
    Output('median-price-paid-apps-box', 'figure'),
    Output('category-genre-treemap', 'figure'),
    Output('category-genre-installs-heatmap', 'figure'),
    Output('rating-installs-bubble', 'figure'),
    Output('rating-installs-category-scatter-3d', 'figure'),
    Output('installs-time-line', 'figure'),
    Output('installs-android-bar', 'figure'),
    Output('rating-content_rating-violin', 'figure'),
    Output('category-genre-size-heatmap', 'figure'),
    Input('category-dropdown', 'value')
)



def update_charts(selected_category):
    if selected_category == 'All Categories':
        filtered_df = df_apps_clean
    else:
        filtered_df = df_apps_clean[df_apps_clean['Category'] == selected_category]
    

    # 1. Donut chart for Content Rating
    fig1 = px.pie(
        labels=filtered_df['Content_Rating'].value_counts().index,
        values=filtered_df['Content_Rating'].value_counts().values,
        title="Donut Chart For Content Rating",
        names=filtered_df['Content_Rating'].value_counts().index,
        hole=0.6
    )
    fig1.update_traces(textposition='inside', textfont_size=15, textinfo='percent')
    


    # 2. Vertical Bar chart for the number of apps per category
    top10_category = filtered_df['Category'].value_counts()[:10]
    fig2 = px.bar(x=top10_category.index, y=top10_category.values, title="Vertical Bar Chart For Number of Apps per Category")
    fig2.update_layout(xaxis_title='Categories',yaxis_title='Number of Apps')



    # 3. Horizontal bar chart for category popularity
    category_installs = filtered_df.groupby('Category')['Installs'].sum().reset_index()
    category_installs = category_installs.sort_values('Installs', ascending=False)
    fig3 = px.bar(
        category_installs, x='Installs', y='Category', orientation='h',
        title='Horizontal Bar Chart For Category Popularity'
    )
    fig3.update_layout(
        xaxis_title='Number of Downloads',
        yaxis_title='Category'
    )



    #4. Scatter plot for category concentration
    cat_number = filtered_df['Category'].value_counts().reset_index()
    cat_number.columns = ['Category', 'App Count']
    cat_installs = filtered_df.groupby('Category')['Installs'].sum().reset_index()
    cat_merged_df = pd.merge(cat_number, cat_installs, on='Category', how="inner")

    fig4 = px.scatter(
    cat_merged_df, x='App Count', y='Installs', title='Scatter Plot For Category Concentration',
    size='App Count', color='Category'
      )
    fig4.update_layout(xaxis_title="Number of Apps (Lower=More Concentrated)", yaxis_title="Installs", yaxis=dict(type='log'))



    # 5. Bar chart for the number of apps per genre
    stack = filtered_df['Genres'].str.split(';', expand=True).stack()
    num_genres = stack.value_counts()
    fig5 = px.bar(
        x=num_genres.index[:15], y=num_genres.values[:15], title='Bar Chart For Number of Apps Per Genre',
        hover_name=num_genres.index[:15]
    )
    fig5.update_layout(xaxis_title='Genre', yaxis_title='Number of Apps', coloraxis_showscale=False)



    # 6. Grouped bar chart for free vs paid apps by category
    df_free_vs_paid = filtered_df.groupby(["Category", "Type"], as_index=False).agg({'App': pd.Series.count})
    fig6 = px.bar(
        df_free_vs_paid, x='Category', y='App', title='Grouped Bar Chart For Free vs Paid Apps by Category', color='Type', barmode='group'
    )



    # 7. Box plot for downloads of free vs paid apps
    fig7 = px.box(
        filtered_df, y='Installs', x='Type', color='Type', notched=True,
        title='Box plot for downloads of free vs paid apps'
    )
    fig7.update_layout(yaxis=dict(type='log'))




    df_paid_apps = filtered_df[filtered_df['Type'] == 'Paid']
    # 8. Box plot for median price for paid apps
    fig8 = px.box(df_paid_apps, x='Category', y="Price", title='Box Plot For Median Price for paid apps')
    fig8.update_layout(xaxis_title='Category', yaxis_title='Paid App Price', xaxis={'categoryorder': 'max descending'}, yaxis=dict(type='log'))





    # 9. Treemap showing Categories and Genres with colors showing Rating.
    fig9 = px.treemap(
        filtered_df,
        path=['Category', 'Genres'],
        values='Installs',
        color='Rating',
        color_continuous_scale='Viridis',
        title='Treemap Showing Categories and Genres with colors showing Rating'
    )









    # 10. Heatmap showing Category and Genre with colors showing installs in Thousands
    # Convert 'Installs' to thousands
    filtered_df['Installs_Thousands'] = filtered_df['Installs'] / 1e6

    #Create the heatmap pivot table 
    heatmap_data = filtered_df.pivot_table(index='Category', columns='Genres', values='Installs_Thousands', aggfunc=np.sum)

    #Plot the heatmap with the adjusted 'Installs_Thousands' data
    fig10 = px.imshow(
        heatmap_data,
        labels=dict(x="Genres", y="Category", color="Installs"),
        x=heatmap_data.columns,
        y=heatmap_data.index,
        title='Heatmap showing Category and Genres with colors showing Installs in Thousands',
        color_continuous_scale=[[0, 'rgb(128,0,128)'], [0.166, 'rgb(0,0,255)'], [0.333, 'rgb(0,255,255)'],
                           [0.5, 'rgb(0,255,0)'], [0.666, 'rgb(255,255,0)'], [0.833, 'rgb(255,165,0)'],
                           [1, 'rgb(255,0,0)']],
        zmin=0,
        zmax=20000
    )
    fig10.update_traces(hovertemplate='Category: %{y}<br>Genre: %{x}<br>Installs: %{z:.2f}')
    fig10.update_layout(
        autosize=True,
        width=1000,  # Set the width of the plot
        height=600
    )





    # 11. Bubble Chart showing relationship between rating and installs across content-rating.
    bubble_data = filtered_df.groupby(['Genres', 'Content_Rating']).agg({'Installs': 'sum', 'Rating': 'mean'}).reset_index()
    fig11 = px.scatter(
        bubble_data,
        x='Rating',
        y='Installs',
        size='Rating',
        color='Content_Rating',
        title='Bubble Chart showing relationship between rating and installs across content-rating.'
    )
    fig11.update_layout(
            autosize=False,
            width=1000,  # Set the width of the plot
            height=600,  # Set the height of the plot
    )





    # 12. 3D Scatter Plot showing Relationship between Rating,Installs and Content rating.
    fig12 = px.scatter_3d(
        filtered_df,
        x='Rating',
        y='Reviews',
        z='Installs',
        color='Content_Rating',
        title='3D Scatter Plot showing Relationship between Rating,Installs and Content rating'
    )
    fig12.update_layout(
    width=900,  # Set the width of the plot
    height=700  # Set the height of the plot
    )




    # 13. Line Chart showing number of installs over time
    # Group by 'Last_Updated' and aggregate the sum of 'Installs'
    line_data = filtered_df.groupby('Last_Updated').agg({'Installs': 'sum'}).reset_index()

    fig13 = px.line(
        line_data,
        x='Last_Updated',
        y='Installs',
        title='Line Chart showing number of installs over time'
    )
    fig13.update_layout(
    width=1500,  # Set the width of the plot
    height=700  # Set the height of the plot
    )

    

    



    # 14. Bar chart showing Installs for different Android Versions
    bar_data = filtered_df.groupby('Android_Ver').agg({'Installs': 'sum'}).reset_index()
    bar_data['Installs'] = bar_data['Installs'].astype(str)
    bar_data = bar_data[bar_data['Installs'].astype(str) != '0']  # Exclude rows where Installs are 0
    fig14 = px.bar(
        bar_data,
        x='Android_Ver',
        y='Installs',
        title='Bar chart showing Installs for different Android Versions'
    )
   


    # 15. Violin plot showing distribution of rating across different content rating categories
    fig15 = px.violin(
        filtered_df,
        x='Content_Rating',
        y='Rating',
        box=True,
        title='Violin plot showing distribution of rating across different content rating categories'
    )





    #16. Heatmap for Category and Genres and color denoting size in MBs
    heatmap_data_prices = filtered_df.pivot_table(index='Category', columns='Genres', values='Size_MBs', aggfunc=np.sum)
    fig16= px.imshow(
        heatmap_data_prices,
        labels=dict(x="Genres", y="Category",color="size_MBs"),
        x=heatmap_data_prices.columns,
        y=heatmap_data_prices.index,
        title='Heat map showing Category and Genres and color denoting size in MBs',
        color_continuous_scale=[[0, 'rgb(128,0,128)'], [0.166, 'rgb(0,0,255)'], [0.333, 'rgb(0,255,255)'],
                           [0.5, 'rgb(0,255,0)'], [0.666, 'rgb(255,255,0)'], [0.833, 'rgb(255,165,0)'],
                           [1, 'rgb(255,0,0)']], # You can choose your desired color scale
    )

    fig16.update_layout(
        autosize=False,
        width=1000,  # Set the width of the plot
        height=600,  # Set the height of the plot
    )


    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10,fig11, fig12, fig13, fig14, fig15, fig16




if __name__ == '__main__':
    app.run_server(debug=True)



