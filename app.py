from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# 1. MAGYAR FELIRATOK ÉS KATEGÓRIAFORDÍTÁSOK
# ============================================================

HU_COL = {
    "id": "Azonosító",
    "city": "Város",
    "type": "Ingatlan típusa",
    "squareMeters": "Alapterület (m²)",
    "rooms": "Szobák száma",
    "floor": "Emelet",
    "floorCount": "Emeletek száma",
    "buildYear": "Építés éve",
    "latitude": "Szélességi koordináta",
    "longitude": "Hosszúsági koordináta",
    "centreDistance": "Távolság a központtól",
    "poiCount": "Közeli POI-k száma",
    "schoolDistance": "Iskola távolsága",
    "clinicDistance": "Klinika távolsága",
    "postOfficeDistance": "Posta távolsága",
    "kindergartenDistance": "Óvoda távolsága",
    "restaurantDistance": "Étterem távolsága",
    "collegeDistance": "Főiskola / egyetem távolsága",
    "pharmacyDistance": "Gyógyszertár távolsága",
    "ownership": "Tulajdoni forma",
    "buildingMaterial": "Építőanyag",
    "condition": "Állapot",
    "hasParkingSpace": "Parkolóhely",
    "hasBalcony": "Erkély",
    "hasElevator": "Lift",
    "hasSecurity": "Biztonsági szolgáltatás",
    "hasStorageRoom": "Tároló",
    "price": "Ár (PLN)",
    "price_per_sqm": "Ár/m² (PLN/m²)",
    "city_label": "Város",
    "type_label": "Ingatlan típusa",
    "ownership_label": "Tulajdoni forma",
    "buildingMaterial_label": "Építőanyag",
    "condition_label": "Állapot",
}

HU_VALUE = {
    "blockOfFlats": "Panel / társasházi blokk",
    "blockofflats": "Panel / társasházi blokk",
    "tenement": "Bérház / régi társasház",
    "apartmentBuilding": "Társasház",
    "apartmentbuilding": "Társasház",
    "condominium": "Társasházi tulajdon",
    "cooperative": "Szövetkezeti lakás",
    "concreteSlab": "Panel / betonlap",
    "concreteslab": "Panel / betonlap",
    "brick": "Tégla",
    "low": "Felújítandó / gyengébb állapot",
    "premium": "Prémium / jó állapot",
    "yes": "Igen",
    "no": "Nem",
    True: "Igen",
    False: "Nem",
}

CITY_LABELS = {
    "bialystok": "Białystok",
    "bydgoszcz": "Bydgoszcz",
    "czestochowa": "Częstochowa",
    "gdansk": "Gdańsk",
    "gdynia": "Gdynia",
    "katowice": "Katowice",
    "krakow": "Kraków",
    "lodz": "Łódź",
    "lublin": "Lublin",
    "poznan": "Poznań",
    "radom": "Radom",
    "rzeszow": "Rzeszów",
    "szczecin": "Szczecin",
    "warszawa": "Warszawa",
    "wroclaw": "Wrocław",
}


# ============================================================
# 2. ADATBETÖLTÉS ÉS TISZTÍTÁS
# ============================================================

@dataclass
class LoadInfo:
    rows_raw: int
    rows_clean: int
    columns: list[str]


def _to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _to_text(series: pd.Series) -> pd.Series:
    s = series.astype("string").str.strip()
    s = s.replace(
        {
            "": pd.NA,
            "nan": pd.NA,
            "NaN": pd.NA,
            "none": pd.NA,
            "None": pd.NA,
            "null": pd.NA,
            "NULL": pd.NA,
        }
    )
    return s


def _to_bool_text(series: pd.Series) -> pd.Series:
    s = series.astype("string").str.strip().str.lower()

    mapping = {
        "yes": "yes",
        "true": "yes",
        "1": "yes",
        "y": "yes",
        "t": "yes",
        "igen": "yes",
        "no": "no",
        "false": "no",
        "0": "no",
        "n": "no",
        "f": "no",
        "nem": "no",
        "nan": pd.NA,
        "none": pd.NA,
        "": pd.NA,
    }

    return s.map(mapping).astype("string")


