#################
# libraries
#################
import pandas as pd
import numpy as np
import requests
import streamlit as st
from streamlit_lottie import st_lottie
from PIL import Image
pd.set_option("display.expand_frame_repr",False)

#################
# data load
#################
df = pd.read_csv("df.csv")


def artist_data_prep(limiter_start=50, dataframe=df, limiting_variable="popularity", step=10):
    """
    verilen dataframe içinde


    dataframe: inceleme yapılacak dataframe nesnesi

    limiting_variable: veri setini kırmak iççin kullanılacak değişkenin adı

    limiter_start: limiting_variable ile belirtilen değişkenin hangi değerinden sonrası ile ilgileneceğimiz

    step: oluşturulacak sınıfların kaçar birim aralıklarla oluşturulacagı

    count: kaç adet öneri istenildigi

    sort_asc_var: büyükten küçüğe sıralanacak değişken adı

    sort_desc_var: küçükten buyuge sıralanacak değişken adı

    """
    from sklearn.neighbors import LocalOutlierFactor
    lof = LocalOutlierFactor()

    temp_df = dataframe[dataframe[limiting_variable] > limiter_start]
    for x in range(int(limiter_start), max(temp_df[limiting_variable]), int(step)):
        temp_df.loc[(temp_df[limiting_variable] > x) & (temp_df[limiting_variable] <= x + step), "CLASSES"] = str(
            x) + "_" + str(x + step) + "_" + "class"
    temp_df["lof_results"] = lof.fit_predict(temp_df[[limiting_variable]])
    temp_df.drop(["Unnamed: 0", "genres"], axis=1, inplace=True)

    return temp_df


artist_data_prep().to_csv(path_or_buf="df_lof.csv", header=True, index=False)

#################
# artist recommendation
#################

#################
# functions
#################

df = pd.read_csv("df_lof.csv")


def artist_recomm(dataframe, count, sort_asc_var="popularity", sort_desc_var="followers"):
    return dataframe[dataframe["lof_results"] == -1].sort_values(by=[sort_asc_var, sort_desc_var],
                                                                 ascending=[False, True])[
        ["name", "followers", "popularity"]]. \
        groupby(by="popularity").first().head(count)


def outlier(dataframe, count, ratio=0.2):
    cols = dataframe["CLASSES"].unique()
    for col in cols[1:]:
        q1 = dataframe[dataframe["CLASSES"] == col]["followers"].quantile(q=0.35)
        q3 = dataframe[dataframe["CLASSES"] == col]["followers"].quantile(q=0.75)

        iqr = q3 - q1

        low = q1 - ratio*iqr

        return dataframe[dataframe["followers"] < low].\
            sort_values(by=["popularity", "followers"], ascending=[False, True]).\
            groupby("popularity").first().sort_values(by="popularity",ascending=False)[["name","followers"]].head(count)




outlier(df,10)

#################
# page setup
#################
st.set_page_config(page_title="spotiuul.com", page_icon="🥑", layout="wide")


#################
# image url reader
#################
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_coding1 = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_mnqyd97b.json")
lottie_coding2 = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_llbjwp92qL.json")
lottie_coding3 = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_D3Jkbk4bHd.json")


#################
# local css reader
#################
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("style/style.css")

#################
# web page
#################
image = Image.open("res.png")
st.image(image, use_column_width=True)
st.header(":blue[SPOTIUUL]")
st.subheader("Welcome to SPOTIUUL musics and artists recommendation website :heart:")

with st.container():
    st.write("---")
    left_col, right_col = st.columns(2)
    with left_col:
        st.title(
            "we are really glad you are here to seek something new & discover someone potential popular artists :star:")
    with right_col:
        st_lottie(lottie_coding2, height=300, key="tree")

with st.container():
    st.write("***")
    left_col, right_col = st.columns(2)
    with left_col:
        st_lottie(lottie_coding3, height=450, key="globe")
    with right_col:
        st.title(
            "Lean back and relax. In this section we're gonna be recommending you shining artists right after we complete searching our artist database most probably you haven't heard them names.")

st.sidebar.header("USER INPUT PARAMETERS")
count = st.sidebar.slider(":blue[recommendation count] :microphone:", 1, 5, 3)
# classes = st.sidebar.multiselect(":green[class selections for second method :microphone:]",['50_60_class', '60_70_class', '80_90_class', '70_80_class',
#       '90_100_class'],["90_100_class"])

with st.container():
    st.write("***")
    left_col, right_col = st.columns(2)
    with left_col:
        st.subheader("results of first method")
        st.write(artist_recomm(df, count))

    with right_col:
        st.subheader("results of second method")
        st.write(outlier(df,count))
