import streamlit as st
import pandas as pd
import math
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='GDP dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    # Convert years from string to integers
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])

    return gdp_df

gdp_df = get_gdp_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: GDP dashboard

Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great (and did I mention _free_?) source of data.
'''

# Add some spacing
''
''

min_value = gdp_df['Year'].min()
max_value = gdp_df['Year'].max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

countries = gdp_df['Country Code'].unique()

if not len(countries):
    st.warning("Select at least one country")

selected_countries = st.multiselect(
    'Which countries would you like to view?',
    countries,
    ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

''
''
''

# Filter the data
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries))
    & (gdp_df['Year'] <= to_year)
    & (from_year <= gdp_df['Year'])
]

st.header('GDP over time', divider='gray')

''

st.line_chart(
    filtered_gdp_df,
    x='Year',
    y='GDP',
    color='Country Code',
)

''
''


first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

st.header(f'GDP in {to_year}', divider='gray')

''

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]

    with col:
        first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
        last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000

        if math.isnan(first_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country} GDP',
            value=f'{last_gdp:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )

import streamlit as st
import pandas as pd


# --- PAGE CONFIGURATION ---
st.set_page_config(
   page_title="Penguins Data Analysis",
   page_icon="🐧",
   layout="wide",
   initial_sidebar_state="expanded",
)


# --- DATA LOADING ---
# Using st.cache_data to avoid reloading data on every interaction
@st.cache_data
def load_data():
   """Loads the palmer penguins dataset from a public URL."""
   url = "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/inst/extdata/penguins.csv"
   df = pd.read_csv(url)
   # Drop rows with missing values for simplicity in this demo
   df.dropna(inplace=True)
   return df


df = load_data()


# --- APP TITLE AND DESCRIPTION ---
st.title("🐧 Palmer Penguins Data Analysis")
st.markdown("""
This application performs a simple exploratory data analysis (EDA) on the Palmer Penguins dataset.
Use the filters in the sidebar to explore the relationships between different measurements of the penguins.
""")


# --- SIDEBAR FOR FILTERS ---
st.sidebar.header("Filter Your Penguins")


# Filter for species
species = st.sidebar.multiselect(
   "Select Species",
   options=df["species"].unique(),
)


# Filter for island
island = st.sidebar.multiselect(
   "Select Island",
   options=df["island"].unique(),
)


# Filter for sex
sex = st.sidebar.multiselect(
   "Select Sex",
   options=df["sex"].unique(),
)


# Filter for body mass
min_mass, max_mass = int(df["body_mass_g"].min()), int(df["body_mass_g"].max())
body_mass_slider = st.sidebar.slider(
   "Select Body Mass (g)",
   min_value=min_mass,
   max_value=max_mass,
   value=(min_mass, max_mass),
)


# --- FILTERING THE DATAFRAME ---
# Start with the full dataframe and apply filters sequentially
df_selection = df.copy()


# Apply multiselect filters only if a selection has been made for that filter
if species:
   df_selection = df_selection[df_selection["species"].isin(species)]
if island:
   df_selection = df_selection[df_selection["island"].isin(island)]
if sex:
   df_selection = df_selection[df_selection["sex"].isin(sex)]


# Always apply the slider filter
df_selection = df_selection[
   (df_selection["body_mass_g"] >= body_mass_slider[0]) &
   (df_selection["body_mass_g"] <= body_mass_slider[1])
]




# Display error message if no data is selected
if df_selection.empty:
   st.warning("No data available for the selected filters. Please adjust your selection.")
   st.stop() # Halts the app execution


# --- MAIN PAGE CONTENT ---
st.subheader("📊 Key Metrics")


# --- DISPLAY KEY METRICS ---
col1, col2, col3 = st.columns(3)
with col1:
   st.metric(label="Total Penguins", value=df_selection.shape[0])
with col2:
   avg_bill_length = round(df_selection["bill_length_mm"].mean(), 1)
   st.metric(label="Avg. Bill Length (mm)", value=avg_bill_length)
with col3:
   avg_body_mass = round(df_selection["body_mass_g"].mean(), 1)
   st.metric(label="Avg. Body Mass (g)", value=f"{avg_body_mass / 1000:.2f} kg")


st.markdown("---")


# --- VISUALIZATIONS ---
st.subheader("📈 Visualizations")


# Arrange charts in columns
viz_col1, viz_col2 = st.columns(2)


with viz_col1:
   # Scatter plot: Bill Length vs. Bill Depth
   st.subheader("Bill Length vs. Bill Depth")
   # st.scatter_chart can use a color parameter to differentiate categories
   st.scatter_chart(
       data=df_selection,
       x="bill_length_mm",
       y="bill_depth_mm",
       color="species"
   )


with viz_col2:
   # Bar Chart: Average Body Mass by Species
   st.subheader("Average Body Mass by Species")
   # Group data to calculate average body mass for the bar chart
   avg_mass_by_species = df_selection.groupby('species')['body_mass_g'].mean().round(1)
   st.bar_chart(avg_mass_by_species)




# --- DISPLAY RAW DATA ---
with st.expander("View Raw Data"):
   st.dataframe(df_selection)
   st.markdown(f"**Data Dimensions:** {df_selection.shape[0]} rows, {df_selection.shape[1]} columns")


st.markdown("---")
st.write("Data Source: [Palmer Penguins Dataset](https://github.com/allisonhorst/palmerpenguins)")








