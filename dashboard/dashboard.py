import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from PIL import Image

bike_rent = 'bikerent.png'
bike_rent_image = Image.open(bike_rent)

# Data Gathering

byHour_df = pd.read_csv(r'../dataset/hour.csv')
byDay_df = pd.read_csv(r'../dataset/day.csv')

# Data Cleaning

byHour_df['dteday'] = pd.to_datetime(byHour_df['dteday'])
byDay_df['dteday'] = pd.to_datetime(byDay_df['dteday'])

st.header('MIFTAHUL BIKE RENT DASHBOARD :star:')

# Filtering Date

min_date = byDay_df['dteday'].min()
max_date = byDay_df['dteday'].max()

with st.sidebar:
    st.image(bike_rent_image, caption='WELCOME', use_column_width=True)

    selected_dates = st.date_input(
        label='Time Span',
        min_value=min_date,max_value=max_date,
        value=[min_date, max_date]
    )

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date = selected_dates[0]
        end_date = selected_dates[0]

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

inputHour_df = byHour_df[(byHour_df['dteday'] >= start_date) & (byHour_df['dteday'] <= end_date)]
inputDay_df = byDay_df[(byDay_df['dteday'] >= start_date) & (byDay_df['dteday'] <= end_date)]

# Display 1

st.subheader('Bike Rentals by Customer Category')
st.text(f'{start_date.date()} until {end_date.date()}')

col1, col2, col3 = st.columns(3)

with col1:
    val1 = inputDay_df['casual'].sum()
    st.metric("Casual User (units)", value=val1)

with col2:
    val2 = inputDay_df['registered'].sum()
    st.metric("Registered User (units)", value=val2)

with col3:
    val3 = inputDay_df['cnt'].sum()
    st.metric("Total Bike Rent (units)", value=val3)

casual_total = inputDay_df['casual'].sum()
registered_total = inputDay_df['registered'].sum()
total_bike_rent = inputDay_df['cnt'].sum()

casual_pct = casual_total / total_bike_rent * 100
registered_pct = registered_total / total_bike_rent * 100

fig, ax = plt.subplots()
ax.pie([casual_pct, registered_pct], labels=['Casual', 'Registered'],
       autopct='%1.1f%%', startangle=90, colors=['lightgray', 'skyblue'])
ax.axis('equal')
st.pyplot(fig)

# Display 2

st.subheader('Bike Rentals by Rentals in A Day')
st.text(f'{start_date.date()} until {end_date.date()}')

daily_rentals = inputDay_df.groupby('dteday')['cnt'].sum().reset_index()
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(inputDay_df['dteday'], inputDay_df['cnt'], linestyle='-', color='black')
ax.set_title('Total Bike Rentals by A Day', fontsize=16)
ax.set_xlabel('Date', fontsize=14)
ax.set_ylabel('Total Rental', fontsize=14)
ax.set_facecolor('lightblue')
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=45)
st.pyplot(fig)

# Display 3

st.subheader('Bike Rentals by User Time Segment')
st.text(f'{start_date.date()} until {end_date.date()}')
st.text('Early Morning \t= 02:00 AM - 04:59 AM\nMorning \t= 05:00 AM - 10:59 AM\nAfternoon \t= 11:00 AM - 02:59 PM\n'
        'Evening \t= 03:00 PM - 05:59 PM\nNight \t\t= 06:00 PM - 09:59 PM\nMidnight \t= 10:00 PM - 01:59 AM')

time_segments = {
    'Early Morning': (2, 4),
    'Morning': (5, 10),
    'Afternoon': (11, 14),
    'Evening': (15, 17),
    'Night': (18, 21),
    'Midnight': (22, 1)
}

def segmentation(hour):
    for segment, (start, end) in time_segments.items():
        if start <= hour <= end or (start > end and (hour >= start or hour <= end)):
            return segment
    return None

inputHour_df['time_segment'] = inputHour_df['hr'].apply(segmentation)

casual_user = inputHour_df.groupby('time_segment')['casual'].sum()
casual_user = casual_user.sort_values(ascending=True)

registered_user = inputHour_df.groupby('time_segment')['registered'].sum()
registered_user = registered_user.sort_values(ascending=True)

