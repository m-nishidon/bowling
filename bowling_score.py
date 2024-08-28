import gspread
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

from utils import calc_bowling_score

# Google Sheets APIの認証情報を設定
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)
client = gspread.authorize(creds)


def keisha(row, max_):
    rate = max_ / row["人数"]
    for i in range(1, 11):
        row[str(i)] *= rate
    return row[3:-1]


def make_rank(df):
    df = df.sort_values("10", ascending=False)
    df["順位"] = [i + 1 for i in range(df.shape[0])]
    return df


# スプレッドシートのデータを読み込み
@st.cache_data
def read_origin_score():
    # スプレッドシートを開く
    sheet = client.open("スコア表").worksheet("1ゲーム目")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    for col in df.columns[:2:-1]:
        if df[col].sum() > 0:
            break
    current_frame = int(col.split("_")[0])

    df[[str(i) for i in range(1, 11)]] = df[df.columns[3:]].apply(
        calc_bowling_score, result_type="expand", axis=1
    )

    df_team = df[list(df.columns[:3]) + list(df.columns[-10:])].copy()
    df_team = df_team.groupby("チーム", as_index=False).agg(
        {
            "名前": lambda x: "  ".join(x),
            "拠点": "first",
            **{
                col: "sum"
                for col in df_team.columns
                if col not in ["チーム", "名前", "拠点"]
            },
        }
    )
    df_team["人数"] = list(df.groupby("チーム")["名前"].count())
    df_team = df_team.rename(columns={"名前": "メンバー"})
    max_ = df_team["人数"].max()
    df_team[[str(i) for i in range(1, 11)]] = df_team.apply(
        keisha, result_type="expand", axis=1, max_=max_
    )
    df_team = make_rank(df_team)
    df = make_rank(df)

    return df, df_team, current_frame


def read_updated_score():
    # スプレッドシートを開く
    sheet = client.open("スコア表").worksheet("1ゲーム目")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df


df, df_team, current_frame = read_origin_score()


def sidebar_select(df, df_team, colname, multi):
    selected_elements = "ALL"
    st.sidebar.title(f"{colname}選択")
    if colname != "名前":
        labels = ["ALL"] + sorted(df_team[colname].unique())
    else:
        labels = ["ALL"] + sorted(df[colname].unique())

    if not multi:
        selected_elements = set()
        selected_elements.add(
            st.sidebar.selectbox(f"{colname}を選択してください", labels)
        )
    else:
        selected_elements = set(
            st.sidebar.multiselect(f"{colname}を選択してください", labels, labels[0])
        )

    if "ALL" not in selected_elements:
        df = df[df[colname].isin(selected_elements)]
        if colname != "名前":
            df_team = df_team[df_team[colname].isin(selected_elements)]
    return df, df_team, selected_elements


df, df_team, _ = sidebar_select(df, df_team, "拠点", False)
df, df_team, _ = sidebar_select(df, df_team, "チーム", True)
df, df_team, selected_elements = sidebar_select(df, df_team, "名前", True)

current_frame = st.sidebar.slider(
    label="フレームを選択してください", min_value=1, max_value=10, value=current_frame
)


# データを表示
st.title("個人順位表")

if st.button("順位更新"):
    # 再読み込み
    read_origin_score.clear()
    df, df_team = read_origin_score()

st.dataframe(
    df[["順位", str(current_frame), "名前", "拠点", "チーム"]].rename(
        columns={str(current_frame): "得点"}
    ),
    hide_index=True,
)


fig = go.Figure()

for index, row in df.iterrows():
    fig.add_trace(
        go.Scatter(
            x=list(range(1, current_frame + 1)),
            y=row[24 : 24 + current_frame],
            mode="lines+markers",
            name=row["名前"],
        )
    )

fig.update_layout(
    title="個人順位表",
    xaxis_title="フレーム",
    yaxis_title="スコア",
    legend_title="名前",
    xaxis=dict(tickmode="linear"),
    yaxis=dict(rangemode="tozero"),
    hovermode="x unified",
)

st.plotly_chart(fig)


st.dataframe(
    df[["順位", "名前"] + [str(i + 1) for i in range(current_frame)]], hide_index=True
)

if "ALL" in selected_elements:
    st.title("チーム順位表")

    st.dataframe(
        df_team[["順位", "10", "メンバー", "拠点"]].rename(columns={"10": "得点"}),
        hide_index=True,
    )

    fig_team = go.Figure()

    for index, row in df_team.iterrows():
        fig_team.add_trace(
            go.Scatter(
                x=list(range(1, current_frame + 1)),
                y=row[3 : 3 + current_frame],
                mode="lines+markers",
                name=row["メンバー"],
            )
        )

    fig_team.update_layout(
        title="チーム順位表",
        xaxis_title="フレーム",
        yaxis_title="スコア",
        legend_title="メンバー",
        xaxis=dict(tickmode="linear"),
        yaxis=dict(rangemode="tozero"),
        hovermode="x unified",
    )

    st.plotly_chart(fig_team)

else:
    st.write("個人が選択されているため、チーム順位表は表示していません")

st.subheader("データ更新用")
edited_df = st.data_editor(df[df.columns[:-11]], num_rows="dynamic")
