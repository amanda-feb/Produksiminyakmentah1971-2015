#import packages
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

#TITLE
st.set_page_config(layout="wide")  # this needs to be the first Streamlit command called
st.title("Produksi Minyak Mentah Dunia Pada Rentang 1971-2015")

#open file json
with open ("kode_negara_lengkap.json") as f :
    data1 = json.load(f)

#open csv file
data = pd.read_csv("produksi_minyak_mentah.csv")
df = pd.DataFrame(data, columns= ['kode_negara','tahun','produksi'])

#membuat list kode negara dari csv
countcode = list(df['kode_negara'].unique())

#list smua kode negara di json
allcode = [dic['alpha-3'] for dic in data1]

#filter yang bukan kode negara
organisation = [i for i in countcode if i not in allcode]

#menghapus yang buka kode negara
for i in organisation:
    df = df[df.kode_negara != i]
    if i in countcode:
        countcode.remove(i)

#membuat list yang berisi dictionary informasi negara dari json yang ada di csv
countryList = []
nl = []
for c in countcode:
    for d in data1:
        targetList = countryList if d.get('alpha-3') == c else nl
        targetList.append(d)

#membuat list negara, region, subregion yang ada di csv dari list dict yg sdh di filter
Country = [dic['name'] for dic in countryList]
alpha_3 = [dic['alpha-3'] for dic in countryList]
Year = list(df['tahun'])

codelist = dict(zip(Country, alpha_3))

#membuat list baru dengan data untuk summary
from operator import itemgetter
tuple_keys = ('name','alpha-2','alpha-3','country-code','region','sub-region')
get_keys = itemgetter(*tuple_keys)
summdata = [ dict(zip(tuple_keys,get_keys(d))) for d in countryList ]

for d in summdata:
    d['Nama Negara'] = d.pop('name')
    d['Kode Negara 2 Huruf'] = d.pop('alpha-2')
    d['Kode Negara 3 Huruf'] = d.pop('alpha-3')
    d['Kode Negara Angka'] = d.pop('country-code')
    d['Region'] = d.pop('region')
    d['Sub-Region'] = d.pop('sub-region')

# fungsi untuk memanggil summary yang dibutuhkan
def build_dict(seq, key):
    return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))

# Glosarium data negara di sidebar
st.sidebar.title("Glosarium Data Negara")
info = st.sidebar.selectbox("Pilih kode negara", sorted(alpha_3),
                            help='Anda akan mendapatkan ringkasan info negara tersebut')

country_by_name = build_dict(summdata, key="Kode Negara 3 Huruf")
country_info = country_by_name.get(info.upper())
del country_info["index"]

finalsum = [(v, k) for k, v in country_info.items()]

for (v, k) in finalsum[:]:
    st.sidebar.write(k.capitalize(), ':', v)
#################################################################################################
menu = st.radio(
     "What's your favorite movie genre",
     ('Grafik Produksi Minyak Mentah Suatu Negara Terhadap Waktu (Tahun)', 'Grafik Peringkat Produksi Minyak Mentah Pada Tahun Tertentu',
      'Grafik Peringkat Produksi Minyak Mentah Secara Kumulatif Pada Keseluruhan Tahun','Data Summary'))

if menu == 'Grafik Produksi Minyak Mentah Suatu Negara Terhadap Waktu (Tahun)':
     st.write("✨" * 55)
     # nomer 1
     st.header('Grafik Produksi Minyak Mentah Suatu Negara Terhadap Waktu (Tahun)')
     x = st.selectbox('Pilih Negara yang diinginkan', Country)

     # membuat dataframe yang diinginkan
     y = codelist[x]
     df1 = df.loc[df['kode_negara'] == y]

     # membuat plot
     fig = px.bar(df1, x="produksi", y="tahun", color="tahun", orientation='h',
                  title=f"Produksi Minyak Mentah Negara {x}")
     st.plotly_chart(fig, use_container_width=True)

