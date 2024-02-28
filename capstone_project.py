import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import math
import datetime
from streamlit_option_menu import option_menu
from PIL import Image
# import matplotlib.pyplot as plt
# import seaborn as sns

img = Image.open('crime.jpg')
st.set_page_config(page_title ='Public Crime Dashboard',page_icon = img, layout ='wide')

###################################################################################################################################
# 1. Cleansing Dataset

cp_original = pd.read_csv('Crime_Data_from_2020_to_Present.csv')
cp = cp_original.drop(columns=['Part 1-2','Vict Descent','Crm Cd 1','Crm Cd 2','Crm Cd 3','Crm Cd 4','LOCATION','Cross Street','LAT','LON']) 
cp.columns = cp.columns.str.lower() # transform all column header to lower case
cp.rename(columns=lambda x: x.replace(' ','_'),inplace=True) # transform all space in column header replace with '_'
cp['time_occ'] = cp['time_occ'].apply(lambda x:str(x).zfill(4)) # transform time_occ value to string format new value with length 4 character
# st.write(cp['time_occ'].dtypes)
cp['date_rptd'] = pd.to_datetime(cp['date_rptd'])
cp['date_occ'] = pd.to_datetime(cp['date_occ']).astype(str) # change tipe to str so can be join with time_occ
cp['datetime_occ'] = cp['date_occ']+' '+cp['time_occ']
cp['datetime_occ'] = pd.to_datetime(cp['datetime_occ']) # change to datetime format

datetime_occ_pop = cp.pop('datetime_occ') # save old column in a variable
cp.insert(4,'datetime_occ',datetime_occ_pop)
cp = cp.drop(columns=['date_occ','time_occ'])

cp['year_occ'] = cp['datetime_occ'].dt.year
year_occ_pop = cp.pop('year_occ')
cp.insert(3,'year_occ',year_occ_pop)

cp['month_occ'] = cp['datetime_occ'].dt.month
# declare dictionary
months_dict = {
   '1':'Jan',
   '2':'Feb',
   '3':'Mar',
   '4':'Apr',
   '5':'May',
   '6':'Jun',
   '7':'Jul',
   '8':'Aug',
   '9':'Sept',
   '10':'Oct',
   '11':'Nov',
   '12':'Dec'
}
cp['month_occ'] = cp['month_occ'].apply(lambda x:months_dict[str(x)])
month_occ_pop = cp.pop('month_occ')
cp.insert(4,'month_occ',month_occ_pop)

cp['time_crime_occ'] = cp['datetime_occ'].dt.hour
time_crime_occ_pop = cp.pop('time_crime_occ')
cp.insert(5,'time_crime_occ',time_crime_occ_pop)
cp['mocodes'] = cp['mocodes'].fillna('Not confirm')

# update vict_sex record 
def updating_sex(value):
    if pd.isna(value) or value == 'H' or value == 'X' or value == '-':
        return 'Not confirm'
    elif value == 'F':
        return 'Female'
    else:
        return 'Male'
cp['vict_sex'] = cp['vict_sex'].apply(updating_sex)

def updating_weapon_used(weapon):
    if pd.isna(weapon):
        return 'Not confirm'
    else:
        return weapon
cp['weapon_desc'] = cp['weapon_desc'].apply(updating_weapon_used)
# above function block can be changed using code as below:
# cp['weapon_desc'] = cp['weapon_desc'].fillna('Not confirm')

cp['premis_desc'] = cp['premis_desc'].fillna('Not confirm')
# st.write(cp.isnull().sum())

def age_grouping(age):
    if age == 0:
        return 'Not confirm'
    elif age<=-1 or 1 <= age <= 2:
        return 'Baby'
    elif 3 <= age <= 16:
        return 'Children'
    elif 17 <= age <= 30:
        return 'Young Adults'
    elif 31 <= age <= 45:
        return 'Middle-age Adults'
    else:
        return 'Old Adults'
cp['vict_age_class'] = cp['vict_age'].apply(age_grouping)
vict_age_class_pop = cp.pop('vict_age_class')
cp.insert(13,'vict_age_class',vict_age_class_pop)

# st.write(cp.head())
# Tahap pembuatan filter dan grouping

#exclude 2024 untuk perhitungan %kenaikan/penurunan jumlah tindak kejahatan          
latest_year_compare = cp[cp['month_occ']=='Dec']
latest_year = max(latest_year_compare['year_occ'])
# st.write(latest_year_compare)
# st.write(latest_year)
latest_year_before = latest_year-1
# st.write(latest_year_before)

data = cp[cp['year_occ']!=2024].groupby(['year_occ','vict_sex']).agg({'crm_cd_desc':'count'}).reset_index()
male_data = data[data['vict_sex'] == 'Male'].rename(columns={'crm_cd_desc': 'male_count'})
female_data = data[data['vict_sex'] == 'Female'].rename(columns={'crm_cd_desc': 'female_count'})
not_confirm_data = data[data['vict_sex'] == 'Not confirm'].rename(columns={'crm_cd_desc': 'not_confirm_count'})
merged_data = male_data.merge(female_data, on=['year_occ'], how='outer').merge(not_confirm_data, on=['year_occ'], how='outer').reset_index()

