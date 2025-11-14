import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path



st.title('Marriages in Alberta, Canada')
st.write('This file display the trend of marriages in Alberta, Canada. Particularly,\
         those that count as first mattiages for both parties.\n' \
         'The data was taken from https://open.canada.ca/en')

marriages = pd.read_excel(Path('data/marriage-first-marriages-age-of-groom-by-age-of-bride.xlsx'), skiprows=2) 
st.write(marriages.head())


annual_marriages = marriages.loc[marriages['Age of Groom (Years)'] == 'Total',['Calendar Year','Total']]\
                    .copy().reset_index(drop=True)


annual_marriages_chart = (
    alt.Chart(annual_marriages)
    .mark_line(color='red')
    .encode(
        x=alt.X("Calendar Year:O", title="Calendar Year"),
        y=alt.Y("Total:Q", title="Total Marriages"),
    )
    .properties(
        title="First Marriages per Year",
        width="container",
        height=400
    )
    .interactive()
)


## Number of Newborns

newborns = pd.read_csv(Path('data/13100415.csv') )

total_newborns = newborns.loc[(newborns.GEO == 'Alberta, place of residence of mother') 
         & (newborns.UOM == 'Number')
         & (newborns['Month of birth']	== 'Total, month of birth')
         & (newborns.REF_DATE >= 2001)
         & (newborns.REF_DATE <= 2024)
         , ['REF_DATE','VALUE']]


total_newborns_chart = (
    alt.Chart(total_newborns
            , title=f"Average Age of First Marriage"
            )
    .mark_line(color="green")
    .encode(
        x=alt.X("REF_DATE:O", title="Year"),
        y=alt.Y("VALUE:Q", title="Total Newborns")
    ).interactive()
)

#st.altair_chart(total_newborns_chart, use_container_width=True)

#st.altair_chart(annual_marriages_chart, use_container_width=True)

combined = alt.layer(
    total_newborns_chart,
    annual_marriages_chart
).resolve_scale(
    y='independent'
)

st.altair_chart(combined, use_container_width=True)
st.write('The number of marriages in Alberta has increased over the years. However, there was a sharp drop in 2020, probably due to the pandemic.')


st.header('Gender Analysis')
# Woman
marriages_woman = marriages.loc[marriages['Age of Groom (Years)'] == 'Total',:]\
    .drop(columns=['Total','Age of Groom (Years)'])
age_groups = marriages_woman.columns[1:]
marriages_woman = marriages_woman.melt(id_vars=['Calendar Year'],value_vars=age_groups, value_name='Women Number',var_name='Group Age')

# Men
marriages_men = marriages.loc[marriages['Age of Groom (Years)'] != 'Total',['Calendar Year','Age of Groom (Years)','Total']]\
    .rename(columns={'Total':'Men Number','Age of Groom (Years)':'Group Age'})


marriages_gender = pd.merge(marriages_men,marriages_woman, on=['Group Age','Calendar Year'])

blue_15 = ["#e3f2fd","#d0e7fb","#bddcf9","#aacff7","#97c2f4","#84b5f1","#71a8ee","#5e9beb","#4b8ee7","#3881e3","#2573df","#1265db","#0b57c1","#06479e","#003377" ]
purple_15 = ["#f3e5f5", "#e8d4ee", "#ddc3e7", "#d2b2e0", "#c7a1d9","#bc90d2", "#b17fcb", "#a66ec4", "#9b5dbd", "#8f4cb6","#833baf", "#772aa8", "#6b19a1", "#5e089a", "#4a0072"]
ordered_ages = ["<15", "15-19", "20-24", "25-29", "30-34", "35-39","40-44", "45-49", "50-54", "55-59", "60-64","65-69", "70-74", "75+", "NS"]


gender = st.radio('**Choose a Gender:man::woman:**',['Men','Women'], index = 0)
marriages_gender_chart = (
    alt.Chart(marriages_gender, title=f"First Marriages per Group Age for {gender}")
    .mark_line()
    .encode(
        x="Calendar Year:O",
        y=f"{gender} Number:Q",
        color=alt.Color("Group Age:N"
                        , scale=alt.Scale(range=(purple_15 if gender=='Women' else blue_15))
                        , sort=ordered_ages),
        detail="Group Age:N"
    ).interactive()
)

st.altair_chart(marriages_gender_chart, use_container_width=True)

st.write(('The number of women who marry before the age of 25 has decreased significantly, while the number of those who marry between 25–29 or 30–35 has increased considerably.\
          In the case of men, the number of men who marry after the age of 30 has always been higher than the number of men who marry before the age of 25.'))



st.header('Mean Age per Gender')
marriages_gender_accumulated = marriages_gender.copy()
marriages_gender_accumulated['Group Age'] = marriages_gender_accumulated['Group Age'].copy().replace(to_replace={'<15':15, '15-19':17, '20-24':22, '25-29':27, '30-34':32, '35-39':37, '40-44':42, '45-49':47, '50-54':52, '55-59':57, '60-64':62, '65-69':67, '70-74':72, '75+':80, 'NS':80})
marriages_gender_accumulated['Men Accumulated Years'] = marriages_gender_accumulated['Group Age']*marriages_gender_accumulated['Men Number']
marriages_gender_accumulated['Women Accumulated Years'] = marriages_gender_accumulated['Group Age']*marriages_gender_accumulated['Women Number']
marriages_gender_accumulated = marriages_gender_accumulated.groupby('Calendar Year').sum().reset_index()
annual_marriages['Men Mean Age'] = (marriages_gender_accumulated['Men Accumulated Years']/annual_marriages.Total.values).values
annual_marriages['Women Mean Age'] = (marriages_gender_accumulated['Women Accumulated Years']/annual_marriages.Total.values).values

marriages_gender_age_chart = (
    alt.Chart(annual_marriages.melt(id_vars = 'Calendar Year', value_vars=["Women Mean Age", "Men Mean Age"],var_name="Gender",value_name="Mean Age")
            , title=f"Average Age of First Marriage")
    .mark_line()
    .encode(
        x="Calendar Year:O",
        y="Mean Age:Q",
        color=alt.Color('Gender:N', scale=alt.Scale(range= ["#1e3a8a","#4a0072"]))
    ).interactive()
)

st.altair_chart(marriages_gender_age_chart, use_container_width=True)