elif menu == 'Grafik Peringkat Produksi Minyak Mentah Pada Tahun Tertentu':
    # nomer 2
    st.write("✨" * 55)
    st.header('Grafik Peringkat Produksi Minyak Mentah Pada Tahun Tertentu')

    # input tahun dan jumlah negara
    x2 = st.selectbox('Pilih Tahun', Year)
    y2 = st.number_input('Pilih Jumlah Negara', min_value=3, max_value=len(Country))

    # membuat dataframe yang diinginkan
    df2 = df[df["tahun"] == x2].sort_values("produksi", ascending=False)
    dfx = df2[:y2]

    # membuat plot
    fig2 = px.bar(dfx, x="produksi", y="kode_negara", color="kode_negara", orientation='h',
                  title=f"Produksi Minyak Mentah Terbesar Tahun {x2}")
    st.plotly_chart(fig2, use_container_width=True)

elif menu == 'Grafik Peringkat Produksi Minyak Mentah Secara Kumulatif Pada Keseluruhan Tahun':
    # nomer 3
    st.write("✨" * 55)
    st.header('Grafik Peringkat Produksi Minyak Mentah Secara Kumulatif Pada Keseluruhan Tahun')

    # Menambahkan kolom baru
    df['Total_Produksi'] = df.groupby(['kode_negara'])['produksi'].transform('sum')

    # Membuat data frame baru yang berisi kode negara dan total produksi saja
    df3 = df.drop_duplicates(subset=['kode_negara']).drop(
        columns='tahun').drop(columns='produksi').sort_values('Total_Produksi', ascending=False)

    # input jumlah negara
    y3 = st.number_input('Jumlah Negara', min_value=3, max_value=len(Country))

    # membuat dataframe baru yang menampilkan baris sesuai input
    dfy = df3[:y3]

    # plot horizontal bar
    fig3 = px.bar(dfy, x="Total_Produksi", y="kode_negara", color="kode_negara", orientation='h',
                  title=f"Produksi Minyak Mentah {y3} Besar Negara")
    st.plotly_chart(fig3, use_container_width=True)

