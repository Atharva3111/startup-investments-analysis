import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load and clean dataset
@st.cache_data
def load_data():
    df = pd.read_csv('investments_VC.csv', encoding='ISO-8859-1')
    df.columns = df.columns.str.strip()
    df['funding_total_usd'] = df['funding_total_usd'].replace('[\$,]', '', regex=True)
    df['funding_total_usd'] = pd.to_numeric(df['funding_total_usd'], errors='coerce')
    df['first_funding_at'] = pd.to_datetime(df['first_funding_at'], errors='coerce')
    df['founded_year'] = pd.to_numeric(df['founded_year'], errors='coerce')
    df.fillna({'market': 'Unknown'}, inplace=True)
    df_india = df[df['country_code'] == 'IND'].copy()
    return df, df_india

df, df_india = load_data()

st.title("🇮🇳 Indian Startup Investments Dashboard")

# Sidebar filters
st.sidebar.header("Filter Options")
year_filter = st.sidebar.slider("Founded Year", int(df_india['founded_year'].min()), int(df_india['founded_year'].max()), (2000, 2024))
sector_filter = st.sidebar.multiselect("Select Sectors", options=df_india['market'].dropna().unique())

# Apply filters
filtered_df = df_india[(df_india['founded_year'] >= year_filter[0]) & (df_india['founded_year'] <= year_filter[1])]
if sector_filter:
    filtered_df = filtered_df[filtered_df['market'].isin(sector_filter)]

st.markdown(f"### Startups Found: {filtered_df.shape[0]}")

# Total Funding Over the Years
st.subheader("Total Funding Over the Years")
funding_by_year = filtered_df.groupby('founded_year')['funding_total_usd'].sum()
fig, ax = plt.subplots(figsize=(12,5))
sns.lineplot(x=funding_by_year.index, y=funding_by_year.values, marker='o', ax=ax)
ax.set_xlabel("Year")
ax.set_ylabel("Total Funding (USD)")
st.pyplot(fig)

# Top 10 Funded Sectors (market column)
st.subheader("Top 10 Funded Sectors")
top_sectors = filtered_df.groupby('market')['funding_total_usd'].sum().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(x=top_sectors.values, y=top_sectors.index, palette='viridis', ax=ax)
ax.set_xlabel("Total Funding (USD)")
ax.set_ylabel("Sector")
st.pyplot(fig)

# Top Countries by Total Funding (from full dataset)
st.subheader("Top Countries by Total Funding")
top_countries = df.groupby('country_code')['funding_total_usd'].sum().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(x=top_countries.values, y=top_countries.index, palette='magma', ax=ax)
ax.set_xlabel("Total Funding (USD)")
ax.set_ylabel("Country Code")
st.pyplot(fig)

# Most Active Funding Rounds (sum of funding round columns)
st.subheader("Most Active Funding Rounds")
funding_round_cols = ['seed', 'venture', 'equity_crowdfunding', 'undisclosed', 'convertible_note',
                      'debt_financing', 'angel', 'grant', 'private_equity', 'post_ipo_equity',
                      'post_ipo_debt', 'secondary_market', 'product_crowdfunding',
                      'round_A', 'round_B', 'round_C', 'round_D', 'round_E', 'round_F', 'round_G', 'round_H']

# Sum count of rounds (assuming these columns are counts or indicators)
round_activity = filtered_df[funding_round_cols].sum().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(12,5))
sns.barplot(x=round_activity.values, y=round_activity.index, palette='coolwarm', ax=ax)
ax.set_xlabel("Number of Rounds")
ax.set_ylabel("Funding Round Type")
st.pyplot(fig)


# Top Funded Cities
st.subheader("Top 10 Funded Indian Cities")
top_cities = filtered_df.groupby('city')['funding_total_usd'].sum().nlargest(10).reset_index()
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=top_cities, y='city', x='funding_total_usd', palette='crest', ax=ax)
ax.set_xlabel("Total Funding (USD)")
ax.set_ylabel("City")
st.pyplot(fig)

# Top Funded Companies
st.subheader("Top 10 Funded Companies")
top_companies = filtered_df[['name', 'funding_total_usd']].dropna().sort_values(by='funding_total_usd', ascending=False).head(10)
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=top_companies, y='name', x='funding_total_usd', palette='flare', ax=ax)
ax.set_xlabel("Total Funding (USD)")
ax.set_ylabel("Company")
st.pyplot(fig)

# Startups Founded Per Year
st.subheader("Startups Founded Per Year")
founding_trend = filtered_df['founded_year'].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(x=founding_trend.index, y=founding_trend.values, ax=ax)
ax.set_xlabel("Year")
ax.set_ylabel("Number of Startups")
st.pyplot(fig)

# Funding Stage Popularity
st.subheader("Funding Stage Popularity")
funding_stages = ['seed', 'venture', 'angel', 'grant', 'private_equity']
stage_counts = filtered_df[funding_stages].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x=stage_counts.index, y=stage_counts.values, palette='pastel', ax=ax)
ax.set_ylabel("Number of Rounds")
st.pyplot(fig)

# Download filtered data button
st.markdown("---")
if st.button("Download Filtered Data as CSV"):
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download CSV", data=csv, file_name='filtered_indian_startups.csv', mime='text/csv')
