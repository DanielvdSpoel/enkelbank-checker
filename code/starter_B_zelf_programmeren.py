# ============================================================
#  ENKELBAND-CHECKER
#  Route B: ZELF PROGRAMMEREN
#
#  DE ZAAK
#  In Almelo lopen 8 personen met een enkelband rond (E01 t/m E08).
#  De recherche vermoedt dat sommigen stiekem met elkaar afspreken.
#  Jij krijgt hun locatiedata van één weekend.
#
#  JOUW OPDRACHT: beantwoord deze drie vragen
#    1. WIE spreken er met elkaar af?
#    2. WAAR en WANNEER spreken ze af?
#    3. Hoe weet je zeker dat het een AFSPRAAK is en geen TOEVAL?
#
#  HOE WERKT DIT BESTAND?
#  Bij elke stap haal je het # (en de spatie erna) weg voor de code, en vul je
#  op de plek van de vraagtekens (??? of ??) zelf iets in. Lees de tip die erbij staat!
#
#  Doe de stappen op volgorde: latere stappen gebruiken wat je eerder hebt aangezet.
#
#  Rood scherm? Lees de foutmelding en controleer of je het # helemaal
#  hebt weggehaald (ook de spatie) en of er nergens nog vraagtekens staan.
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk


# ------------------------------------------------------------
# STAP 1  Geef je app een naam
# Verander de tekst tussen de aanhalingstekens in je eigen naam.
# ------------------------------------------------------------
st.title("Enkelband-checker van ...")
st.info("Wie spreken er af? Waar en wanneer? En is het een afspraak of toeval?")


# ------------------------------------------------------------
# Al klaar: de agent uploadt hier het bestand.
# ------------------------------------------------------------
bestand = st.file_uploader("Upload de enkelband-data (CSV-bestand)", type="csv")
if bestand is None:
    st.stop()
data = pd.read_csv(bestand, parse_dates=["tijdstip"])
st.write(f"Er zijn **{len(data)}** metingen van **{data['enkelband_id'].nunique()}** personen.")


# ------------------------------------------------------------
# STAP 2  Bekijk de data
# Laat alleen de EERSTE 20 regels zien.
# Tip: de functie heet zoals "de kop van de tabel" in het Engels.
# st.dataframe(data.???(20))
# Wat betekenen de vier kolommen, denk je?
# ------------------------------------------------------------


# ------------------------------------------------------------
# STAP 3  Kies welke personen je wilt bekijken
# In welke KOLOM staat wie wie is? Vul die kolomnaam in op alle drie de plekken.
# personen = st.multiselect("Welke personen?", sorted(data["???"].unique()), default=sorted(data["???"].unique()))
# data = data[data["???"].isin(personen)]
# ------------------------------------------------------------


# ------------------------------------------------------------
# STAP 4  Zet de metingen op de kaart
# Vul in welke kolom de breedtegraad (latitude) en welke de lengtegraad (longitude) is.
# st.map(data, latitude="???", longitude="???", size=20)
# ------------------------------------------------------------


# ------------------------------------------------------------
# Al klaar: deze functie zoekt voor elk moment alle duo's op,
# met hoe ver ze van elkaar af waren (kolom "afstand", in meters).
# ------------------------------------------------------------
def afstand_in_meters(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    h = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6_371_000 * np.arcsin(np.sqrt(h))


def alle_duos(data):
    paren = data.merge(data, on="tijdstip", suffixes=("_1", "_2"))
    paren = paren[paren["enkelband_id_1"] < paren["enkelband_id_2"]].copy()
    paren["afstand"] = afstand_in_meters(paren["lat_1"], paren["lon_1"], paren["lat_2"], paren["lon_2"])
    paren["duo"] = paren["enkelband_id_1"] + " + " + paren["enkelband_id_2"]
    paren["lat"] = (paren["lat_1"] + paren["lat_2"]) / 2
    paren["lon"] = (paren["lon_1"] + paren["lon_2"]) / 2
    return paren[["tijdstip", "duo", "afstand", "lat", "lon"]]


paren = alle_duos(data)


# ------------------------------------------------------------
# STAP 5  Wanneer zijn twee personen SAMEN?
# Hoe dichtbij moet je zijn om "samen" te zijn? Probeer de schuifbalk!
# max_meter = st.slider("Hoe dichtbij is 'samen'? (meter)", 10, 500, 50)
# Vul op de plek van ?? het teken in voor "kleiner dan of gelijk aan".
# Dan houd je alleen de momenten over waarop de afstand hooguit max_meter is.
# Tip: "kleiner dan" schrijf je als <. Voor "of gelijk aan" zet je er nog een = achter.
# samen = paren[paren["afstand"] ?? max_meter]
# st.header(f"{len(samen)} momenten waarop personen samen waren")
# st.dataframe(samen)
# ------------------------------------------------------------


# ------------------------------------------------------------
# STAP 6  Welk duo is het vaakst samen?
# value_counts() telt hoe vaak elke waarde in een kolom voorkomt.
# Welke kolom van 'samen' wil je tellen?
# st.bar_chart(samen["???"].value_counts())
# ------------------------------------------------------------


# ------------------------------------------------------------
# STAP 7  De heatmap: WAAR spreken ze af?
# Welke tabel zet je op de heatmap? Probeer eerst 'data' en daarna 'samen'.
# Wat is het verschil? Welke helpt de recherche?
# st.pydeck_chart(pdk.Deck(layers=[pdk.Layer("HeatmapLayer", data=???, get_position=["lon", "lat"], radius_pixels=40)], initial_view_state=pdk.ViewState(latitude=52.357, longitude=6.663, zoom=12)))
# ------------------------------------------------------------


# ------------------------------------------------------------
# STAP 8 (EXPERT)  Afspraak of toeval?
# Twee mensen die 20 minuten tegelijk in de supermarkt staan: is dat een afspraak?
# Bedenk een regel die echte afspraken van toeval scheidt, en programmeer die.
#
# Ideeën:
#   - Ze moeten op MEERDERE DAGEN samen zijn geweest.
#     Tip: samen["tijdstip"].dt.day geeft de dag van de maand.
#          groupby("duo") + nunique() telt hoeveel verschillende waarden elk duo heeft.
#   - Ze moeten minstens 30 MINUTEN achter elkaar samen zijn.
#     (Er is elke 5 minuten een meting. Hoeveel metingen is 30 minuten?)
#
# Schrijf je code hieronder:

