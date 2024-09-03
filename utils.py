import gspread
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials


def calc_bowling_score(pins):
    from itertools import accumulate

    types, cnts = get_one_game_info(pins[:21])
    t2, c2 = get_one_game_info(pins[21:])
    types += t2
    cnts += c2

    first = True
    scores = []
    for i, (type_, cnt) in enumerate(zip(types[:-3], cnts[:-3])):
        if type_ == 1:
            scores.append(cnt + cnts[i + 1] + cnts[i + 2])
        elif first:
            first ^= True
            continue
        else:
            if type_ == 2:
                scores.append(cnts[i - 1] + cnt + cnts[i + 1])
            else:
                scores.append(cnts[i - 1] + cnt)
            first ^= True

    scores.append(sum(pins[-3:]))
    return list(accumulate(scores))


def get_one_game_info(pins):
    pins = list(pins)
    odd = False
    cnts = []
    types = []  # 0特になし、1ストライク、2スペア
    for pin in pins[:-3]:
        odd ^= True
        if odd:
            if pin == 10:
                cnts.append(pin)
                types.append(1)
            else:
                cnts.append(pin)
                types.append(0)
        else:
            if types[-1] == 1:
                continue
            elif cnts[-1] + pin == 10:
                cnts.append(pin)
                types.append(2)
            else:
                cnts.append(pin)
                types.append(0)

    types += [0, 0, 0]
    cnts += pins[-3:]
    return types, cnts


# スプレッドシートのデータを読み込み
@st.cache_data
def read_origin_score():
    client = connect_spread_sheet()
    # スプレッドシートを開く
    try:
        spreadsheet = client.open("スコア表").worksheet("data")
    except AttributeError:
        connect_spread_sheet.clear()
        client = connect_spread_sheet()
        spreadsheet = client.open("スコア表").worksheet("data")

    sheet_data = spreadsheet.get_all_records()

    df = pd.DataFrame(sheet_data)

    df, df_conf = df[df.columns[:-3]].copy(), df[df.columns[-3:]][:2].copy()
    for col in df.columns[:2:-1]:
        if df[col].sum() > 0:
            break
    current_frame = int(col.split("_")[0])

    df[[str(i) for i in range(1, 21)]] = df[df.columns[3:]].apply(
        calc_bowling_score, result_type="expand", axis=1
    )

    df_team = df[list(df.columns[:3]) + list(df.columns[-20:])].copy()
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
    df_team[[str(i) for i in range(1, 21)]] = df_team.apply(
        keisha, result_type="expand", axis=1, max_=max_
    )
    df_team = make_rank(df_team)
    df = make_rank(df)

    return df, df_team, current_frame, df_conf


@st.cache_data
def connect_spread_sheet():
    # Google Sheets APIの認証情報を設定
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    return gspread.authorize(creds)


def keisha(row, max_):
    rate = max_ / row["人数"]
    for i in range(1, 21):
        row[str(i)] *= rate
    return row[3:-1]


def make_rank(df):
    df = df.sort_values("20", ascending=False)
    df["順位"] = [i + 1 for i in range(df.shape[0])]
    return df


# def read_updated_score():
#     # スプレッドシートを開く
#     sheet = client.open("スコア表").worksheet("1ゲーム目")
#     data = sheet.get_all_records()
#     df = pd.DataFrame(data)
#     return df


def send_message(message, token):
    headers = {
        "Authorization": f"Bearer {token}",
    }

    files = {
        "message": (None, message),
    }

    requests.post("https://notify-api.line.me/api/notify", headers=headers, files=files)
