# Day 76 - Google Play Store Analysis with Plotly

# Step 1: Import Libraries
import pandas as pd
import plotly.express as px

# Step 2: Load Data
df_apps = pd.read_csv('apps.csv')

# Step 3: Preliminary Exploration
print(df_apps.shape)
print(df_apps.columns)
print(df_apps.sample(5))

# Step 4: Drop Unnecessary Columns
df_apps_clean = df_apps.drop(columns=['Last_Updated', 'Android_Ver'], axis=1)

# Step 5: Remove Rows with NaN Ratings
df_apps_clean = df_apps_clean.dropna(subset=['Rating'])
print(df_apps_clean.shape)

# Step 6: Remove Duplicates
df_apps_clean = df_apps_clean.drop_duplicates(subset=['App', 'Reviews'])
print(df_apps_clean.shape)

# Step 7: Convert Size & Installs to Numeric
df_apps_clean['Installs'] = df_apps_clean['Installs'].astype(str).str.replace(',', '').str.replace('+', '')
df_apps_clean['Installs'] = pd.to_numeric(df_apps_clean['Installs'])

df_apps_clean['Price'] = df_apps_clean['Price'].astype(str).str.replace('$', '')
df_apps_clean['Price'] = pd.to_numeric(df_apps_clean['Price'])
df_apps_clean = df_apps_clean[df_apps_clean['Price'] < 250]

# Step 8: Add Revenue Estimate
df_apps_clean['Revenue_Estimate'] = df_apps_clean['Price'] * df_apps_clean['Installs']

# Step 9: Pie & Donut Chart of Content Ratings
ratings = df_apps_clean.Content_Rating.value_counts()

fig = px.pie(labels=ratings.index,
             values=ratings.values,
             title="Content Rating",
             names=ratings.index)
fig.update_traces(textposition='outside', textinfo='percent+label')
fig.show()

fig = px.pie(labels=ratings.index,
             values=ratings.values,
             title="Content Rating Donut",
             names=ratings.index,
             hole=0.6)
fig.update_traces(textposition='inside', textfont_size=15, textinfo='percent')
fig.show()

# Step 10: Bar Charts for Category Popularity
top10_category = df_apps_clean.Category.value_counts()[:10]
bar = px.bar(x=top10_category.index, y=top10_category.values)
bar.show()

# Horizontal Bar Chart by Total Installs per Category
category_installs = df_apps_clean.groupby('Category').agg({'Installs':'sum'})
category_installs.sort_values('Installs', ascending=True, inplace=True)

h_bar = px.bar(x=category_installs.Installs, y=category_installs.index, orientation='h', title='Category Popularity')
h_bar.update_layout(xaxis_title='Number of Downloads', yaxis_title='Category')
h_bar.show()

# Scatter Plot of Category Concentration
cat_number = df_apps_clean.groupby('Category').agg({'App':'count'})
cat_merged_df = pd.merge(cat_number, category_installs, on='Category', how='inner')

scatter = px.scatter(cat_merged_df, x='App', y='Installs', title='Category Concentration',
                     size='App', hover_name=cat_merged_df.index, color='Installs')
scatter.update_layout(xaxis_title="Number of Apps (Lower=More Concentrated)",
                      yaxis_title="Installs",
                      yaxis=dict(type='log'))
scatter.show()

# Step 11: Extracting Nested Column Data - Genres
stack = df_apps_clean.Genres.str.split(';', expand=True).stack()
num_genres = stack.value_counts()

bar = px.bar(x=num_genres.index[:15], y=num_genres.values[:15], title='Top Genres',
             hover_name=num_genres.index[:15], color=num_genres.values[:15],
             color_continuous_scale='Agsunset')
bar.update_layout(xaxis_title='Genre', yaxis_title='Number of Apps', coloraxis_showscale=False)
bar.show()

# Step 12: Grouped Bar Chart - Free vs Paid Apps
df_free_vs_paid = df_apps_clean.groupby(['Category','Type'], as_index=False).agg({'App':'count'})

g_bar = px.bar(df_free_vs_paid, x='Category', y='App', color='Type', barmode='group',
               title='Free vs Paid Apps by Category')
g_bar.update_layout(xaxis_title='Category', yaxis_title='Number of Apps',
                    xaxis={'categoryorder':'total descending'}, yaxis=dict(type='log'))
g_bar.show()

# Step 13: Box Plot - Installs by App Type
box = px.box(df_apps_clean, y='Installs', x='Type', color='Type', notched=True, points='all',
             title='How Many Downloads are Paid Apps Giving Up?')
box.update_layout(yaxis=dict(type='log'))
box.show()

# Step 14: Box Plot - Revenue Estimates by Category
df_paid_apps = df_apps_clean[df_apps_clean['Type']=='Paid']
box_revenue = px.box(df_paid_apps, x='Category', y='Revenue_Estimate',
                     title='How Much Can Paid Apps Earn?')
box_revenue.update_layout(xaxis_title='Category', yaxis_title='Paid App Ballpark Revenue',
                          xaxis={'categoryorder':'min ascending'}, yaxis=dict(type='log'))
box_revenue.show()

# Step 15: Box Plot - Pricing by Category
box_price = px.box(df_paid_apps, x='Category', y='Price', title='Price per Category')
box_price.update_layout(xaxis_title='Category', yaxis_title='Paid App Price',
                        xaxis={'categoryorder':'max descending'}, yaxis=dict(type='log'))
box_price.show()
