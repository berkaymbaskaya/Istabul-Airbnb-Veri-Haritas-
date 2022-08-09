import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import plotly.express as px
from streamlit_folium import folium_static
from PIL import Image
import shapely.geometry as shp

st.set_page_config(page_title="Berkay_CBS",page_icon=":smile:")
st.header("CBS PROJESİ")
st.markdown("Çalışmada İstanbul ili içerisindeki, Airbnb uygulamasında mevcut olan evlere dair ham veriler işlenmiş ve görselleştirilmiştir. Çalışmada evler ilçe bazlı olarak gruplandırılmıştır.  İlçelerdeki kiralık evlere ait nitelikler sol taraftaki araç çubuğundan filtrelerenerek harita üzerinden sorgulanabilir")


base="dark"
secondaryBackgroundColor="#3b9e79"

evler=pd.read_csv("https://raw.githubusercontent.com/berkaymbaskaya/streamlit/gh-pages/listings.csv")
ilceler=gpd.read_file("https://raw.githubusercontent.com/berkaymbaskaya/streamlit/gh-pages/neighbourhoods.geojson")

evler["geometry"]=evler[["longitude","latitude"]].apply(shp.Point,axis=1)
evler=gpd.GeoDataFrame(evler)
evler.set_crs(epsg=4326, inplace=True)

ortalamalar=evler.groupby(["neighbourhood"]).mean()
ilceler_ort=ilceler.merge(ortalamalar,on="neighbourhood")

evler["birim"]=1
ilcedeki_toplam_ev=evler.groupby(["neighbourhood"]).count()["birim"]

df_toplamev = pd.DataFrame(ilcedeki_toplam_ev)
e=df_toplamev["birim"]
ilceler=ilceler.merge(e,on="neighbourhood")
ilceler_ort=ilceler_ort.merge(e,on="neighbourhood")
ilceler["price"]=ilceler_ort["price"].round(2)

max=evler.groupby(["neighbourhood"]).max("price")
max.columns =max.columns.str.replace('price','max_price')


min=evler.groupby(["neighbourhood"]).min("price")
min.columns =min.columns.str.replace('price','min_price')

median=evler.groupby(["neighbourhood"]).median("price")
median.columns =median.columns.str.replace('price','median_price')
a=min["min_price"]
b=max["max_price"]
m=median["median_price"]
a_df=pd.DataFrame(a)
b_df=pd.DataFrame(b)
m_df=pd.DataFrame(m)
ilceler=ilceler.merge(a_df,on="neighbourhood")
ilceler=ilceler.merge(b_df,on="neighbourhood")
ilceler=ilceler.merge(m_df,on="neighbourhood")


#image=Image.open(urlopen("https://r.resimlink.com/zNOLkjyeAQ.jpg"))
#st.image(image,width=750)

sınıflandırma_dict={"Ortalama Fiyat":"price","İlçedeki toplam ev sayısı":"birim","En Yüksek Fiyat":"max_price","En Düşük Fiyat":"min_price","Ortanca Fiyat":"median_price"}

st.sidebar.header("HARİTA GÖSTERİM SEÇENEKLERİ:")
#image1=Image.open("https://r.resimlink.com/zNOLkjyeAQ.jpg")
#st.sidebar.image(image1, use_column_width=True)
sınıflandırma_secimi = st.sidebar.selectbox(label = "Harita hangi özelliğe göre renklendirilsin ?  Lütfen Seçiminizi yapın.", 
                                         options =( "Ortalama Fiyat","İlçedeki toplam ev sayısı","En Yüksek Fiyat","En Düşük Fiyat","Ortanca Fiyat"))

highlight_function = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.50, 
                                'weight': 0.1}
style_function = lambda x: {'fillColor': '#ffffff', 
                            'color':'#000000', 
                            'fillOpacity': 0.1, 
                            'weight': 0.1}
 


map=folium.Map(zoom_start=9,location=[41.2, 29],tiles="CartoDB Positron" )
m=folium.Choropleth(
    geo_data=ilceler,
    name='choropleth',
    data=ilceler,
    columns=["neighbourhood",sınıflandırma_dict[sınıflandırma_secimi]],
    key_on='feature.properties.neighbourhood',
    fill_color='PuRd',
    fill_opacity=0.7,
    line_opacity=1,

   
).add_to(map)
folium.LayerControl().add_to(map)

NIL = folium.features.GeoJson(
    ilceler, 
    style_function=style_function, 
    control=False,
    highlight_function=highlight_function, 
    tooltip=folium.features.GeoJsonTooltip(
        fields=['neighbourhood',sınıflandırma_dict[sınıflandırma_secimi]],
        aliases=['İlçe: ', sınıflandırma_secimi],
        style=('background-color: grey; color: white;'),
        
      
    )
)
m.add_child(NIL)


folium_static(map)
st.info("Bu aplikasyonda kullanılan istatistiksel ve coğrafi verilerin tamamı Airbnb web platformundan alınmıştır.")

st.markdown("## Evlerin İl Üzerindeki Dağılımı")
st.map(evler,zoom=8)








