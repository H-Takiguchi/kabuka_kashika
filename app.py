import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title('たきお 保有株価可視化アプリ')

st.sidebar.write("""
# 国内株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

st.sidebar.write("""
## 表示日数選択
""")

months = st.sidebar.slider('月数', 1, 6, 3)

st.write(f"""
### 過去 **{months}ヶ月間** の国内株価
""")

@st.cache_data
def get_data(months, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{months}mo', interval='1d')
        hist.index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

try:
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください。',
        0.0, 5000.0, (1000.0, 4000.0)
        )

    tickers = {
        '良品計画': '7453.T',
        '森永製菓': '2201.T',
        '明治ホールディングス': '2269.T',
        '小田急電鉄': '9007.T'
    }

    df = get_data(months, tickers)

    companies = st.multiselect(
        '会社名を選択してください。',
        list(df.index),
        ['良品計画', '森永製菓', '明治ホールディングス', '小田急電鉄']
    )

    if not companies:
        st.error('少なくとも一社は選んでください。')
    else:
        data = df.loc[companies]
        st.write("### 株価 (Yen)", data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(Yen)'}
        )

        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(Yen):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )

        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "おっと！なにかエラーが起きているようです。"
    )