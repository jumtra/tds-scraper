import re
import time
from logging import getLogger
from pathlib import Path
from typing import TypedDict

import pandas as pd
from bs4 import BeautifulSoup

from tds_scraper.core.scraper.common_scraper import get_text_from_url
from tds_scraper.core.scraper.land_to_theme import dict_land_to_theme

logger = getLogger(__name__)


__all__ = ["get_distance_data"]


AttractionName = str
AttractionURL = dict | str
ThemeLand = str
ListAttraction = list[AttractionName]
AttractionNameToURLDict = dict[AttractionName, AttractionURL]


def _get_attraction_url(soup: BeautifulSoup, main_url: str) -> dict[ThemeLand, AttractionNameToURLDict]:
    dict_theme_land_to_attraction_url = {}
    for theme_land in soup.find_all("h2", class_="title"):
        dict_attraction_url = {}
        for i_attraction, attraction in enumerate(theme_land.nextSibling()):
            if i_attraction % 4 == 1:
                attraction_name = attraction.text
                attraction_link = main_url + attraction["href"]
                dict_attraction_url[str(attraction_name)] = str(attraction_link)
        dict_theme_land_to_attraction_url[str(theme_land.text)] = dict_attraction_url
    return dict_theme_land_to_attraction_url


def _calc_seconds(time_str: str) -> int:
    """Minutes convert to seconds."""
    time_str = time_str.replace(" ", "")
    if "分" not in time_str:
        time_str = "0分" + time_str
    pattern = r"(\d+)分(\d+)秒"
    match: re.Match[str] | None = re.match(pattern, time_str)
    if match is None:
        raise  # noqa: PLE0704
    minutes = int(match.group(1))
    seconds = int(match.group(2))
    return minutes * 60 + seconds


def _get_lat_log(string: str) -> tuple[float | None, float | None]:
    """スクレイピング先からアトラクションの座標を取得."""
    pattern = r"new google\.maps\.LatLng\(([-+]?\d+\.\d+), ([-+]?\d+\.\d+)\)"
    match = re.search(pattern, string)
    if match:
        latitude = float(match.group(1))
        longitude = float(match.group(2))

        return latitude, longitude
    return None, None


class ScrapeBase(TypedDict):
    from_theme: list[None | str]
    from_attraction: list[None | str]
    to_attraction: list[None | str]
    to_theme: list[None | str]
    distance_m: list[None | float]
    steps: list[None | float]
    time_s: list[None | float]


class ScrapePosBase(TypedDict):
    theme_park: list[None | str]
    attraction: list[None | str]
    lat: list[None | float]
    lon: list[None | float]


def _get_dataframe(
    list_theme: ListAttraction,
    dict_theme_land_to_attraction_url: AttractionNameToURLDict,
) -> dict[dict, dict]:  # noqa: ANN202
    dict_base = ScrapeBase(
        from_theme=[],
        from_attraction=[],
        to_attraction=[],
        to_theme=[],
        distance_m=[],
        steps=[],
        time_s=[],
    )
    dict_pos_base = ScrapePosBase(
        theme_park=[],
        attraction=[],
        lat=[],
        lon=[],
    )
    for theme_land in list_theme:
        for attraction_name, attraction_url in dict_theme_land_to_attraction_url[theme_land].items():
            base_url = "/".join(attraction_url.split("/")[:-1])
            logger.info(f"アトラクション: {attraction_name}のデータを取得します。")
            try:
                soup = get_text_from_url(url=attraction_url)
                col_distance = soup.find_all("td", class_="hosuu_col1")
                col_attr_name = soup.find_all("td", class_="hosuu_col2")
                col_step_time = soup.find_all("td", class_="hosuu_col3")
                for distance, attr_name, step_time in zip(
                    col_distance,
                    col_attr_name,
                    col_step_time,
                    strict=True,
                ):
                    to_attraction_name = attr_name.find_all("a")[0].text
                    to_theme_name = attr_name.find_all("span")[0].text
                    dict_base["from_theme"].append(theme_land)
                    dict_base["from_attraction"].append(attraction_name)
                    dict_base["to_theme"].append(to_theme_name)
                    dict_base["to_attraction"].append(to_attraction_name)
                    dict_base["distance_m"].append(int(distance.text.split(" ")[0]))
                    steps, pred_time = step_time.text.split("歩")
                    dict_base["steps"].append(int(steps))
                    dict_base["time_s"].append(_calc_seconds(pred_time))

                    # 緯度経度情報を取得する
                    if to_attraction_name not in dict_pos_base["attraction"]:
                        attr_url = base_url + "/" + attr_name.find_all("a")[0]["href"]
                        time.sleep(1)
                        pos_soup = get_text_from_url(url=attr_url)
                        lat, lon = _get_lat_log(pos_soup.find_all("script", type="text/javascript")[0].string)
                        dict_pos_base["lat"].append(lat)
                        dict_pos_base["lon"].append(lon)
                        dict_pos_base["attraction"].append(to_attraction_name)
                        dict_pos_base["theme_park"].append(to_theme_name)

            except Exception as e:
                logger.error(f"データの取得に失敗しました。\n{e}")
        time.sleep(1)
    return dict_base, dict_pos_base


def get_distance_data(dir_data: str) -> None:
    dir_data = Path(dir_data)
    url = "https://disney.hosuu.jp/attractions.php"
    main_url = "/".join(url.split("/")[:-1]) + "/"
    # BeautifulSoupオブジェクト生成
    soup = get_text_from_url(url=url)

    dict_theme_land_to_attraction_url = _get_attraction_url(soup=soup, main_url=main_url)
    for land_name, list_theme in dict_land_to_theme.items():
        logger.info(f"{land_name}のデータを取得します。")
        if not (dir_data / f"{land_name}/distance.csv").exists():
            dict_df, _ = _get_dataframe(
                list_theme=list_theme,
                dict_theme_land_to_attraction_url=dict_theme_land_to_attraction_url,
            )
            logger.info(f"{land_name}のデータを保存します。")
            (dir_data / land_name).mkdir(exist_ok=True, parents=True)
            pd.DataFrame(dict_df).to_csv(dir_data / f"{land_name}/distance.csv", index=False)