total_user = inputHour_df.groupby('time_segment')['cnt'].sum()
total_user = total_user.sort_values(ascending=True)

segmented_df = pd.DataFrame({
    'Casual Users': casual_user,
    'Registered Users': registered_user,
    'Total Users': total_user
})

segmented_df = segmented_df.sort_values(by='Total Users', ascending=False)
segmented_df.index.name = 'Time Segment'

fig, ax = plt.subplots(figsize=(10, 6))
groups = ['Total Users', 'Registered Users', 'Casual Users']
bars = segmented_df[groups].plot(kind='barh', ax=ax, color=['gray', 'blue', 'yellow'])

ax.set_title('User Segmentation by Time Segment', fontsize=16)
ax.set_xlabel('Number of Users', fontsize=14)
ax.set_ylabel('Time Segment', fontsize=14)
ax.set_facecolor('lightblue')


for bar in bars.containers:
    for rectangle in bar:
        width = rectangle.get_width()
        percentage = (width / segmented_df['Total Users'].sum()) * 100
        ax.text(width, rectangle.get_y() + rectangle.get_height() / 2, f'{percentage:.1f}%',
                va='center', ha='left', fontsize=10, color='black')

st.pyplot(fig)

# Display 4

st.subheader('Bike Rentals by Season and Weather Situation')
st.text(f'{start_date.date()} until {end_date.date()}')

season_name = {
    1: 'Spring',
    2: 'Summer',
    3: 'Fall',
    4: 'Winter'
}

weather_name = {
    1: 'Clear, Cloudy',
    2: 'Mist, Broken Cloud',
    3: 'Light Snow, Light Rain',
    4: 'Heavy Rain, Thunderstorm'
}

inputDay_df['season'] = inputDay_df['season'].replace(season_name)
inputDay_df['weathersit'] = inputDay_df['weathersit'].replace(weather_name)

season_weather_df = inputDay_df.groupby(['season', 'weathersit'])['cnt'].sum().reset_index()

pivot_table = season_weather_df.pivot(index='season', columns='weathersit', values='cnt')
fig, ax = plt.subplots(figsize=(10, 6))
bars = pivot_table.plot(kind='bar', ax=ax,  color=['grey', 'blue', 'yellow'])
ax.set_title('Total Bike Rentals by Season and Weather Situation', fontsize=16)
ax.set_xlabel('Season', fontsize=14,)
ax.set_ylabel('Total Rentals', fontsize=14)
ax.set_facecolor('lightblue')
plt.xticks(rotation=45)

total_rentals = pivot_table.sum().sum()
for bar in bars.containers:
    for rectangle in bar:
        width = rectangle.get_height()
        percentage = (width / total_rentals) * 100
        ax.text(
            rectangle.get_x() + rectangle.get_width() / 2, width + 0.5,
            f'{percentage:.1f}%', ha='center', fontsize=10, color='black')

ax.legend(title='Weather Situation', bbox_to_anchor=(1.05, 1), loc='upper left')
st.pyplot(fig)

# Display 5

st.subheader('Bike Rentals by Windspeed Clustering')
st.text(f'{start_date.date()} until {end_date.date()}')

def windspeed_cluster(windspeed):
    if 0 <= windspeed <= 0.33:
        return 'LOW'
    elif 0.34 <= windspeed <= 0.66:
        return 'MEDIUM'
    else:
        return 'HIGH'

inputHour_df['windspeed_cluster'] = inputHour_df['windspeed'].apply(windspeed_cluster)
windspeed_groups = inputHour_df.groupby('windspeed_cluster')['cnt'].sum().reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(windspeed_groups['windspeed_cluster'], windspeed_groups['cnt'], color=['grey', 'blue', 'yellow'])

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, yval, f'{yval:,}',
            ha='center', va='bottom')

ax.set_title('Total Bike Rentals by Windspeed Cluster', fontsize=16)
ax.set_xlabel('Windspeed Cluster', fontsize=14)
ax.set_ylabel('Total Rentals', fontsize=14)
ax.set_facecolor('lightblue')
plt.tight_layout()
st.pyplot(fig)