@st.cache_data(show_spinner="Adatok betöltése és tisztítása...")
def load_apartments(csv_path: str) -> tuple[pd.DataFrame, LoadInfo]:
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"Nincs ilyen fájl: {path}")

    df = pd.read_csv(
        path,
        sep=",",
        engine="python",
        on_bad_lines="skip",
        dtype=str,
    )

    rows_raw = len(df)
    df.columns = [c.strip() for c in df.columns]

    required = {"city", "type", "price"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Hiányzó kötelező oszlop(ok): {sorted(missing)}. "
            f"Elérhető oszlopok: {df.columns.tolist()}"
        )

    text_cols = [
        "id",
        "city",
        "type",
        "ownership",
        "buildingMaterial",
        "condition",
    ]

    for col in text_cols:
        if col in df.columns:
            df[col] = _to_text(df[col])

    numeric_cols = [
        "squareMeters",
        "rooms",
        "floor",
        "floorCount",
        "buildYear",
        "latitude",
        "longitude",
        "centreDistance",
        "poiCount",
        "schoolDistance",
        "clinicDistance",
        "postOfficeDistance",
        "kindergartenDistance",
        "restaurantDistance",
        "collegeDistance",
        "pharmacyDistance",
        "price",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = _to_numeric(df[col])

    bool_cols = [
        "hasParkingSpace",
        "hasBalcony",
        "hasElevator",
        "hasSecurity",
        "hasStorageRoom",
    ]

    for col in bool_cols:
        if col in df.columns:
            df[col] = _to_bool_text(df[col])

    df = df.dropna(subset=["city", "type", "price"])

    df["city"] = df["city"].astype("string").str.strip().str.lower()
    df["type"] = df["type"].astype("string").str.strip()

    df = df[df["price"] > 0]

    if "squareMeters" in df.columns:
        df = df[df["squareMeters"].isna() | (df["squareMeters"] > 0)]
        df["price_per_sqm"] = df["price"] / df["squareMeters"]
        df["price_per_sqm"] = df["price_per_sqm"].replace([np.inf, -np.inf], np.nan)

    if "latitude" in df.columns:
        df.loc[~df["latitude"].between(-90, 90), "latitude"] = np.nan

    if "longitude" in df.columns:
        df.loc[~df["longitude"].between(-180, 180), "longitude"] = np.nan

    df["city_label"] = df["city"].map(CITY_LABELS).fillna(df["city"])

    for col in ["type", "ownership", "buildingMaterial", "condition"]:
        if col in df.columns:
            df[col + "_label"] = df[col].map(
                lambda x: HU_VALUE.get(x, HU_VALUE.get(str(x), str(x)))
                if pd.notna(x)
                else pd.NA
            )

    for col in bool_cols:
        if col in df.columns:
            df[col + "_label"] = df[col].map(
                lambda x: HU_VALUE.get(x, str(x))
                if pd.notna(x)
                else pd.NA
            )

    rows_clean = len(df)

    info = LoadInfo(
        rows_raw=rows_raw,
        rows_clean=rows_clean,
        columns=df.columns.tolist(),
    )

    return df, info


# ============================================================
# 3. SEGÉDFÜGGVÉNYEK
# ============================================================

def format_number(value: float | int | None, digits: int = 0) -> str:
    if value is None or pd.isna(value):
        return "nincs adat"

    if digits == 0:
        return f"{value:,.0f}".replace(",", " ")

    return f"{value:,.{digits}f}".replace(",", " ")


def safe_range_slider(
    data: pd.DataFrame,
    column: str,
    label: str,
    step: float = 1.0,
    fmt: str | None = None,
) -> tuple[float, float] | None:
    if column not in data.columns:
        return None

    values = pd.to_numeric(data[column], errors="coerce").dropna()

    if values.empty:
        st.info(f"Nincs használható adat ehhez a szűrőhöz: {label}")
        return None

    lo = float(values.min())
    hi = float(values.max())

    if lo == hi:
        st.info(f"{label}: csak egy érték található: {format_number(lo)}")
        return lo, hi

    return st.slider(
        label=label,
        min_value=float(lo),
        max_value=float(hi),
        value=(float(lo), float(hi)),
        step=float(step),
        format=fmt,
    )


def apply_range_filter(
    data: pd.DataFrame,
    column: str,
    selected_range: tuple[float, float] | None,
) -> pd.DataFrame:
    if selected_range is None or column not in data.columns:
        return data

    lo, hi = selected_range
    return data[data[column].between(lo, hi, inclusive="both")]


def categorical_multiselect(
    label: str,
    data: pd.DataFrame,
    raw_col: str,
) -> list[str]:
    if raw_col not in data.columns:
        return []

    options_df = data[[raw_col]].dropna().drop_duplicates().copy()

    if options_df.empty:
        return []

    options_df["label"] = options_df[raw_col].map(
        lambda x: HU_VALUE.get(x, HU_VALUE.get(str(x), str(x)))
    )

    options_df = options_df.sort_values("label")
    label_to_raw = dict(zip(options_df["label"], options_df[raw_col]))

    selected_labels = st.multiselect(
        label,
        options=list(label_to_raw.keys()),
        default=list(label_to_raw.keys()),
    )

    return [label_to_raw[item] for item in selected_labels]


def rename_for_display(data: pd.DataFrame) -> pd.DataFrame:
    display_df = data.copy()

    technical_cols = [c for c in display_df.columns if c.endswith("_label")]
    display_df = display_df.drop(columns=technical_cols, errors="ignore")

    display_df = display_df.rename(columns=HU_COL)

    return display_df


def prepare_display_numbers(data: pd.DataFrame) -> pd.DataFrame:
    display_df = data.copy()

    for col in display_df.columns:
        if "ár" in col.lower() or "pln" in col.lower():
            if pd.api.types.is_numeric_dtype(display_df[col]):
                display_df[col] = display_df[col].round(0)

        if "alapterület" in col.lower():
            if pd.api.types.is_numeric_dtype(display_df[col]):
                display_df[col] = display_df[col].round(1)

    return display_df


# ============================================================
# 4. STREAMLIT APP
# ============================================================

def main() -> None:
    st.set_page_config(
        page_title="Interaktív Ingatlanpiaci Elemző Dashboard",
        page_icon="🏠",
        layout="wide",
    )

    st.title("🏠 Interaktív Ingatlanpiaci Elemző Dashboard")
    st.caption(
        "Szűrhető, térképes és grafikonos adatvizualizáció "
        "ingatlanhirdetési adatok alapján. "
        "Az alkalmazás célja a lakáspiaci adatok interaktív feltárása, "
        "összehasonlítása és elemzése."
    )

    data_dir = Path(__file__).resolve().parents[1] / "data"
    csv_files = sorted(data_dir.glob("*.csv"))

    if not csv_files:
        st.error(f"Nincs CSV fájl a data mappában: {data_dir}")
        st.stop()

    with st.sidebar:
        st.header("🔎 Keresőmotor / szűrők")

        selected_csv = st.selectbox(
            "Adatfájl",
            options=csv_files,
            format_func=lambda p: p.name,
        )

    try:
        df, info = load_apartments(str(selected_csv))
    except Exception as exc:
        st.error(f"Hiba történt az adatbetöltés közben: {exc}")
        st.stop()

    filtered = df.copy()

    with st.sidebar:
        st.markdown(f"**Adatfájl:** `{selected_csv.name}`")
        st.markdown(f"**Nyers sorok száma:** {format_number(info.rows_raw)}")
        st.markdown(f"**Tisztított sorok száma:** {format_number(info.rows_clean)}")
        st.markdown("**Pénznem:** PLN")

        st.divider()

        city_search = st.text_input(
            "Város keresése",
            placeholder="pl. városnév...",
        ).strip().lower()

        city_options = sorted(filtered["city"].dropna().unique().tolist())
        city_display = {CITY_LABELS.get(c, c): c for c in city_options}
        city_labels = list(city_display.keys())

        if city_search:
            city_labels = [
                label for label in city_labels
                if city_search in label.lower()
                or city_search in city_display[label].lower()
            ]

        selected_city_labels = st.multiselect(
            "Város(ok)",
            options=city_labels,
            default=city_labels,
        )

        selected_cities = [city_display[label] for label in selected_city_labels]

        if selected_cities:
            filtered = filtered[filtered["city"].isin(selected_cities)]

        if "type" in filtered.columns:
            selected_types = categorical_multiselect(
                "Ingatlan típusa",
                filtered,
                raw_col="type",
            )
            if selected_types:
                filtered = filtered[filtered["type"].isin(selected_types)]

        if "ownership" in filtered.columns:
            selected_ownership = categorical_multiselect(
                "Tulajdoni forma",
                filtered,
                raw_col="ownership",
            )
            if selected_ownership:
                filtered = filtered[filtered["ownership"].isin(selected_ownership)]

        if "buildingMaterial" in filtered.columns:
            selected_materials = categorical_multiselect(
                "Építőanyag",
                filtered,
                raw_col="buildingMaterial",
            )
            if selected_materials:
                filtered = filtered[filtered["buildingMaterial"].isin(selected_materials)]

        if "condition" in filtered.columns:
            selected_conditions = categorical_multiselect(
                "Állapot",
                filtered,
                raw_col="condition",
            )
            if selected_conditions:
                filtered = filtered[filtered["condition"].isin(selected_conditions)]

        st.divider()

        price_rng = safe_range_slider(
            filtered,
            "price",
            "Ár intervallum (PLN)",
            step=10000.0,
            fmt="%.0f",
        )
        filtered = apply_range_filter(filtered, "price", price_rng)

        sqm_rng = safe_range_slider(
            filtered,
            "squareMeters",
            "Alapterület (m²) intervallum",
            step=1.0,
            fmt="%.0f",
        )
        filtered = apply_range_filter(filtered, "squareMeters", sqm_rng)

        rooms_rng = safe_range_slider(
            filtered,
            "rooms",
            "Szobaszám intervallum",
            step=0.5,
            fmt="%.1f",
        )
        filtered = apply_range_filter(filtered, "rooms", rooms_rng)

        if "buildYear" in filtered.columns:
            year_rng = safe_range_slider(
                filtered,
                "buildYear",
                "Építési év intervallum",
                step=1.0,
                fmt="%.0f",
            )
            filtered = apply_range_filter(filtered, "buildYear", year_rng)

        if "centreDistance" in filtered.columns:
            centre_rng = safe_range_slider(
                filtered,
                "centreDistance",
                "Távolság a központtól",
                step=0.1,
                fmt="%.1f",
            )
            filtered = apply_range_filter(filtered, "centreDistance", centre_rng)

        st.divider()

        bool_filter_cols = [
            ("hasParkingSpace", "Parkolóhely"),
            ("hasBalcony", "Erkély"),
            ("hasElevator", "Lift"),
            ("hasSecurity", "Biztonsági szolgáltatás"),
            ("hasStorageRoom", "Tároló"),
        ]

        for col, label in bool_filter_cols:
            if col in filtered.columns:
                choice = st.selectbox(
                    label,
                    options=["Mindegy", "Igen", "Nem"],
                    index=0,
                )

                if choice == "Igen":
                    filtered = filtered[filtered[col] == "yes"]
                elif choice == "Nem":
                    filtered = filtered[filtered[col] == "no"]

    if filtered.empty:
        st.warning("A megadott szűrőkkel nincs találat. Lazíts a szűrésen.")
        st.stop()

    st.subheader("📌 Fő mutatók a szűrt adatállomány alapján")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Találatok száma", format_number(len(filtered)))
    col2.metric("Átlagár (PLN)", f"{format_number(filtered['price'].mean())} PLN")
    col3.metric("Mediánár (PLN)", f"{format_number(filtered['price'].median())} PLN")

    if "price_per_sqm" in filtered.columns:
        col4.metric(
            "Medián ár/m²",
            f"{format_number(filtered['price_per_sqm'].median())} PLN/m²",
        )

    if "squareMeters" in filtered.columns:
        col5.metric(
            "Átlagos alapterület",
            f"{format_number(filtered['squareMeters'].mean(), 1)} m²",
        )

    st.caption(
        "A mutatók mindig az aktuális bal oldali szűrők alapján frissülnek, "
        "vagyis a megjelenítés paraméterezhető, az eredeti adatfájl módosítása nélkül."
    )

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "📊 Áttekintő grafikonok",
            "🏙️ Városi összehasonlítás",
            "🗺️ Térkép",
            "🔗 Összefüggések",
            "🧹 Adatminőség",
            "📄 Adattábla",
        ]
    )

    with tab1:
        st.header("📊 Áttekintő grafikonok")

        left, right = st.columns(2)

        with left:
            fig_price_hist = px.histogram(
                filtered,
                x="price",
                nbins=50,
                title="Áreloszlás",
                labels={
                    "price": "Ár (PLN)",
                    "count": "Darabszám",
                },
            )
            fig_price_hist.update_layout(bargap=0.05)
            st.plotly_chart(fig_price_hist, use_container_width=True)

        with right:
            if "squareMeters" in filtered.columns:
                fig_sqm_hist = px.histogram(
                    filtered.dropna(subset=["squareMeters"]),
                    x="squareMeters",
                    nbins=50,
                    title="Alapterület eloszlása",
                    labels={
                        "squareMeters": "Alapterület (m²)",
                        "count": "Darabszám",
                    },
                )
                fig_sqm_hist.update_layout(bargap=0.05)
                st.plotly_chart(fig_sqm_hist, use_container_width=True)

        left, right = st.columns(2)

        with left:
            if "type_label" in filtered.columns:
                type_counts = (
                    filtered["type_label"]
                    .fillna("Nincs adat")
                    .value_counts()
                    .reset_index()
                )
                type_counts.columns = ["Ingatlan típusa", "Darabszám"]

                fig_type = px.bar(
                    type_counts,
                    x="Ingatlan típusa",
                    y="Darabszám",
                    title="Ingatlantípusok megoszlása",
                    text_auto=True,
                )
                st.plotly_chart(fig_type, use_container_width=True)

        with right:
            if "ownership_label" in filtered.columns:
                own_counts = (
                    filtered["ownership_label"]
                    .fillna("Nincs adat")
                    .value_counts()
                    .reset_index()
                )
                own_counts.columns = ["Tulajdoni forma", "Darabszám"]

                fig_own = px.pie(
                    own_counts,
                    names="Tulajdoni forma",
                    values="Darabszám",
                    title="Tulajdoni forma megoszlása",
                    hole=0.35,
                )
                st.plotly_chart(fig_own, use_container_width=True)

    with tab2:
        st.header("🏙️ Városi összehasonlítás")

        city_summary = (
            filtered
            .groupby("city_label", dropna=False)
            .agg(
                darabszam=("price", "size"),
                atlagar=("price", "mean"),
                medianar=("price", "median"),
                atlag_nm=("squareMeters", "mean"),
                median_ar_nm=("price_per_sqm", "median"),
            )
            .reset_index()
            .rename(
                columns={
                    "city_label": "Város",
                    "darabszam": "Darabszám",
                    "atlagar": "Átlagár (PLN)",
                    "medianar": "Mediánár (PLN)",
                    "atlag_nm": "Átlagos alapterület (m²)",
                    "median_ar_nm": "Medián ár/m² (PLN/m²)",
                }
            )
            .sort_values("Darabszám", ascending=False)
        )

        city_summary = city_summary.round(
            {
                "Átlagár (PLN)": 0,
                "Mediánár (PLN)": 0,
                "Átlagos alapterület (m²)": 1,
                "Medián ár/m² (PLN/m²)": 0,
            }
        )

        st.dataframe(city_summary, use_container_width=True, hide_index=True)

        left, right = st.columns(2)

        with left:
            fig_city_count = px.bar(
                city_summary,
                x="Város",
                y="Darabszám",
                title="Hirdetések száma városonként",
                text_auto=True,
            )
            st.plotly_chart(fig_city_count, use_container_width=True)

        with right:
            fig_city_price = px.bar(
                city_summary.sort_values("Medián ár/m² (PLN/m²)", ascending=False),
                x="Város",
                y="Medián ár/m² (PLN/m²)",
                title="Medián ár/m² városonként (PLN/m²)",
                text_auto=".0f",
            )
            st.plotly_chart(fig_city_price, use_container_width=True)

        fig_city_box = px.box(
            filtered,
            x="city_label",
            y="price_per_sqm",
            points="outliers",
            title="Ár/m² szóródása városonként",
            labels={
                "city_label": "Város",
                "price_per_sqm": "Ár/m² (PLN/m²)",
            },
        )
        st.plotly_chart(fig_city_box, use_container_width=True)

    with tab3:
        st.header("🗺️ Térképes megjelenítés")

        st.markdown(
            """
            A térképes megjelenítés az aktuálisan leszűrt lakáshirdetések földrajzi elhelyezkedését mutatja.

            **Kétféle térkép érhető el:**

            1. **Egyedi hirdetések térképe** – minden pont egy konkrét lakáshirdetés.  
               A pont színe az ár/m² értéket, a pont mérete pedig az alapterületet jelzi.

            2. **Városi összesítő térkép** – minden pont egy várost jelöl.  
               A pont mérete a hirdetések számát, a színe pedig a medián ár/m² értéket mutatja.

            Az árak mindenhol **PLN-ben**, az ár/m² mutatók pedig **PLN/m²-ben** értendők.
            """
        )

        required_map_cols = {"latitude", "longitude"}

        if not required_map_cols.issubset(filtered.columns):
            st.warning("Az adatbázisban nincs megfelelő koordinátaoszlop a térképes megjelenítéshez.")
        else:
            map_df = filtered.dropna(subset=["latitude", "longitude"]).copy()

            if map_df.empty:
                st.warning("A szűrt adatok között nincs térképen megjeleníthető koordináta.")
            else:
                if "price_per_sqm" in map_df.columns:
                    map_df["price_per_sqm"] = map_df["price_per_sqm"].replace(
                        [np.inf, -np.inf],
                        np.nan,
                    )

                map_mode = st.radio(
                    "Térkép típusa",
                    options=[
                        "Egyedi hirdetések térképe",
                        "Városi összesítő térkép",
                    ],
                    horizontal=True,
                )

                if map_mode == "Egyedi hirdetések térképe":
                    st.subheader("📍 Egyedi lakáshirdetések térképe")

                    st.info(
                        "Ezen a térképen minden pont egy konkrét lakáshirdetést jelent. "
                        "Ha csak egy város van kiválasztva, a térkép automatikusan ráközelít az adott városra. "
                        "A szín az ár/m² értéket, a pont mérete az alapterületet mutatja."
                    )

                    max_available = int(min(10000, len(map_df)))

                    max_points = st.slider(
                        "Térképen megjelenített maximum pontszám",
                        min_value=1,
                        max_value=max_available,
                        value=max_available if max_available < 3000 else 3000,
                        step=1,
                    )

                    plot_df = map_df.copy()

                    if len(plot_df) > max_points:
                        plot_df = plot_df.sample(max_points, random_state=42)

                    center_lat = float(plot_df["latitude"].mean())
                    center_lon = float(plot_df["longitude"].mean())

                    selected_city_count = (
                        plot_df["city_label"].dropna().nunique()
                        if "city_label" in plot_df.columns
                        else 0
                    )

                    zoom_level = 11 if selected_city_count == 1 else 5

                    color_column = "price_per_sqm" if "price_per_sqm" in plot_df.columns else "price"
                    size_column = "squareMeters" if "squareMeters" in plot_df.columns else None

                    fig_map = px.scatter_mapbox(
                        plot_df,
                        lat="latitude",
                        lon="longitude",
                        color=color_column,
                        size=size_column,
                        size_max=18,
                        zoom=zoom_level,
                        center={
                            "lat": center_lat,
                            "lon": center_lon,
                        },
                        height=650,
                        hover_name="city_label" if "city_label" in plot_df.columns else None,
                        hover_data={
                            "price": ":,.0f" if "price" in plot_df.columns else False,
                            "price_per_sqm": ":,.0f" if "price_per_sqm" in plot_df.columns else False,
                            "squareMeters": ":.1f" if "squareMeters" in plot_df.columns else False,
                            "rooms": True if "rooms" in plot_df.columns else False,
                            "type_label": True if "type_label" in plot_df.columns else False,
                            "buildingMaterial_label": True if "buildingMaterial_label" in plot_df.columns else False,
                            "condition_label": True if "condition_label" in plot_df.columns else False,
                            "latitude": False,
                            "longitude": False,
                        },
                        labels={
                            "city_label": "Város",
                            "price": "Ár (PLN)",
                            "price_per_sqm": "Ár/m² (PLN/m²)",
                            "squareMeters": "Alapterület (m²)",
                            "rooms": "Szobák száma",
                            "type_label": "Típus",
                            "buildingMaterial_label": "Építőanyag",
                            "condition_label": "Állapot",
                        },
                        title="Lakáshirdetések térképen – ár/m² és alapterület alapján",
                    )

                    fig_map.update_layout(mapbox_style="open-street-map")
                    fig_map.update_coloraxes(
                        colorbar_title="Ár/m² (PLN/m²)",
                        colorbar_tickformat=",.0f",
                    )
                    fig_map.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})

                    st.plotly_chart(fig_map, use_container_width=True)

                    st.markdown(
                        """
                        **Értelmezés:**  
                        - egy pont = egy lakáshirdetés;  
                        - a pont színe az ár/m² értéket mutatja **PLN/m²-ben**;  
                        - a pont mérete az alapterületet jelzi;  
                        - a bal oldali szűrők módosításával a térkép is automatikusan változik.
                        """
                    )

                else:
                    st.subheader("🏙️ Városi összesítő térkép")

                    st.info(
                        "Ezen a térképen minden pont egy várost jelent. "
                        "A pont mérete a hirdetések számát, a színe pedig a medián ár/m² értéket mutatja."
                    )

                    city_map = (
                        map_df
                        .groupby("city_label", dropna=False)
                        .agg(
                            latitude=("latitude", "mean"),
                            longitude=("longitude", "mean"),
                            hirdetesek_szama=("price", "size"),
                            atlagar=("price", "mean"),
                            medianar=("price", "median"),
                            atlagos_alapterulet=("squareMeters", "mean"),
                            median_ar_nm=("price_per_sqm", "median"),
                        )
                        .reset_index()
                    )

                    city_map = city_map.dropna(subset=["latitude", "longitude"])

                    if city_map.empty:
                        st.warning("Nincs megjeleníthető városi összesítő adat.")
                    else:
                        center_lat = float(city_map["latitude"].mean())
                        center_lon = float(city_map["longitude"].mean())

                        fig_city_map = px.scatter_mapbox(
                            city_map,
                            lat="latitude",
                            lon="longitude",
                            size="hirdetesek_szama",
                            color="median_ar_nm",
                            size_max=45,
                            zoom=4,
                            center={
                                "lat": center_lat,
                                "lon": center_lon,
                            },
                            height=650,
                            hover_name="city_label",
                            hover_data={
                                "hirdetesek_szama": True,
                                "atlagar": ":,.0f",
                                "medianar": ":,.0f",
                                "median_ar_nm": ":,.0f",
                                "atlagos_alapterulet": ":.1f",
                                "latitude": False,
                                "longitude": False,
                            },
                            labels={
                                "city_label": "Város",
                                "hirdetesek_szama": "Hirdetések száma",
                                "atlagar": "Átlagár (PLN)",
                                "medianar": "Mediánár (PLN)",
                                "median_ar_nm": "Medián ár/m² (PLN/m²)",
                                "atlagos_alapterulet": "Átlagos alapterület (m²)",
                            },
                            title="Városi összesítő térkép – hirdetésszám és medián ár/m² alapján",
                        )

                        fig_city_map.update_layout(mapbox_style="open-street-map")
                        fig_city_map.update_coloraxes(
                            colorbar_title="Medián ár/m² (PLN/m²)",
                            colorbar_tickformat=",.0f",
                        )
                        fig_city_map.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})

                        st.plotly_chart(fig_city_map, use_container_width=True)

                        city_map_display = city_map.rename(
                            columns={
                                "city_label": "Város",
                                "latitude": "Szélességi koordináta",
                                "longitude": "Hosszúsági koordináta",
                                "hirdetesek_szama": "Hirdetések száma",
                                "atlagar": "Átlagár (PLN)",
                                "medianar": "Mediánár (PLN)",
                                "median_ar_nm": "Medián ár/m² (PLN/m²)",
                                "atlagos_alapterulet": "Átlagos alapterület (m²)",
                            }
                        )

                        city_map_display = city_map_display.round(
                            {
                                "Szélességi koordináta": 4,
                                "Hosszúsági koordináta": 4,
                                "Átlagár (PLN)": 0,
                                "Mediánár (PLN)": 0,
                                "Medián ár/m² (PLN/m²)": 0,
                                "Átlagos alapterület (m²)": 1,
                            }
                        )

                        st.markdown("### Városi térképes összesítő tábla")
                        st.dataframe(city_map_display, use_container_width=True, hide_index=True)

                        st.markdown(
                            """
                            **Értelmezés:**  
                            - egy pont = egy város;  
                            - nagyobb pont = több hirdetés az adott városban;  
                            - a szín az adott város medián ár/m² értékét mutatja **PLN/m²-ben**;  
                            - így jól összehasonlíthatók a városok az aktuális szűrés alapján.
                            """
                        )

    with tab4:
        st.header("🔗 Összefüggések vizsgálata")

        scatter_df = filtered.dropna(subset=["squareMeters", "price"]).copy()

        if scatter_df.empty:
            st.warning("Nincs elég adat az ár és alapterület kapcsolatának megjelenítéséhez.")
        else:
            fig_scatter = px.scatter(
                scatter_df,
                x="squareMeters",
                y="price",
                color="city_label",
                size="rooms" if "rooms" in scatter_df.columns else None,
                hover_name="city_label",
                hover_data={
                    "type_label": True if "type_label" in scatter_df.columns else False,
                    "rooms": True if "rooms" in scatter_df.columns else False,
                    "buildYear": True if "buildYear" in scatter_df.columns else False,
                    "price_per_sqm": ":,.0f" if "price_per_sqm" in scatter_df.columns else False,
                },
                title="Ár és alapterület kapcsolata",
                labels={
                    "squareMeters": "Alapterület (m²)",
                    "price": "Ár (PLN)",
                    "city_label": "Város",
                    "rooms": "Szobák száma",
                    "type_label": "Típus",
                    "buildYear": "Építés éve",
                    "price_per_sqm": "Ár/m² (PLN/m²)",
                },
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        left, right = st.columns(2)

        with left:
            if "type_label" in filtered.columns and "price_per_sqm" in filtered.columns:
                fig_type_box = px.box(
                    filtered,
                    x="type_label",
                    y="price_per_sqm",
                    points="outliers",
                    title="Ár/m² ingatlantípus szerint",
                    labels={
                        "type_label": "Ingatlan típusa",
                        "price_per_sqm": "Ár/m² (PLN/m²)",
                    },
                )
                st.plotly_chart(fig_type_box, use_container_width=True)

        with right:
            if "buildingMaterial_label" in filtered.columns and "price_per_sqm" in filtered.columns:
                fig_material_box = px.box(
                    filtered,
                    x="buildingMaterial_label",
                    y="price_per_sqm",
                    points="outliers",
                    title="Ár/m² építőanyag szerint",
                    labels={
                        "buildingMaterial_label": "Építőanyag",
                        "price_per_sqm": "Ár/m² (PLN/m²)",
                    },
                )
                st.plotly_chart(fig_material_box, use_container_width=True)

        if "centreDistance" in filtered.columns:
            centre_df = filtered.dropna(subset=["centreDistance", "price_per_sqm"]).copy()

            if not centre_df.empty:
                fig_distance = px.scatter(
                    centre_df,
                    x="centreDistance",
                    y="price_per_sqm",
                    color="city_label",
                    title="Központtól való távolság és ár/m² kapcsolata",
                    labels={
                        "centreDistance": "Távolság a központtól",
                        "price_per_sqm": "Ár/m² (PLN/m²)",
                        "city_label": "Város",
                    },
                )
                st.plotly_chart(fig_distance, use_container_width=True)

    with tab5:
        st.header("🧹 Adatminőségi kimutatások")

        st.markdown(
            """
            Ez a rész a projektmunkához különösen hasznos, mert bemutatja,
            hogy az adatforrás nem tökéletes, ezért szükség volt rugalmas betöltésre,
            típuskonverzióra és hiányzó adatok kezelésére.
            """
        )

        missing = df.isna().sum().reset_index()
        missing.columns = ["Oszlop", "Hiányzó értékek száma"]
        missing["Hiányzó értékek aránya (%)"] = missing["Hiányzó értékek száma"] / len(df) * 100
        missing["Magyar oszlopnév"] = missing["Oszlop"].map(HU_COL).fillna(missing["Oszlop"])
        missing = missing.sort_values("Hiányzó értékek száma", ascending=False)
        missing["Hiányzó értékek aránya (%)"] = missing["Hiányzó értékek aránya (%)"].round(2)

        st.dataframe(missing, use_container_width=True, hide_index=True)

        missing_for_chart = missing[missing["Hiányzó értékek száma"] > 0]

        if not missing_for_chart.empty:
            fig_missing = px.bar(
                missing_for_chart,
                x="Magyar oszlopnév",
                y="Hiányzó értékek száma",
                title="Hiányzó adatok száma oszloponként",
                text_auto=True,
            )
            st.plotly_chart(fig_missing, use_container_width=True)
        else:
            st.success("A tisztított adatállományban nincs hiányzó érték.")

        col_a, col_b, col_c = st.columns(3)

        col_a.metric("Nyers sorok", format_number(info.rows_raw))
        col_b.metric("Tisztított sorok", format_number(info.rows_clean))
        col_c.metric("Eltávolított / hibás sorok", format_number(info.rows_raw - info.rows_clean))

        st.markdown("### Ismert oszlopok magyar megnevezéssel")

        known_cols = [c for c in df.columns if c in HU_COL]

        known_df = pd.DataFrame(
            {
                "Eredeti oszlopnév": known_cols,
                "Magyar megnevezés": [HU_COL[c] for c in known_cols],
            }
        )

        st.dataframe(known_df, use_container_width=True, hide_index=True)

    with tab6:
        st.header("📄 Szűrt adattábla")

        st.markdown(
            f"A jelenlegi szűrés eredménye: **{format_number(len(filtered))} sor**."
        )

        display_df = rename_for_display(filtered)
        display_df = prepare_display_numbers(display_df)

        st.dataframe(display_df, use_container_width=True, height=500, hide_index=True)

        csv_bytes = display_df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="📥 Szűrt adattábla letöltése CSV-ként",
            data=csv_bytes,
            file_name="szurt_lakasadatok.csv",
            mime="text/csv",
        )

    st.divider()

    st.caption(
        "Projektmunka: komplex adatforrás interaktív megjelenítése, "
        "paraméterezhető szűréssel, grafikonokkal, térképpel és adatminőségi elemzéssel. "
        "Az árak PLN-ben, az ár/m² értékek PLN/m²-ben értendők."
    )


if __name__ == "__main__":
    main()