import datetime
import time
import urllib.request
from logging import getLogger
from pathlib import Path

import numpy as np
import pandas as pd  # type: ignore  # noqa: PGH003
from bs4 import BeautifulSoup  # type: ignore  # noqa: PGH003
from tqdm import tqdm  # type: ignore  # noqa: PGH003

logger = getLogger(__name__)


# source https://tkstock.site/2022/09/21/python-weather-historical-data-scraping/
def str2float(weather_data: str) -> float:
    try:
        return float(weather_data)
    except Exception as e:
        logger.exception(e)  # noqa: TRY401
        return np.nan


def scraping(url: str, date: datetime.datetime) -> list[list[str]]:
    # 気象データのページを取得
    html = urllib.request.urlopen(url).read()  # noqa: S310
    soup = BeautifulSoup(html, features="html.parser")
    trs = soup.find("table", {"class": "data2_s"})

    data_list = []
    data_list_per_hour = []

    # table の中身を取得
    for tr in trs.findAll("tr")[2:]:
        tds = tr.findAll("td")

        if tds[1].string is None:
            break

        data_list.append(date)
        data_list.append(tds[0].string)
        data_list.append(str2float(tds[1].string))
        data_list.append(str2float(tds[2].string))
        data_list.append(str2float(tds[3].string))
        data_list.append(str2float(tds[4].string))
        data_list.append(str2float(tds[5].string))
        data_list.append(str2float(tds[6].string))
        data_list.append(str2float(tds[7].string))
        data_list.append(str2float(tds[8].string))
        data_list.append(str2float(tds[9].string))
        data_list.append(str2float(tds[10].string))
        data_list.append(str2float(tds[11].string))
        data_list.append(str2float(tds[12].string))
        data_list.append(str2float(tds[13].string))

        data_list_per_hour.append(data_list)
        data_list = []

    return data_list_per_hour


def get_weather_data(dir_data: str) -> None:
    dir_data = Path(dir_data)

    dir_data.mkdir(parents=True, exist_ok=True)
    # データ取得開始・終了日

    start_date = datetime.date(2022, 4, 24)
    # 実行日を取得
    end_date = datetime.date.today() - datetime.timedelta(days=1)

    # データフレームのカラム定義
    fields = [
        "date",
        "time",
        "pressure_local",
        "pressure_sea",
        "precipitation",
        "temperature",
        "dew_point_humidity",
        "vapor_pressure",
        "humidity",
        "wind_speed",
        "wind_direction",
        "sunshine_hours",
        "total_solar_radiation",
        "snowfall",
        "snow_cover",
    ]

    # fields = ["年月日", "時間", "気圧（現地）", "気圧（海面）",
    #            "降水量", "気温", "露点湿度", "蒸気圧", "湿度",
    #            "風速", "風向", "日照時間", "全天日射量", "降雪", "積雪"]

    date = start_date
    for date in tqdm(pd.date_range(start=start_date, end=end_date, freq="D"), desc="Get weather data"):
        w_data = []
        month = str(date.month).zfill(2)
        day = str(date.day).zfill(2)
        file_name = dir_data / f"{date.year}-{month}-{day}.csv"
        if file_name.exists():
            logger.info(f"{date.year}-{month}-{day}の天気データ取得をスキップしました")
            continue

        # 対象url（今回は東京）
        url = (
            "http://www.data.jma.go.jp/obd/stats/etrn/view/hourly_s1.php?"
            "prec_no=44&block_no=47662&year=%d&month=%d&day=%d&view="
            % (
                date.year,
                date.month,
                date.day,
            )
        )
        data_per_day = scraping(url, date)

        for dpd in data_per_day:
            w_data.append(dpd)

        df_weather = pd.DataFrame(w_data, columns=fields)
        if df_weather.empty:
            logger.info(f"{date.year}-{month}-{day}の天気データが存在しません")
        else:
            df_weather.to_csv(file_name, index=False)
        time.sleep(1)
