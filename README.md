# Interaktív Ingatlanpiaci Elemző Dashboard

Ez a projekt egy ingatlanhirdetési adatbázis interaktív Streamlit-alapú megjelenítését valósítja meg.

Az alkalmazás célja, hogy egy komplex, több ezer soros adatforrást felhasználóbarát módon lehessen vizsgálni szűrők, grafikonok, térképes megjelenítés és adatminőségi kimutatások segítségével.

## Projekt célja

A projekt célja egy olyan interaktív adatvizualizációs dashboard létrehozása, amely ingatlanhirdetési adatok alapján támogatja az adatok feltárását, összehasonlítását és elemzését.

Az alkalmazás lehetőséget ad arra, hogy a felhasználó különböző paraméterek szerint szűrje az adatokat, majd a szűrés eredményét grafikonokon, térképen és táblázatos formában is megtekinthesse.

A megoldás megfelel annak a projektkövetelménynek, hogy egy komplex adatforrás interaktív megjelenítése történjen meg, Excel-előfeldolgozás nélkül, Python és Streamlit használatával.

## Adatforrás

Az alkalmazás bemeneti adatfájlja:

```text
data/apartments_pl_2023_08.csv
```

Az adatfájl lakáshirdetési adatokat tartalmaz. Az adatbázisban többek között város, ingatlantípus, ár, alapterület, szobaszám, építési év, koordináta, tulajdoni forma, építőanyag és állapot szerinti információk szerepelnek.

Az árak az adatállomány alapján PLN-ben, azaz lengyel złotyban értendők.

Fontosabb oszlopok:

```text
city → Város
type → Ingatlan típusa
price → Ár (PLN)
squareMeters → Alapterület (m²)
rooms → Szobák száma
floor → Emelet
floorCount → Emeletek száma
buildYear → Építés éve
latitude → Szélességi koordináta
longitude → Hosszúsági koordináta
centreDistance → Távolság a központtól
ownership → Tulajdoni forma
buildingMaterial → Építőanyag
condition → Állapot
hasParkingSpace → Parkolóhely
hasBalcony → Erkély
```

## Fő funkciók

Az alkalmazás főbb funkciói:

- interaktív oldalsávos szűrők,
- város szerinti keresés és szűrés,
- ingatlantípus szerinti szűrés,
- tulajdoni forma szerinti szűrés,
- építőanyag és állapot szerinti szűrés,
- árintervallum szerinti szűrés,
- alapterület szerinti szűrés,
- szobaszám szerinti szűrés,
- építési év szerinti szűrés,
- központtól való távolság szerinti szűrés,
- parkolóhely, erkély, lift és egyéb jellemzők szerinti szűrés,
- KPI mutatók megjelenítése,
- áreloszlás és alapterület-eloszlás vizsgálata,
- városi összehasonlító grafikonok,
- térképes megjelenítés,
- egyedi hirdetések térképe,
- városi összesítő térkép,
- ár/m² elemzések,
- adatminőségi kimutatás,
- szűrt adattábla megjelenítése,
- szűrt adattábla letöltése CSV-formátumban.

## Interaktív szűrés

Az alkalmazás bal oldali oldalsávjában találhatók a szűrők. Ezekkel a felhasználó dinamikusan módosíthatja, hogy mely hirdetések jelenjenek meg a grafikonokon, térképen és táblázatban.

A szűrés nem módosítja az eredeti CSV-fájlt. A szűrők kizárólag a megjelenített adatállományt változtatják.

## KPI mutatók

A főoldalon az aktuálisan szűrt adatok alapján az alábbi fő mutatók jelennek meg:

```text
Találatok száma
Átlagár (PLN)
Mediánár (PLN)
Medián ár/m² (PLN/m²)
Átlagos alapterület
```

Ezek a mutatók minden szűrés után automatikusan frissülnek.

## Grafikonok

Az alkalmazás többféle grafikus megjelenítést tartalmaz:

- áreloszlás,
- alapterület-eloszlás,
- ingatlantípusok megoszlása,
- tulajdoni forma megoszlása,
- hirdetések száma városonként,
- medián ár/m² városonként,
- ár/m² szóródása városonként,
- ár és alapterület kapcsolata,
- ár/m² ingatlantípus szerint,
- ár/m² építőanyag szerint,
- központtól való távolság és ár/m² kapcsolata.

## Térképes megjelenítés

Az alkalmazás kétféle térképes nézetet tartalmaz.

### Egyedi hirdetések térképe

Ebben a nézetben minden pont egy konkrét lakáshirdetést jelöl.

A térképen:

