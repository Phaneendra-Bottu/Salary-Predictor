import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def shorten_categories(categories, cutoff):
    categorical_map = {}
    for i in range(len(categories)):
        if categories.values[i] >= cutoff:
            categorical_map[categories.index[i]] = categories.index[i]
        else:
            categorical_map[categories.index[i]] = 'Other'
    return categorical_map


def clean_experience(x):
    if x == 'More than 50 years':
        return 50
    if x == 'Less than 1 year':
        return 0.5
    return float(x)


def clean_education(x):
    if 'Bachelor’s degree' in x:
        return 'Bachelor’s degree'
    if 'Master’s degree' in x:
        return 'Master’s degree'
    if 'Professional degree' in x or 'Other doctoral' in x:
        return 'Post grad'
    return 'Less than a Bachelors'


exchange_rates = {
    "USD	United States dollar": 1.0,
    "EUR European Euro": 1.07,
    "GBP	Pound sterling": 1.23,
    "CAD	Canadian dollar": 0.78,
    "INR	Indian rupee": 0.012,
    "AUD	Australian dollar": 0.64,
    "BRL	Brazilian real": 0.20,
    "SEK	Swedish krona": 0.11,
    "PLN	Polish zloty": 0.27,
    "CHF	Swiss franc": 1.12,
    "DKK	Danish krone": 0.14,
    "NOK	Norwegian krone": 0.09,
    "ILS	Israeli new shekel": 0.25,
    "RUB	Russian ruble": 0.011,
    "NZD	New Zealand dollar": 0.59
}


def convert_to_usd(row):
    currency = row['Currency']
    salary = row['Salary']
    exchange_rate = exchange_rates.get(currency)
    if exchange_rate is not None:
        return salary * exchange_rate
    else:
        return None


@st.cache_data
def load_data():
    df = pd.read_csv("survey_results_public.csv")
    df = df[["Country", "EdLevel", "YearsCodePro", "Employment", "CompTotal", "Currency"]]
    df = df.rename({"CompTotal": "Salary"}, axis=1)

    df = df[df["Salary"].notnull()]
    df = df.dropna()
    df = df[df["Employment"] == "Employed full-time"]
    df = df.drop("Employment", axis=1)

    country_map = shorten_categories(df.Country.value_counts(), 400)
    df['Country'] = df['Country'].map(country_map)

    currency_map = shorten_categories(df.Currency.value_counts(), 300)
    df['Currency'] = df['Currency'].map(currency_map)

    df['Salary'] = df.apply(convert_to_usd, axis=1)
    df = df.drop(['Currency'], axis=1)

    df = df[df["Salary"] <= 300000]
    df = df[df["Salary"] >= 5000]
    df = df[df['Country'] != 'Other']

    df["YearsCodePro"] = df["YearsCodePro"].apply(clean_experience)
    df["EdLevel"] = df["EdLevel"].apply(clean_education)
    return df


df = load_data()


def show_explore_page():
    st.title("Explore Software Engineer Salaries")

    st.write("""### Stack Overflow Developer Survey 2020""")

    data = df["Country"].value_counts()

    fig1, ax1 = plt.subplots()
    ax1.pie(data, labels=data.index, autopct="%1.1f%%", shadow=True, startangle=90)
    ax1.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.write("""#### Number of Data from different countries""")

    st.pyplot(fig1)

    st.write("""#### Mean Salary Based On Country""")

    data = df.groupby(["Country"])["Salary"].mean().sort_values(ascending=True)
    st.bar_chart(data)

    st.write("""#### Mean Salary Based On Experience""")

    data = df.groupby(["YearsCodePro"])["Salary"].mean().sort_values(ascending=True)
    st.line_chart(data)

