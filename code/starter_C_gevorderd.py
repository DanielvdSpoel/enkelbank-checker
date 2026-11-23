# ============================================================
#  ENKELBAND-CHECKER
#  Route C: GEVORDERD (je kunt al een beetje programmeren)
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
#  In deze route schrijf je bijna alles zelf. Overal waar TODO staat, moet jij code
#  schrijven. De tips en links helpen je op weg. Het lastige rekenwerk (afstanden
#  en duo's) is al klaar, en er staat uitgelegd hoe het werkt.
#
#  Handige documentatie:
#    Streamlit: https://docs.streamlit.io/develop/api-reference
#    pandas:    https://pandas.pydata.org/docs/user_guide/10min.html
#    pydeck:    https://deckgl.readthedocs.io/en/latest/
#
#  Je app ververst als je opslaat. Rood scherm? Lees de foutmelding van onder naar
#  boven: de laatste regel zegt wat er mis is, de regel erboven waar.
# ============================================================


# ------------------------------------------------------------
# TODO 1  Imports
# Importeer de vier bibliotheken die je nodig hebt, met deze afkortingen:
#   streamlit -> st     (de app zelf: knoppen, tabellen, kaarten)
#   pandas    -> pd     (werken met tabellen, "DataFrames")
#   numpy     -> np     (rekenen met hele kolommen tegelijk; de hulpfuncties hieronder gebruiken dit)
#   pydeck    -> pdk    (geavanceerde kaarten, zoals de heatmap)
# Voorbeeld van één import:  import streamlit as st
# ------------------------------------------------------------



# ------------------------------------------------------------
# TODO 2  Titel en data inladen
# a) Geef je app een titel met st.title(...)
# b) Laat de agent een CSV-bestand uploaden met st.file_uploader(...).
#    Zolang er nog niets is geüpload, geeft die functie None terug. Stop de app dan
#    netjes met st.stop(), anders krijg je verderop fouten.
# c) Lees het bestand in met pd.read_csv(...).
#    Let op: de kolom "tijdstip" moet als datum/tijd worden ingelezen, niet als tekst.
#    Zoek in de documentatie van read_csv naar de parameter "parse_dates".
# d) Laat met st.write(...) zien hoeveel metingen en hoeveel personen er zijn.
#    Tip: len(data) en data["enkelband_id"].nunique()
#
# Noem je tabel "data", want de code hieronder gaat daarvan uit.
# Documentatie: https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader
# ------------------------------------------------------------



# ------------------------------------------------------------
# TODO 3  Filters in een zijbalk
# Alles wat je met st.sidebar.<iets> maakt, komt in een zijbalk links.
# a) Maak met st.sidebar.multiselect(...) een keuzelijst met alle personen
#    (alle unieke waarden uit de kolom "enkelband_id"), standaard allemaal aangevinkt.
# b) Uitdaging: maak met st.sidebar.slider(...) een schuifbalk met een begin- en eindtijd.
#    Als je een slider een tuple met twee waarden als value geeft, krijg je een "bereik".
#    Tip: data["tijdstip"].min() en .max() zijn pandas-tijdstempels; .to_pydatetime() maakt
#    er gewone Python-datetimes van, die de slider begrijpt.
# c) Filter "data" zodat alleen de gekozen personen en tijden overblijven.
#    Tip: data[data["enkelband_id"].isin(...)]  en  data["tijdstip"].between(begin, eind)
# ------------------------------------------------------------



# ------------------------------------------------------------
# TODO 4  Alle metingen op de kaart
# Simpel: st.map(...) met de kolommen "lat" en "lon".
# Uitdaging: geef elke persoon een eigen kleur. st.map heeft een parameter "color" die
# een kolomnaam accepteert. Maak dus eerst een kolom met een kleur per persoon,
# bijvoorbeeld met een dictionary en data["enkelband_id"].map(...).
# Kleuren mogen als hex-tekst, zoals "#0093D9".
# ------------------------------------------------------------



# ============================================================
# AL KLAAR: het rekenwerk
# Je hoeft hier niets aan te veranderen, maar lees de uitleg: je hebt deze
# functies nodig in de volgende TODO's.
# ============================================================

def afstand_in_meters(lat1, lon1, lat2, lon2):
    """
    Berekent de afstand in meters tussen twee punten op aarde.

    Waarom niet gewoon Pythagoras?
        Breedte- en lengtegraden zijn hoeken op een bol, geen meters op een plat vlak.
        Eén graad lengte is op de evenaar ±111 km, maar in Almelo maar ±68 km.
        Daarom gebruiken we de "haversine-formule": die rekent de afstand uit over
        het oppervlak van een bol met de straal van de aarde (6.371 km).

    Waarom werkt dit op hele kolommen tegelijk?
        lat1, lon1, lat2 en lon2 mogen losse getallen zijn, maar ook hele pandas-kolommen.
        numpy-functies zoals np.sin rekenen dan voor elke regel tegelijk. Dat heet
        "vectoriseren" en is veel sneller dan een for-loop over duizenden regels.

    Geeft terug: de afstand(en) in meters.
    """
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])  # graden -> radialen
    h = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6_371_000 * np.arcsin(np.sqrt(h))


