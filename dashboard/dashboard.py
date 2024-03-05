import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Helper functions

def create_monthly_users_df(df):
    df['date'] = pd.to_datetime(df['date'])
    monthly_users_df = df.resample(rule='M', on='date').agg({
        "total": "sum",
        "registered": "sum",
        "unregistered": "sum"
    })
    monthly_users_df.index = monthly_users_df.index.strftime('%b-%Y')
    monthly_users_df.rename(columns={"casual": "unregistered"}, inplace=True)
    monthly_users_df['total'] = monthly_users_df['registered'] + monthly_users_df['unregistered']
    return monthly_users_df


def create_users_percentage_df(df):
    total_users = df['total'].sum()
    workingday_users = df[df['workingday'] == 'Yes']['total'].sum()
    non_workingday_users = df[df['workingday'] == 'No']['total'].sum()
    percentage_workingday = (workingday_users / total_users) * 100
    percentage_non_workingday = (non_workingday_users / total_users) * 100
    return percentage_workingday, percentage_non_workingday

def create_season_rentals_df(df):
    season_rentals = df.groupby('season')['total'].sum()
    season_rentals_df = pd.DataFrame({
        'Season': ['Fall', 'Spring', 'Summer', 'Winter'],
        'Total Rentals': season_rentals.values
    })
    return season_rentals_df

def create_weather_rentals_df(df):
    return df.groupby(by="weathersit").agg({
        "registered": "sum",
        "unregistered": "sum",
        "total": "sum"
    }).sort_values(by='total', ascending=False)

# Load data
df = pd.read_csv("day_data.csv")

min_date = pd.to_datetime(df['date']).dt.date.min()
max_date = pd.to_datetime(df['date']).dt.date.max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("logo.jpg")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Date Range',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
# menyimpan data yang telah difilter ke dalam main_df
main_df = df[(df["date"] >= str(start_date)) & 
             (df["date"] <= str(end_date))]

# memanggil helper function
monthly_users_df = create_monthly_users_df(main_df)
users_percentage_df = create_users_percentage_df(main_df)
season_rentals_df = create_season_rentals_df(df)
weather_rentals_df = create_weather_rentals_df(df)

# Header
st.title("Capital Bike Sharing Dashboard")

# Display total users
total_users = df['total'].sum()
st.metric("Total Users", value=total_users)

# monthly users
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(monthly_users_df.index, monthly_users_df['registered'],
        label='Registered Users', marker='o', color='tab:blue')
ax.plot(monthly_users_df.index, monthly_users_df['unregistered'],
        label='Unregistered Users', marker='o', color='tab:green')
ax.plot(monthly_users_df.index, monthly_users_df['total'],
        label='Total Users', marker='o', color='tab:red')
ax.set_title('Monthly Users')
ax.set_xlabel('Month')
ax.set_ylabel('Number of Users')
ax.legend()
ax.tick_params(axis='x', labelrotation=45)
st.pyplot(fig)

tab1, tab2, tab3 = st.tabs(["Working Day vs. Non-Working Day", "Seasonal Rentals", "Weather Rentals"])

# visualisasi 1 - Perbandingan Jumlah Peminjaman Sepeda pada Hari Kerja dan Non-Kerja
with tab1:
    st.header("Perbandingan Jumlah Peminjaman Sepeda pada Hari Kerja dan Non-Kerja")
    percentage_workingday, percentage_non_workingday = create_users_percentage_df(df)
    labels = ['Working Day', 'Non-Working Day']
    sizes = [percentage_workingday, percentage_non_workingday]
    colors = ['#ff9999', '#66b3ff']
    explode = (0.1, 0)  # Explode "Working Day" slice

    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    ax.set_title('Percentage of Bike Rentals on Working vs Non-Working Days')
    ax.axis('equal')  # Ensure pie chart is a circle
    st.pyplot(fig)
    
with tab1:
    with st.expander("See explanation"):
        st.write(
            """Pada hari kerja didapatkan jumlah peminjaman sepeda yang lebih tinggi dibandingkan
            pada hari non-kerja,
            dengan persentase hari kerja sebesar 69.6% dan hari non-kerja sebesar 30.4%. Temuan
            ini memberikan wawasan bagi perusahaan untuk meningkatkan ketersediaan sepeda pada hari
            kerja guna memenuhi permintaan pelanggan yang lebih tinggi pada periode tersebut. 
            """
        )

# Visualisasi 2 - Jumlah Peminjaman Sepeda Berdasarkan Musim
with tab2:
    st.subheader("Jumlah Peminjaman Sepeda Berdasarkan Musim")
    fig, ax = plt.subplots()
    ax.bar(season_rentals_df['Season'], season_rentals_df['Total Rentals'],
           color=['skyblue', 'lightgreen', 'lightcoral', 'lightsalmon'])
    ax.set_title('Total Bike Rentals Based on Season')
    ax.set_xlabel('Season')
    ax.set_ylabel('Total Rentals')
    st.pyplot(fig)
    
with tab2:
    with st.expander("See explanation"):
        st.write(
            """Peminjaman sepeda mencapai puncaknya pada musim panas (fall), hal ini
            memberikan peluang bagi perusahaan untuk merancang strategi penyesuaian
            harga atau penawaran khusus yang dapat meningkatkan pendapatan selama
            periode sibuk ini.
            """
        )

# Visualisasi 3 - Distribusi Jumlah Peminjaman Sepeda berdasarkan Kondisi Cuaca
with tab3:
    st.subheader("Distribusi Jumlah Peminjaman Sepeda berdasarkan Kondisi Cuaca")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x='weathersit', y='total', data=df, palette='viridis', ax=ax)
    ax.set_title('Distribution of Bike Rentals Based on Weather Condition')
    ax.set_xlabel('Weather Condition')
    ax.set_ylabel('Bike Rentals')
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(['Clear', 'Mist', 'Light Snow/Rain', 'Heavy Rain/Ice Pellets'])
    st.pyplot(fig)
    
with tab3:
    with st.expander("See explanation"):
        st.write(
            """Hubungan antara kondisi cuaca dan jumlah peminjaman sepeda cukup signifikan,
            dengan peminjaman yang meningkat pada cuaca cerah dan menurun pada cuaca buruk.
            Perusahaan dapat mengoptimalkan stok sepeda sesuai prakiraan cuaca untuk
            memenuhi permintaan yang berubah-ubah, meningkatkan layanan pelanggan, dan efisiensi operasional.
            """
        )