- a pont helye a szélességi és hosszúsági koordináták alapján jelenik meg,
- a pont színe az ár/m² értéket mutatja,
- a pont mérete az alapterületet jelzi.

Ez a nézet alkalmas arra, hogy a felhasználó megnézze, földrajzilag hol helyezkednek el a szűrt hirdetések.

### Városi összesítő térkép

Ebben a nézetben minden pont egy várost jelöl.

A térképen:

- a pont mérete a hirdetések számát mutatja,
- a pont színe a medián ár/m² értéket mutatja.

Ez a nézet városi szintű összehasonlításra alkalmas.

## Adatminőségi kimutatás

Az alkalmazás külön fülön jeleníti meg az adatminőségi információkat.

Ez a rész bemutatja:

- az egyes oszlopokban található hiányzó értékek számát,
- a hiányzó értékek arányát,
- a nyers sorok számát,
- a tisztított sorok számát,
- az eltávolított vagy hibás sorok számát,
- az ismert oszlopok magyar megnevezését.

Ez a funkció azért fontos, mert igazolja, hogy a projekt nemcsak megjeleníti az adatokat, hanem az adatminőséget is vizsgálja.

## Adatbetöltés és adattisztítás

A végleges verzióban az adatbetöltési és adattisztítási logika közvetlenül az `app.py` fájlban található.

Az alkalmazás az adatbetöltés során:

- ellenőrzi, hogy a CSV-fájl létezik-e,
- beolvassa az adatokat,
- megtisztítja az oszlopneveket,
- ellenőrzi a kötelező oszlopokat,
- numerikus típussá alakítja a megfelelő mezőket,
- kezeli a hiányzó értékeket,
- kiszűri a hibás árakat,
- kiszámítja az ár/m² mutatót,
- ellenőrzi a koordináták érvényességét,
- magyar megnevezéseket rendel az oszlopokhoz és kategóriákhoz.

A fejlesztés során készült külön `data_loader.py` fájl is, de a végleges alkalmazásban az egyszerűbb futtathatóság érdekében az adatbetöltési logika az `app.py` fájlba került beépítésre. Emiatt a program futtatásához külön `data_loader.py` modul nem szükséges.

## Projektstruktúra

A projekt javasolt mappaszerkezete:

```text
apartments_search_app/
│
├── app/
│   └── app.py
│
├── data/
│   └── apartments_pl_2023_08.csv
│
├── screenshots/
│   ├── 01_fooldal_kpi.png
│   ├── 02_attekinto_grafikonok.png
│   ├── 03_varosi_osszehasonlitas.png
│   ├── 04_terkep_egyedi_hirdetesek.png
│   ├── 05_terkep_varosi_osszesito.png
│   ├── 06_adatminoseg.png
│   └── 07_adattabla.png
│
├── README.md
└── requirements.txt
```

## Szükséges csomagok

A projekt futtatásához szükséges Python-csomagok:

```text
streamlit
pandas
numpy
plotly
```

Ezek a `requirements.txt` fájlban szerepelnek.

Telepítés:

```powershell
python -m pip install -r requirements.txt
```

## Futtatás

A projekt gyökérmappájából a következő paranccsal indítható az alkalmazás:

```powershell
python -m streamlit run app/app.py
```

Sikeres indítás után a böngészőben az alkalmazás az alábbi címen érhető el:

```text
http://localhost:8501
```

## Megjegyzés a futtatáshoz

Streamlit alkalmazást nem célszerű a PyCharm zöld Run gombjával indítani. A helyes futtatási mód a terminálos indítás:

```powershell
python -m streamlit run app/app.py
```

Ha az alkalmazás már fut, a terminálban a következő billentyűkombinációval lehet leállítani:

```text
Ctrl + C
```

Ezután újraindítható a fenti futtatási paranccsal.

## Beadandóhoz javasolt fájlok

A beadandóhoz az alábbi fájlokat és mappákat érdemes csatolni:

```text
app/app.py
data/apartments_pl_2023_08.csv
requirements.txt
README.md
screenshots/
fejlesztési_jegyzet.docx vagy fejlesztési_jegyzet.pdf
```

A `.venv`, `.venv2` és `__pycache__` mappákat nem szükséges csatolni.

## Rövid összefoglaló

A projekt egy interaktív ingatlanpiaci elemző dashboardot valósít meg Streamlitben. Az alkalmazás egy komplex lakáshirdetési adatbázist dolgoz fel, majd szűrhető, grafikonos, térképes és táblázatos formában jeleníti meg az adatokat. A rendszer támogatja az adatok feltárását, a városi összehasonlítást, az ár/m² alapú elemzést, valamint az adatminőség vizsgálatát is.