else:
    # nomer 4
    st.write("✨" * 55)
    st.header('Data Summary')
    st.subheader("Data Kumulatif")
    col1, col2 = st.columns(2)

    # Menambahkan kolom baru
    df['Total_Produksi'] = df.groupby(['kode_negara'])['produksi'].transform('sum')

    # Membuat data frame baru yang berisi kode negara dan total produksi saja
    df3 = df.drop_duplicates(subset=['kode_negara']).drop(
        columns='tahun').drop(columns='produksi').sort_values('Total_Produksi', ascending=False)

    # data terbesar kumulatif
    with col1:
        st.markdown(f"**Data Negara dengan jumlah produksi terbesar secara kumulatif**")

        prodmax1 = df3[:1].iloc[0]["Total_Produksi"]
        st.write(f"Total Produksi: {prodmax1}")
        c1 = df3[:1].iloc[0]["kode_negara"]

        country_by_name1 = build_dict(summdata, key="Kode Negara 3 Huruf")
        country_info1 = country_by_name1.get(c1)
        del country_info1["index"]

        finalsum1 = [(v, k) for k, v in country_info1.items()]

        for (v, k) in finalsum1[:]:
            st.write(k.capitalize(), ':', v)

    # data terkecil kumulatif
    with col2:
        st.markdown(f"**Data Negara dengan jumlah produksi terkecil secara kumulatif**")
        dfmin = df3[df3.Total_Produksi != 0]

        df14min = dfmin.sort_values("Total_Produksi", ascending=True)

        prodmin = df14min[:1].iloc[0]["Total_Produksi"]
        st.write(f"Total Produksi: {prodmin}")
        c2 = df14min[:1].iloc[0]["kode_negara"]

        country_by_name2 = build_dict(summdata, key="Kode Negara 3 Huruf")
        country_info2 = country_by_name2.get(c2)
        del country_info2["index"]

        finalsum2 = [(v, k) for k, v in country_info2.items()]

        for (v, k) in finalsum2[:]:
            st.write(k.capitalize(), ':', v)

    # data nol kumulatif
    st.write("⟣", "−" * 132, "⟢")
    dfnoll = df3[df3.Total_Produksi == 0].drop(columns='Total_Produksi')
    # dari dfnol jadiin list or smthing trus dari si summdata kalo gaada alpha 3 nya di apus dari summdata trus
    # si summdata dijadiin df lalu jadiin tabel
    liii = []
    for i in list(dfnoll["kode_negara"]):
        for d in summdata:
            target = liii if d.get('Kode Negara 3 Huruf') == i else nl
            target.append(d)

    dfnoln = pd.DataFrame(liii)

    with st.container():
        st.markdown(f"**Data Negara dengan jumlah produksi Nol Secara Kumulatif**")
        tablen = go.Figure(data=[go.Table(
            header=dict(values=list(dfnoln.columns),
                        fill_color='#e2d34e',
                        align='left',
                        height=50,
                        font=dict(color='black', size=21),
                        ),
            cells=dict(values=[dfnoln['Nama Negara'], dfnoln['Kode Negara 2 Huruf'], dfnoln['Kode Negara 2 Huruf'],
                               dfnoln['Kode Negara Angka'], dfnoln['Region'], dfnoln['Sub-Region']],
                       fill_color='#6853b9',
                       align='left',
                       height=90,
                       font=dict(color='white', size=20)))
        ])
        tablen.update_layout(autosize=True, margin=dict(r=5, l=5, t=5, b=5))
        st.plotly_chart(tablen, use_container_width=True)

    # Summary berdasarkan tahun
    st.subheader("Data Pada Tahun Tertentu")
    x4 = st.selectbox('Input Tahun', Year)
    leftcol, rightcol = st.columns(2)

    # data terbesar
    with leftcol:
        st.markdown(f"**Data Negara dengan jumlah produksi terbesar pada tahun {x4}**")
        df24 = df[df["tahun"] == x4].sort_values("produksi", ascending=False)

        prodmax2 = df24[:1].iloc[0]["produksi"]
        st.write(f"Jumlah Produksi: {prodmax2}")
        c3 = df24[:1].iloc[0]["kode_negara"]

        country_by_name3 = build_dict(summdata, key="Kode Negara 3 Huruf")
        country_info3 = country_by_name3.get(c3)
        del country_info3["index"]

        finalsum3 = [(v, k) for k, v in country_info3.items()]

        for (v, k) in finalsum3[:]:
            st.write(k.capitalize(), ':', v)

    # data terkecil
    with rightcol:
        st.markdown(f"**Data Negara dengan jumlah produksi terkecil pada tahun {x4}**")
        dfmin2 = df[df.produksi != 0]
        df24min = dfmin2[dfmin2["tahun"] == x4].sort_values("produksi", ascending=True)

        prodmin2 = df24min[:1].iloc[0]["produksi"]
        st.write(f"Jumlah Produksi: {prodmin2}")
        c4 = df24min[:1].iloc[0]["kode_negara"]

        country_by_name4 = build_dict(summdata, key="Kode Negara 3 Huruf")
        country_info4 = country_by_name4.get(c4)
        del country_info4["index"]

        finalsum4 = [(v, k) for k, v in country_info4.items()]

        for (v, k) in finalsum4[:]:
            st.write(k.capitalize(), ':', v)

    # produksi nol pada tahun tertentu
    st.write("⟣", "−" * 132, "⟢")
    dfnol = df24[df24.produksi == 0].drop(columns='tahun').drop(columns='produksi').drop(columns='Total_Produksi')

    # memfilter list agar sesuai dengan data yang diinginkan
    lii = []
    for i in list(dfnol["kode_negara"]):
        for d in summdata:
            target = lii if d.get('Kode Negara 3 Huruf') == i else nl
            target.append(d)

    # membuat tabel
    dfnolt = pd.DataFrame(lii)
    with st.container():
        st.markdown(f"**Data Negara dengan jumlah produksi Nol Pada Tahun {x4}**")
        table1 = go.Figure(data=[go.Table(
            header=dict(values=list(dfnolt.columns),
                        fill_color='#e2d34e',
                        align='left',
                        height=50,
                        font=dict(color='black', size=21),
                        ),
            cells=dict(values=[dfnolt['Nama Negara'], dfnolt['Kode Negara 2 Huruf'], dfnolt['Kode Negara 2 Huruf'],
                               dfnolt['Kode Negara Angka'], dfnolt['Region'], dfnolt['Sub-Region']],
                       fill_color='#6853b9',
                       align='left',
                       height=90,
                       font=dict(color='white', size=20)))
        ])
        table1.update_layout(autosize=True, margin=dict(r=5, l=5, t=5, b=5))
        st.plotly_chart(table1, use_container_width=True)
    st.write("✨" * 55)
'''
By Amanda Febriani (12220025) | 12220025@mahasiswa.itb.ac.id
'''