def alle_duos(data):
    """
    Maakt een tabel met ALLE duo's die op hetzelfde moment gemeten zijn,
    en hoe ver ze toen van elkaar af waren.

    Hoe werkt het?
      1. data.merge(data, on="tijdstip") koppelt de tabel aan zichzelf ("self-join"):
         elke meting wordt gecombineerd met elke andere meting van hetzelfde tijdstip.
         Met 8 personen geeft dat per tijdstip 8 x 8 = 64 combinaties.
         De kolommen van de twee kanten krijgen _1 en _2 achter hun naam.
      2. We houden alleen combinaties waarbij id_1 < id_2. Zo vervallen
         "E01 met E01" (iemand met zichzelf) en dubbelingen ("E02 + E01" is
         hetzelfde als "E01 + E02"). Er blijven 28 duo's per tijdstip over.
      3. Voor elke regel berekenen we de afstand met afstand_in_meters.
      4. We maken een kolom "duo" (bijv. "E02 + E05") en zetten het punt precies
         tussen de twee personen in "lat" en "lon", zodat je het op een kaart kunt zetten.

    Geeft terug: een DataFrame met de kolommen tijdstip, duo, afstand, lat, lon.
    """
    paren = data.merge(data, on="tijdstip", suffixes=("_1", "_2"))
    paren = paren[paren["enkelband_id_1"] < paren["enkelband_id_2"]].copy()
    paren["afstand"] = afstand_in_meters(paren["lat_1"], paren["lon_1"], paren["lat_2"], paren["lon_2"])
    paren["duo"] = paren["enkelband_id_1"] + " + " + paren["enkelband_id_2"]
    paren["lat"] = (paren["lat_1"] + paren["lat_2"]) / 2
    paren["lon"] = (paren["lon_1"] + paren["lon_2"]) / 2
    return paren[["tijdstip", "duo", "afstand", "lat", "lon"]]


# ------------------------------------------------------------
# TODO 5  Wie is er SAMEN?
# a) Roep alle_duos(data) aan en sla het resultaat op als "paren".
# b) Maak een slider "max_meter": hoe dichtbij is samen? (bijv. 10 tot 500 meter, standaard 50)
# c) Maak een nieuwe tabel "samen" met alleen de regels uit "paren" waar de afstand
#    kleiner dan of gelijk aan max_meter is. Dit heet "boolean indexing" in pandas.
# d) Laat zien hoeveel momenten dat zijn, en toon de tabel.
#
# Uitdaging: alle_duos is best zwaar. Elke keer dat je een slider verschuift, draait
# Streamlit je HELE script opnieuw, dus ook die berekening. Zoek uit wat
# @st.cache_data doet en hoe je het kunt gebruiken om je app sneller te maken.
# https://docs.streamlit.io/develop/concepts/architecture/caching
# ------------------------------------------------------------



# ------------------------------------------------------------
# TODO 6  Wie en wanneer?
# a) Maak een staafdiagram (st.bar_chart) van hoe vaak elk duo samen was.
#    Tip: value_counts()
# b) Op welke uren van de dag zijn ze samen? Tip: samen["tijdstip"].dt.hour
# c) Uitdaging: zet je grafieken en tabellen netjes in tabbladen met st.tabs(...).
# ------------------------------------------------------------



# ------------------------------------------------------------
# TODO 7  De heatmap: WAAR?
# Maak een pydeck-kaart met een "HeatmapLayer":
#     laag = pdk.Layer("HeatmapLayer", data=..., get_position=["lon", "lat"], radius_pixels=40)
#     beeld = pdk.ViewState(latitude=52.357, longitude=6.663, zoom=12)
#     st.pydeck_chart(pdk.Deck(layers=[laag], initial_view_state=beeld))
# Probeer het met "data" en met "samen". Wat is het verschil, en welke helpt de recherche?
# Uitdaging: voeg een tweede laag toe (bijv. "ScatterplotLayer") met de losse ontmoetingen.
# ------------------------------------------------------------



# ------------------------------------------------------------
# TODO 8  Afspraak of toeval?
# Twee mensen die 20 minuten tegelijk in de supermarkt staan: is dat een afspraak?
# Programmeer minstens één van deze regels, en kijk welke duo's overblijven:
#
#  Regel 1: ze waren op MEERDERE DAGEN samen.
#    Tip: maak een kolom met de dag (.dt.day) en gebruik groupby("duo") + nunique().
#
#  Regel 2: ze waren minstens 30 MINUTEN ACHTER ELKAAR samen (6 metingen van 5 minuten).
#    Dit is lastiger. Een handige techniek ("aaneengesloten blokken vinden"):
#      - sorteer "samen" op duo en tijdstip;
#      - bereken per duo het tijdsverschil met de vorige regel: groupby("duo")["tijdstip"].diff();
#      - is dat verschil NIET precies 5 minuten (pd.Timedelta(minutes=5)), dan begint er
#        een nieuw blok. Dat geeft een kolom met True/False;
#      - .cumsum() op die kolom geeft elk blok een eigen nummer (True telt als 1);
#      - groupby op duo + bloknummer, en tel per blok het aantal metingen.
#
#  Regel 3: bedenk je eigen regel! Bijvoorbeeld: 's nachts, of steeds op dezelfde plek.
#
# Bonus: laat de agent het resultaat downloaden met st.download_button(...).
# Tip: een DataFrame wordt CSV-tekst met .to_csv(index=False).
# ------------------------------------------------------------