# 2. Mocode table

mc = pd.read_csv('Mocodes.csv')

mc['code'] = mc['code'].apply(lambda x: str(x).zfill(4))
mc.reset_index(inplace=True, names='no')

###################################################################################################################################

# Menampilan menu dari halaman web
selected = option_menu(
    menu_title = None, 
    options = ['Home', 'Table Description',  'Reference', 'Contact Info'], 
    icons=['house', 'table', "book", 'info-circle'], 
    # menu_icon='cast', 
    default_index=0, 
    orientation="horizontal",
    styles={
        "container": {"background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "20px"}, 
        "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "lightblue"},
    }
)

if selected == 'Home':
    st.markdown(
    """
    <style>
    .title {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

    # Menampilkan judul dengan kelas CSS 'title'
    st.markdown("<h1 class='title'>Angka Kriminalitas di Kota Los Angeles</h1>", unsafe_allow_html=True)    
    st.write(
        '<div style="text-align:justify;">'
        'Seiring dengan berjalannya waktu, setiap negara memiliki permasalahan yang beraneka ragam. Baik itu masalah pendidikan, transportasi, kesehatan, tindak kejahatan dan lain sebagainya. Hal ini dapat terjadi misalnya di daerah perkotaan ataupun non perkotaan. Pada kesempatan kali ini, saya mencoba untuk mengambil satu dataset yang menggambarkan catatan kriminalitas yang terjadi dalam kurun waktu mulai dari tahun 2020 sampai dengan 2024.' 
        '</div>',unsafe_allow_html=True    
    )
    st.write('\n\n')
    st.write(
        '<div style="text-align:justify;">' 
        'Secara umum dataset yang digunakan akan memberikan gambaran catatan kriminalitas yang terjadi di kota Los Angeles dalam berbagai parameter baik itu lokasi (area) kejadian, waktu kejadian, siapa saja yang menjadi korban dan umurnya, status dari kasus, modus operandi dan beberapa informasi lainnya. Ketidakakuratan atau ketidaksesuaian catatan yang menampung <b>record case by case</b> akan sangat mungkin untuk terjadi. Hal ini dikarenakan data ini merupakan transkripsi dari laporan asli yang dicatat pada kertas. Sehingga perlu untuk dirapikan agar dapat digunakan.'
        '</div>',unsafe_allow_html=True     
    )
    st.write('\n\n')    
    st.write(
        '<div style="text-align:justify;">'
        'Secara prosentase angka kriminalitas pada tahun 2023 (sebagai acuan tahun terakhir) dibandingkan dengan tahun 2022 mengalami penurunan sebesar 2.06 %, walau tidak secara signifikan.'
        '</div>',unsafe_allow_html=True    
    )
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)

    col_1,col_2,col_3,col_4 = st.columns(4)
    with col_1:
        curr_crime = np.sum(data.loc[data['year_occ']==latest_year,'crm_cd_desc'].values[:])
        prev_crime = np.sum(data.loc[data['year_occ']==latest_year_before,'crm_cd_desc'].values[:])
        number_diff_pct = 100*(curr_crime-prev_crime)/prev_crime
        st.metric('Number of Crime',value = curr_crime,delta=f'{number_diff_pct:.2f}%')

    with col_2:
        curr_female = merged_data.loc[merged_data['year_occ']==latest_year,'female_count'].values[0]
        prev_female = merged_data.loc[merged_data['year_occ']==latest_year_before,'female_count'].values[0]
        female_diff_pct = 100*(curr_female-prev_female)/prev_female
        st.metric('Number of Female Victims',value = curr_female,delta=f'{female_diff_pct:.2f}%')
        curr_female

    with col_3:
        curr_male = merged_data.loc[merged_data['year_occ']==latest_year,'male_count'].values[0]
        prev_male = merged_data.loc[merged_data['year_occ']==latest_year_before,'male_count'].values[0]
        male_diff_pct = 100*(curr_male-prev_male)/prev_male
        st.metric('Number of Male Victims',value = curr_male,delta=f'{male_diff_pct:.2f}%')

    with col_4:
        curr_not_confirm = merged_data.loc[merged_data['year_occ']==latest_year,'not_confirm_count'].values[0]
        prev_not_confirm = merged_data.loc[merged_data['year_occ']==latest_year_before,'not_confirm_count'].values[0]
        not_confirm_diff_pct = 100*(curr_not_confirm-prev_not_confirm)/prev_not_confirm
        st.metric('Number of Not Confirm Victims',value = curr_not_confirm,delta=f'{not_confirm_diff_pct:.2f}%')
    
    st.write('\n\n')

    st.subheader(
        'Bagaimana Trend Angka Kriminalitas Dari Tahun ke Tahun?\n\n'
        )

    col_1,col_2,col_3 = st.columns(3)

    with col_1:
        st.write(
            '<div style="text-align:justify;">'
            'Berdasarkan trend line pada figure memperlihatkan bahwa angka kriminalitas mengalami kenaikan dari tahun 2020 sampai 2022. Dikutip dari <a href="https://mayor.lacity.gov/news/lapd-releases-end-year-crime-statistics-city-los-angeles-2023">lacity.gov</a> menjelaskan bahwa pihak kepolisian fokus untuk mencegah dan mengurangi kriminalitas yang sudah meresahkan. Dan ini memberikan dampak yang positif.'
            '</div>', unsafe_allow_html=True
        )   
        st.write('\n\n')
        col_a,col_b = st.columns(2)
        with col_a:
            container = st.container(border = False)
            with container:
                freq = st.selectbox('Pilih frekuensi Crime Number line chart :',['Yearly','Monthly'])

        st.write(
            '<div style="text-align:justify;">'
            'Dari informasi yang disajikan pada bar chart, diketahui berdasar gender, wanita bukanlah sebagai target tertinggi dari para pelaku kejahatan (kriminal).'
            '</div>',unsafe_allow_html=True
        )

    with col_2:
        data_all = cp.groupby(['year_occ','month_occ']).size().reset_index(name='crime_count')
        month_to_num = {'Jan': '1', 
                        'Feb': '2',     
                        'Mar': '3', 
                        'Apr': '4',
                        'May': '5', 
                        'Jun': '6',
                        'Jul': '7', 
                        'Aug': '8', 
                        'Sept': '9', 
                        'Oct': '10', 
                        'Nov': '11', 
                        'Dec': '12'
        }
        data_all['month_occ_num'] = data_all['month_occ'].apply(lambda x:month_to_num[x])
        data_all['year_month'] = pd.to_datetime(data_all['year_occ'].astype(str)+'-'+data_all['month_occ_num'],format='%Y-%m').dt.strftime('%Y-%m')
        # st.write(data_all)
        total_months = len(data_all['year_month'])
        step = 3

        max_y_value = data_all.groupby('year_occ')['crime_count'].sum().max()
        max_y_axis = max_y_value + 50000
        if freq == 'Monthly':
            line_chart = alt.Chart(data_all).mark_line(point=True,color='lightblue').encode(
                x = alt.X('year_month:O', title='Occurance Periode',axis=alt.Axis(tickCount=step, labelAngle=0)),
                y = alt.Y('crime_count:Q', title='Crimes Number', axis=alt.Axis(format='d'))
            ).properties(title='Crime Number in Monthly',height=350)
        else:
            line_chart = alt.Chart(data_all.groupby('year_occ')['crime_count'].sum().reset_index()).mark_line(point=True,color='lightblue').encode(
                x = alt.X('year_occ:O', title='Occurance Periode',axis=alt.Axis(labelAngle=0)),
                y = alt.Y('crime_count:Q', title='Crimes Number', axis=alt.Axis(format='d'),scale=alt.Scale(domain=(0,max_y_axis)))
            ).properties(title='Crime Number in Yearly',height=350)

        line_chart = line_chart.configure_title(fontSize=16, anchor='middle')
        line_chart = line_chart.interactive()
        st.altair_chart(line_chart, use_container_width=True)     

    with col_3:
        victim_gender = cp[cp['year_occ']!=2024].groupby(['year_occ','vict_sex']).size().reset_index(name='crime_count')
        # st.write(victim_gender)
        bar_chart = alt.Chart(victim_gender).mark_bar().encode(
            # column="category:N",
            x=alt.X('year_occ:O',axis=alt.Axis(labelAngle=0),title='Year'),
            xOffset='vict_sex:N',
            y=alt.Y('crime_count:Q',title='Crimes Number'),
            color=alt.Color('vict_sex:N',scale=alt.Scale(scheme='category20b'),legend=alt.Legend(title='Victims by Gender', orient='right',titleFontSize=12,labelFontSize=12))
        ).properties(title='Comparison Victims by Gender',height=350).configure_title(fontSize=16,anchor='middle')
        st.altair_chart(bar_chart, use_container_width=True)

    st.subheader(
        'Pengelompokkan Korban Berdasarkan Kategori Usia'
    )

    st.write(
        'Pada kondisi ini kita coba melihat lebih detil kategori korban tindak kriminal berdasarkan usianya. Dalam hal ini korban dikelompokkan menjadi 5 kelas (group) usia. Untuk usia sampai dengan 2 tahun ~ Baby, usia 3-16 ~ Children, usia 17-30 ~ Young Adults, usia 31-45 ~ Middle-age Adults, dan usia di atas 45  ~ Old Adults. Sebagai kelas (group) tambahan adalah "Not confirm" untuk korban yang tidak memiliki informasi valid terkait usia.'
    )

    col_1,col_2,col_3,col_4,col_5 = st.columns(5)
    with col_1:
        year_option = (latest_year_compare['year_occ'].unique()).tolist()
        year_option.sort(reverse=True)
        year_option.insert(0,'All Year')
        year_select = st.selectbox('Pilih tahun :',year_option)

    if year_select != 'All Year':
        age_class = cp[cp['year_occ']==year_select].groupby(['year_occ','vict_age_class']).size().reset_index(name='total_age_class')
        col_1,col_2,col_3 = st.columns(3)
        with col_1:
            bar_chart = alt.Chart(age_class).mark_bar().encode(
                x=alt.X('year_occ:O',axis=alt.Axis(labelAngle=0),title='Year'),  
                xOffset='vict_age_class:N',          
                y=alt.Y('total_age_class:Q' ,title='Victims Number by Age Class'),
                color=alt.Color('vict_age_class:N',scale=alt.Scale(scheme='category20b'),title='Victims by Age Class')
            ).properties(title='Victims Number of Crime by Age Class',width=300,height=350).configure_title(fontSize=16,anchor='middle')
            st.altair_chart(bar_chart,use_container_width=True)
    else:
        col_1,col_2 = st.columns([4,3])
        with col_1:
            age_class = cp[cp['year_occ']!=2024].groupby(['year_occ','vict_age_class']).size().reset_index(name='total_age_class')
            bar_chart = alt.Chart(age_class).mark_bar().encode(
                x=alt.X('year_occ:O',axis=alt.Axis(labelAngle=0),title='Year'),  
                xOffset='vict_age_class:N',
                y=alt.Y('total_age_class:Q',title='Victims Number by Age Class'),
                color=alt.Color('vict_age_class:N',scale=alt.Scale(scheme='category20b'),title='Victims by Age Class')
            ).properties(title='Victims Number of Crime by Age Class',width=300,height=350).configure_title(fontSize=16,anchor='middle')
            st.altair_chart(bar_chart,use_container_width=True)


    st.subheader(
        'Pengelompokkan Berdasarkan Area dan Status'
    )

    col_1,col_2,col_3 = st.columns(3)

    with col_1:
        year_option_area=year_option.copy()
        # year_select_area=year_option_area.remove('All Year')
        year_option_area.remove('All Year')

        list_area=cp['area_name'].unique().tolist()
        list_area.sort()
        list_area.insert(0,'All Areas')

        st.write(
            '<div style="text-align:justify;">'
            'Selanjutnya kita dapat melihat dan mengelompokkan berdasarkan area. Sehingga kita dapat mengetahui area mana saja yang memiliki angka kriminalitas tertinggi setiap tahunnya maupun secara keseluruhan. Hal ini tentunya dapat digunakan oleh pihak terkait sebagai masukan untuk area yang diberikan atensi khusus atau lebih. '
            '</div>', unsafe_allow_html=True
        )   
        st.write('\n\n')
        col_a,col_b = st.columns(2)
        with col_a:
            container = st.container(border = False)
            with container:
                year_select_area = st.selectbox('Pilih tahun :',year_option_area)
            with container:
                areas = st.multiselect(
                    'Pilih area :',list_area,default=['All Areas']
                )    
    with col_2:
        area = cp[cp['year_occ']==year_select_area].groupby(['area_name']).size().reset_index(name='crime_count')
        bar_chart = alt.Chart(area).mark_bar().encode(
            x=alt.X('crime_count:Q',title='Crimes Number'),
            # yOffset='area_name:N',
            y=alt.Y('area_name:N',title='Area-Name',sort='-x'),
            color=alt.Color('area_name:N',scale=alt.Scale(scheme='category20b'),title='Crimes Number by Area')
        ).properties(title='Crimes Number Recorded by Area',height=350).configure_title(fontSize=16,anchor='middle').configure_legend(columns=2)
        st.altair_chart(bar_chart, use_container_width=True)
    with col_3:
        if len(areas)>0:
            pass

        status_year=cp[cp['year_occ']==year_select_area]

        if 'All Areas' in areas:
            status_year = status_year.groupby('status_desc').size().reset_index(name='status_count')
            # status_year
            bar_chart = alt.Chart(status_year).mark_bar().encode(
                x=alt.X('status_desc:N',axis=alt.Axis(labelAngle=0),title='Status Category'),
                # xOffset='status_desc:N',
                y=alt.Y('status_count:Q',sort='-y',title='Status Number'),
                color=alt.Color('status_desc:N',scale=alt.Scale(scheme='category20b'),title='Status of Reported Crimes'),
            ).properties(title=(f'Reported Crimes Status - {areas[0]}'),height=350).configure_title(fontSize=16,anchor='middle')
            st.altair_chart(bar_chart,use_container_width=True)
        else:
            area_names = ', '.join(areas)
            status_year=status_year[status_year['area_name'].isin(areas)]
            # status_year
            # st.write(status_year.shape)   # untuk checking apakaha filtersasi dengan code vs manual jumlah barisnya sama
            status_year = status_year.groupby('status_desc').size().reset_index(name='status_count')
            # status_year
            bar_chart = alt.Chart(status_year).mark_bar().encode(
                    x=alt.X('status_desc:N',axis=alt.Axis(labelAngle=0),title='Status Category'),
                    # xOffset='status_desc:N',
                    y=alt.Y('status_count:Q',sort='-y',title='Status Number'),
                    color=alt.Color('status_desc:N',scale=alt.Scale(scheme='category20b'),title='Status of Reported Crimes'),
            ).properties(title=(f'Reported Crimes Status - {area_names}'),height=350).configure_title(fontSize=16,anchor='middle')
            st.altair_chart(bar_chart,use_container_width=True)
    
    st.subheader(
        'Ragam Modus Operandi Pelaku Kejahatan (Kriminal)'
    )

    st.write(
        '<div style="text-align:justify;">'
        'Modus operandi atau yang disebut dengan <b>MO</b> memiliki pengertian sebagai dikutip di bawah ini:'
        '</div>', unsafe_allow_html=True
    )
    st.markdown(
        '''
        * [_cambridge dictionary_](https://dictionary.cambridge.org/us/dictionary/english/), a particular way of doing something
        * [_wikipedia en_](https://en.wikipedia.org/wiki/), someone's habits of working, particularly in the context of business or criminal investigations, but also more generally.
        * [_wikipedia id_](https://id.wikipedia.org/wiki/), cara operasi orang perorang atau kelompok penjahat dalam menjalankan rencana kejahatannya.
        '''
    )
    st.write(
        '<div style="text-align:justify;">'
        'Dari sekian banyak modus yang digunakan para pelaku akan terlihat rumit, misal dalam satu kasus ada beberapa MO yang digunakan. Untuk menyederhanakan pelaporan secara tabular maka penulisan MO ini akan jauh lebih praktis dalam penggunaan <i>code</i> yang mewakili setiap MO (biasa disebut sebagai mocode).'
        '</div>', unsafe_allow_html=True
    )    
    st.write('\n\n')
    st.write(
        '<div style="text-align:justify;">'
        'Dalam pemaparan ini, mocode yang digunakan merupakan tabel terpisah yang dapat diunduh dari <a href="https://data.lacity.org/Public-Safety/Crime-Data-from-2020-to-Present/2nrs-mtv8/about_data">lacity.org</a>. Tabel mocode inilah nanti yang akan digunakakn untuk mapping mocode dari dataset yang disediakan dalam visualisasi grafik.'
        '</div>', unsafe_allow_html=True
    )

    year_option_mo = (latest_year_compare['year_occ'].unique()).tolist()
    year_option_mo.sort(reverse=True)
    # st.write(year_option_mo)

    list_area_mo=cp['area_name'].unique().tolist()
    list_area_mo.sort()
    list_area_mo.insert(0,'All Areas')
    
    col_1,col_2,col_3,col_4,col_5 = st.columns(5)

    with col_1:
        container_mo = st.container(border = False)
        with container_mo:
            year_select_mo = st.selectbox('Pilih tahun :',year_option_mo,key='year_select_mo')
        with container_mo:
            areas = st.multiselect(
                'Pilih area :',list_area_mo,default=['All Areas'],key='areas_select_mo'
            )   
    
    mocodes_dict = mc.set_index('code')['description'].to_dict() # Mengonversi mc menjadi kamus untuk pencarian yang lebih efisien

    description_list = [] # Inisialisasi list untuk menyimpan deskripsi

    # # Loop melalui setiap nilai dalam kolom 'Mocodes' di cp
    mo_cp = cp[cp['year_occ']==year_select_mo]
    for mocode in mo_cp['mocodes']:
        description = ''
        if pd.notna(mocode):  # Memeriksa apakah nilai tidak kosong
            for kode in mocode.split():  # Membagi string menjadi token
                kode = str(kode).zfill(4)  # Menambahkan 0 di depan kode jika panjang kode < 4
                if kode in mocodes_dict:  # Memeriksa apakah kode ada di kamus
                    description += mocodes_dict[kode] + ', '  # Menambahkan deskripsi ke string description
        if description == '':  # Jika deskripsi kosong
            description = 'Not Confirm'  # Ganti dengan 'Not Confirm'
        description_list.append(description.strip(', '))  # Menambahkan deskripsi ke list, menghapus koma terakhir

    mo_cp['mocodes_description'] = description_list # Menambahkan list deskripsi ke DataFrame cp
    # Menampilkan lima baris pertama dari kolom baru
    # st.write(mo_cp.head())

    col_1,col_2 = st.columns([4,3])

    with col_1:
        if 'All Areas' in areas:
            split_mocodes = mo_cp['mocodes_description'].str.split(', ')
            all_mocodes = []
            for sublist in split_mocodes:
                for mocodex in sublist:  # Loop melalui setiap elemen dalam sublist
                    all_mocodes.append(mocodex.strip()) # Menghapus spasi tambahan di awal atau akhir deskripsi
            mocodes_counts = pd.Series(all_mocodes).value_counts()
            mo_year = pd.DataFrame({'mocodes_descriptions': mocodes_counts.index, 'mo_count': mocodes_counts.values})
            mo_year=mo_year.nlargest(20,'mo_count')
            # st.write(mo_year)
            bar_chart = alt.Chart(mo_year).mark_bar().encode(
                x=alt.X('mo_count:Q',title='Modus Operandi Number'),
                y=alt.Y('mocodes_descriptions:N',title='Modus Operandi Name',sort='-x'),
                color=alt.Color('mocodes_descriptions:N',scale=alt.Scale(scheme='category20b'),title='MO Descriptions')
            ).properties(title=(f'All Crimes Modus Operandi - {areas[0]}'),height=350).configure_title(fontSize=16,anchor='middle').configure_legend(columns=2)
            st.altair_chart(bar_chart, use_container_width=True)
        else:
            area_names = ', '.join(areas)
            mo_cp = mo_cp[mo_cp['area_name'].isin(areas)]
            split_mocodes = mo_cp['mocodes_description'].str.split(', ')
            all_mocodes = []
            for sublist in split_mocodes:
                for mocodex in sublist:  # Loop melalui setiap elemen dalam sublist
                    all_mocodes.append(mocodex.strip()) # Menghapus spasi tambahan di awal atau akhir deskripsi
            mocodes_counts = pd.Series(all_mocodes).value_counts()
            mo_year = pd.DataFrame({'mocodes_descriptions': mocodes_counts.index, 'mo_count': mocodes_counts.values})
            mo_year=mo_year.nlargest(20,'mo_count')
            # st.write(mo_year)
            bar_chart = alt.Chart(mo_year).mark_bar().encode(
                x=alt.X('mo_count:Q',title='Modus Operandi Number'),
                y=alt.Y('mocodes_descriptions:N',title='Modus Operandi Name',sort='-x'),
                color=alt.Color('mocodes_descriptions:N',scale=alt.Scale(scheme='category20b'),title='MO Descriptions')
            ).properties(title=(f'All Crimes Modus Operandi - {area_names}'),height=350).configure_title(fontSize=16,anchor='middle').configure_legend(columns=2)
            st.altair_chart(bar_chart, use_container_width=True)


    st.subheader(
        'Kesimpulan dari Visualisasi'
    )

    st.write(
        '<div style="text-align:justify;">'
        'Pengolahan data mentah (raw data) menjadi sebuah visual bertujuan memudahkan pembaca untuk mengerti dan memahami data yang kompleks menjadi terlihat sederhana. Berdasar pada data yang sudah diolah pada kasus ini, dapat ditarik beberapa kesimpulan:'
        '</div>', unsafe_allow_html=True
    )

    st.write('\n\n')

    st.markdown(
        '''
        1. Dari trend yang disajikan, baik secara tahunan maupun bulanan terlihat bahwa jumlah kriminalitas pada tahun 2023 mulai menurun dibandingkan pada tahun 2022 sebesar 2.06%. Dan jika diperhatikan lebih detil, trend ini mulai terlihat dari awal 2023. Pada tahun 2024 dalam 1 bulan berjalan juga terlihat jumlahnya juga turun.
        2. Berdasar trend gender korban, wanita bukan sebagai korban dengan angka tertinggi dan ini terlihat sama dari trend tahunan. Memang masih terdapat data tidak valid yang masih dikategorikan sebagai *Not confirm*.
        3. Area yang memiliki angka kriminalitas tertinggi adalah *Central*. Ini dapat dijadikan masukkan bagi pihak Kepolisian setempat untuk menjadi fokus area yang ditangani.
        4. Berdasar pada data, kita dapat menggunakan *Status kasus yang ditangani* sebagai salah satu indikator untuk melihat kinerja. Asumsi umum tentunya semakin sedikit kasus yang belum tuntas maka semakin baik kinerja. Namun perlu digarisbawahi bahwa penanganan kasus tentunya memiliki parameter lain dan mungkin kompleks sehingga membutuhkan waktu lebih lama. Dalam hal ini, dari data diketahui bahwa kasus yang belum selesai (*Invest Cont*) masih sangat tinggi. Hal ini dapat dijadikan masukkan untuk memperbaiki kinerja departemen tertentu.
        Juga dapat dilihat bahwa angka penahanan pada remaja (*Juv Arrest*) pada angka  yang rendah. Tentunya ini hal yang baik dan sebagai salah satu parameter yang perlu diperhatikan. Misalnya pentingnya kerjasama Kepolisian dan Sekolah dalam memberi edukasi untuk menekan angka kriminalitas anak usia remaja.
        5. Mengetahui MO yang digunakan pelaku kriminal dengan angka tertinggi yaitu *Removes vict property* dan *Vandalized*. Ini juga tentunya dapat digunakan menjadi masukkan bagi departemen terkait misalnya untuk memberikan atensi lebih untuk pencegahan tidak kejahatan tertentu seperti pencurian. Dapat juga untuk melihat anomali/modus operansi baru di dalam melakukan tindak kejahatan. 
        '''
        )
    

if selected == 'Table Description':

    st.markdown("<h1 class='title'>Informasi Terkait Tabel</h1>", unsafe_allow_html=True)

    st.write('\n\n')

    st.markdown(
        '''
        * __Dataset Original__ - raw data atau data mentah yang diperoleh dari sumber dan belum mengalami transformasi.
        '''
    )
    st.write(cp_original.head())

    st.markdown(
        '''
        * __Dataset Original - info__ - memberikan informasi jumlah non-null record dan tipe dari setiap kolom.
        '''
    )

    data = {
        'Column': ['DR_NO', 'Date Rptd', 'DATE OCC', 'TIME OCC', 'AREA', 'AREA NAME', 'Rpt Dist No', 'Part 1-2', 'Crm Cd', 
                'Crm Cd Desc', 'Mocodes', 'Vict Age', 'Vict Sex', 'Vict Descent', 'Premis Cd', 'Premis Desc', 'Weapon Used Cd', 'Weapon  Desc', 'Status', 'Status Desc', 'Crm Cd 1', 'Crm Cd 2', 'Crm Cd 3', 'Crm Cd 4', 'LOCATION', 'Cross Street', 'LAT', 'LON'],
        'Non-Null Count': [891182, 891182, 891182, 891182, 891182, 891182, 891182, 891182, 891182, 891182, 767161, 891182, 773314, 
                        773306,891172, 890637, 308836, 308836, 891182, 891182, 891171, 64938, 2198, 63, 891182, 140713, 891182, 891182],
        'Dtype': ['int64', 'object', 'object', 'int64', 'int64', 'object', 'int64', 'int64', 'int64', 'object', 'object', 'int64', 
                'object', 'object', 'float64', 'object', 'float64', 'object', 'object',
                'object', 'float64', 'float64', 'float64', 'float64', 'object', 'object', 'float64', 'float64']
    }

    doriginal_info = pd.DataFrame(data)
    st.dataframe(doriginal_info.T)

    st.markdown(
        f'''
        * __Dataset Original - shape__ - memberikan informasi jumlah baris dan kolom : {cp_original.shape[0]} *baris* dan {cp_original.shape[1]} *kolom*.
        '''
    )   

    st.markdown(
        '''
        Berikut deskripsi untuk setiap kolom pada tabel:
        '''
    )

    data = {
    'Column Name': ['DR_NO', 'Date Rptd', 'DATE OCC', 'TIME OCC', 'AREA', 'AREA NAME', 'Rpt Dist No', 'Part 1-2', 'Crm Cd', 
                'Crm Cd Desc',  'Mocodes', 'Vict Age', 'Vict Sex', 'Vict Descent', 'Premis Cd', 'Premis Desc', 'Weapon Used Cd', 'Weapon Desc', 'Status', 'Status Desc', 'Crm Cd 1', 'Crm Cd 2', 'Crm Cd 3', 'Crm Cd 4', 'LOCATION', 'Cross Street', 'LAT', 'LON'],
    'Description': ['Division of Records Number: Official file number made up of a 2 digit year, area ID, and 5 digits', 'MM/DD/YYYY', 
                'MM/DD/YYYY', 'In 24 hour military time.', 'The LAPD has 21 Community Police Stations referred to as Geographic Areas within the department.', 'The 21 Geographic Areas or Patrol Divisions are also given a name designation that references a landmark or the surrounding community that it is responsible for.', 'A four-digit code that represents a sub-area within a Geographic Area.', 'Number', 'Indicates the crime committed. (Same as Crime Code 1)', 'Defines the Crime Code provided.', 'Modus Operandi: Activities associated with the suspect in commission of the crime.', 'Two character numeric', 'F - Female M - Male X - Unknown', 'Descent Code: A - Other Asian B - Black C - Chinese D - Cambodian F - Filipino G - Guamanian H - Hispanic/Latin/Mexican I - American Indian/Alaskan Native J - Japanese K - Korean L - Laotian O - Other P - Pacific Islander S - Samoan U - Hawaiian V - Vietnamese W - White X - Unknown Z - Asian Indian', 'The type of structure, vehicle, or location where the crime took place.', 'Defines the Premise Code provided.', 'The type of weapon used in the crime.', 'Defines the Weapon Used Code provided.', 'Status of the case. (IC is the default)', 'Defines the Status Code provided.', 'Indicates the crime committed. Crime Code 1 is the primary and most serious one. Crime Code 2, 3, and 4 are respectively less serious offenses. Lower crime class numbers are more serious.', 'May contain a code for an additional crime, less serious than Crime Code 1.',  'May contain a code for an additional crime, less serious than Crime Code 1.', 'May contain a code for an additional crime, less serious than Crime Code 1.', 'Street address of crime incident rounded to the nearest hundred block to maintain anonymity.', 'Cross Street of rounded Address', 'Latitude', 'Longitude']
    }

    tdescription = pd.DataFrame(data)
    st.write(tdescription)

    st.markdown(
        '''
        * __Dataset After__ - setelah dilakukan cleansing yaitu mengidentifikasi, koreksi, dan membuang data yang tidak diperlukan. Dalam hal ini ada beberapa kolom yang dibuang, penggabungan kolom (tahun, bulan, tanggal, jam), menambahkan kolom.
        '''
    )
    st.write(cp.head())

    st.markdown(
        '''
        * __Dataset After - info__ - memberikan informasi jumlah non-null record dan tipe dari setiap kolom.
        '''
    )
    data = {
        'Column': ['dr_no', 'date_rptd', 'datetime_occ', 'year_occ', 'month_occ', 'time_crime_occ', 'area', 'area_name', 
                'rpt_dist_no',     'crm_cd', 'crm_cd_desc', 'mocodes', 'vict_age', 'vict_age_class', 'vict_sex', 'premis_cd', 'premis_desc', 'weapon_used_cd', 'weapon_desc', 'status', 'status_desc'],
        'Non-Null Count': [891182, 891182, 891182, 891182, 891182, 891182, 891182, 891182, 891182, 891182, 891182, 891182, 891182, 
                        891182, 891182, 891172, 891182, 308836, 891182, 891182, 891182],
        'Dtype': ['int64', 'datetime64[ns]', 'datetime64[ns]', 'int32', 'object', 'int32', 'int64', 'object', 'int64', 'int64', 
                'object', 'object', 'int64', 'object', 'object', 'float64', 'object', 'float64', 
                'object', 'object', 'object']
    }
    
    dafter_info = pd.DataFrame(data)
    st.dataframe(dafter_info.T)

    st.markdown(
        f'''
        * __Dataset After - shape__ - memberikan informasi jumlah baris dan kolom : {cp.shape[0]} *baris* dan {cp.shape[1]} *kolom*.
        '''
    )  

    st.markdown(
        '''
        * __Modus Operandi Codes (mocodes) Original__ - deskripsi kode MO.
        '''
    )
    
    mc = pd.read_csv('Mocodes.csv')
    st.write(mc)

    st.markdown(
        '''
        * __Modus Operandi Codes (mocodes) After__ - standarisasi kode MO menjadi 4 angka. Tabel ini nantinya akan digunakan sebagai source -  lookup table ke Dataset After yang digunakan untuk visualisasi.
        '''
    )
    mc['code'] = mc['code'].apply(lambda x: str(x).zfill(4))
    mc.reset_index(inplace=True, names='no')
    st.write(mc)

if selected == 'Reference':

    st.markdown("<h1 class='title'>Referensi</h1>", unsafe_allow_html=True)
    
    st.markdown(
        '''
        [1] https://catalog.data.gov/dataset/, "Crime Data from 2020 to Present"\n
        [2] https://data.lacity.org/Public-Safety/, "Crime-Data-from-2020-to-Present"\n
        [3] https://mayor.lacity.gov/news/, "LAPD RELEASES END OF YEAR CRIME STATISTICS FOR THE CITY OF LOS ANGELES 2023"\n
        [4] https://dictionary.cambridge.org/us/dictionary/english/, "Modus Operandi"\n
        [5] https://en.wikipedia.org/wiki/, "Modus Operandi"\n
        [6] https://id.wikipedia.org/wiki/, "Modus Operandi"
        '''
    )

if selected == 'Contact Info':

    _,mid_col,_ = st.columns([1,4,1])
    with mid_col:
        st.write(
            '<div style="text-align:justify;">'
            """Dear Sahabat, perkenalkan saya David. Terimakasih sudah meluangkan waktu untuk berkunjung pada halaman ini. Ini merupakan project yang ditujukan sebagai syarat untuk menyelesaikan tugas Capstone Project - TETRIS Program Batch 4 dan sertifikasi. Ini merupakan langkah awal saya untuk terjun ke dunia industri di bidang Data Analytics. Masukan dan sharing yang membangun adalah hal yang saya harapkan.\n
            ~ fokus akan memberi hasil ~"""
            ,unsafe_allow_html=True
        )
        st.markdown(
            '''
            * [email]    : david.mendrofa@gmail.com
            * [linkedin] : linkedin.com/in/david-oktavianus-mendrofa-65605124
            * [github]   : github.com/davidmendrofa
            * [mobile]   : +6287776475937
            '''
        )
            
            
         
            





        
    
