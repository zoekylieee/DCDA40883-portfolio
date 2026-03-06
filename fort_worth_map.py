"""
Fort Worth Hometown Map
=======================
Reads hometown location data, geocodes addresses via the Mapbox API,
and builds an interactive Folium map with custom markers and pop-ups.

Requirements:
    pip install folium requests

Usage:
    python fort_worth_map.py
    → Opens / saves  fort_worth_map.html
"""

import csv
import time
import webbrowser
import requests
import folium
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIG  –  paste your own tokens here
# ─────────────────────────────────────────────
MAPBOX_TOKEN = "pk.eyJ1Ijoiem9la3lsaWVlZSIsImEiOiJjbW1lN3Eyd28wNzFjMm9wczR5cnN2eHZ4In0.ycbhQrdBHqi5O5KJ41GicQ"

# Mapbox tile URL – uses your account's default style (Mapbox Streets).
# To use a custom style: replace the style ID below with yours from
# https://studio.mapbox.com  e.g.  zoekylieee/cm.....
MAPBOX_TILE_URL = (
    "https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/256/{z}/{x}/{y}@2x"
    f"?access_token={MAPBOX_TOKEN}"
)
MAPBOX_ATTRIBUTION = (
    '© <a href="https://www.mapbox.com/">Mapbox</a> '
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
)

OUTPUT_FILE = "fort_worth_map.html"
CSV_FILE    = "FortWorth_-_Sheet1.csv"   # path to your CSV

# ─────────────────────────────────────────────
# LOCATION DATA  (parsed from your CSV)
# The CSV is stored with each location as a column, so we hard-code
# the cleaned data here for reliability; the CSV parser below will
# override these values if the file is present.
# ─────────────────────────────────────────────
DEFAULT_LOCATIONS = [
    {
        "name":        "Paschal High School",
        "address":     "3001 Forest Park Blvd, Fort Worth, TX 76110",
        "type":        "School",
        "description": "This was my high school and I met some of my closest friends here. I also enjoyed my teachers.",
        "image_url":   "https://fwisd2017bond.com/wp-content/uploads/2018/08/rl-paschal-scaled.jpg",
    },
    {
        "name":        "Pie Tap Restaurant + Bar",
        "address":     "1301 W Magnolia Ave, Fort Worth, TX 76104",
        "type":        "Restaurant",
        "description": "I worked at this restaurant for 3 years and became good friends with my coworkers. I enjoyed the community within this restaurant.",
        "image_url":   "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/2f/bb/f4/ff/caption.jpg?w=900&h=500&s=1",
    },
    {
        "name":        "Kimbell Art Museum",
        "address":     "3333 Camp Bowie Blvd, Fort Worth, TX 76107",
        "type":        "Museum",
        "description": "I grew up going to this museum, and enjoyed learning about art. I am currently interning here, and love it.",
        "image_url":   "https://lh3.googleusercontent.com/gps-cs-s/AHVAweqc6NKgTFsuN3t-NVbIUZ46Ye7jQJ7zwwwuGEfk2SvcbAZ3Hl6qgFjOKCm4V1wGqSul8tQf-kv8sB9KCPmRMYfqW7ZusHsJHl74VzmfJzP6yAnPjemBl-I7fBI1N7hh6GmKfqv9ZA=s1360-w1360-h1020-rw",
    },
    {
        "name":        "Melt Ice Cream",
        "address":     "1201 W Magnolia Ave Ste 115, Fort Worth, TX 76104",
        "type":        "Ice Cream Shop",
        "description": "My first official job, and I had the chance to work with my closest friends who I am still in contact with today.",
        "image_url":   "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRHdZKnRIRxGxUJVqZ6N9e3Q6Bj8A5Zeopz5Q&s",
    },
    {
        "name":        "Terra Mediterranean",
        "address":     "2932 Crockett St, Fort Worth, TX 76107",
        "type":        "Restaurant",
        "description": "This is my mom's favorite restaurant, and my older sister worked here when I was younger. I love Mediterranean food.",
        "image_url":   "https://i0.wp.com/fortworthreport.org/wp-content/uploads/2024/12/terra-mediterranean.jpg?resize=1200%2C788&quality=89&ssl=1",
    },
    {
        "name":        "Rockwood Go Kart Racing",
        "address":     "700 N University Dr, Fort Worth, TX 76114",
        "type":        "Go Kart Racing",
        "description": "My brother and I used to love going race car driving when we were younger. I have many memories at this place.",
        "image_url":   "https://lh3.googleusercontent.com/p/AF1QipMRFZOdmz3fbh8XGiCNXx9rkhW4cgCWsHmhTUJ9=s1360-w1360-h1020-rw",
    },
    {
        "name":        "Braum's Ice Cream",
        "address":     "2509 8th Ave, Fort Worth, TX 76110",
        "type":        "Ice Cream Shop",
        "description": "I have vivid memories of getting birthday cake ice cream at this Braum's after school in Kindergarten. The only flavor I ever get here is birthday cake.",
        "image_url":   "https://lh3.googleusercontent.com/gps-cs-s/AHVAwerhrxGRqZ4mGFfAAzepZozaYsF2WThCZkKEacZUyJKoYxJYn9YszNq5b-odv8oDCgAIKhmRsOWfqnSjA7ye3hfD4vU_2l_btfEgfvNL2yU2kzqAInFxlZeNHauPdhFFmyiIoeoodw=s1360-w1360-h1020-rw",
    },
    {
        "name":        "Arts 5th Avenue",
        "address":     "1628 5th Ave, Fort Worth, TX 76104",
        "type":        "Art Studio",
        "description": "I used to perform at this location. My middle school would use this space for our theater performances.",
        "image_url":   "https://lh3.googleusercontent.com/gps-cs-s/AHVAwerprOCrUQdU7UYgRCt5-M4Hm8zdwjZDXHuzM_o3aot-FQhwmltBdyygKSY5bcY8o-sQtECZDbiaD5LSZLa15CS_MP-mlnIprDbw7O0FptAGvvp4mRSIgAoD5bKysimwLppIivyNzA=w289-h156-n-k-no",
    },
    {
        "name":        "Casa Azul Coffee",
        "address":     "300 W Central Ave, Fort Worth, TX 76164",
        "type":        "Coffee Shop",
        "description": "My sister's good friend owns this coffee shop. It has great coffee and unique drinks inspired by the Latino community.",
        "image_url":   "https://lh3.googleusercontent.com/p/AF1QipOFGcerhxs2lRcdLr0iqx0ld0yqYR7WdgQPBEEn=s1360-w1360-h1020-rw",
    },
    {
        "name":        "Scat Jazz Lounge",
        "address":     "111 W 4th St #11, Fort Worth, TX 76102",
        "type":        "Jazz Lounge",
        "description": "This is a really fun location in Fort Worth. They have great music and my friends and I love going here.",
        "image_url":   "https://lh3.googleusercontent.com/p/AF1QipM2Ss9V5-pSArX558sdUOw8h9ZFC4Zq2mJCcIxi=w243-h174-n-k-no-nu",
    },
]

# ─────────────────────────────────────────────
# MARKER STYLES per location type
# ─────────────────────────────────────────────
TYPE_STYLES = {
    "School":         {"color": "#4A90D9", "icon": "graduation-cap", "prefix": "fa"},
    "Restaurant":     {"color": "#E8472A", "icon": "cutlery",        "prefix": "fa"},
    "Museum":         {"color": "#9B59B6", "icon": "institution",    "prefix": "fa"},
    "Ice Cream Shop": {"color": "#F39C12", "icon": "star",           "prefix": "fa"},
    "Go Kart Racing": {"color": "#27AE60", "icon": "flag",           "prefix": "fa"},
    "Art Studio":     {"color": "#E91E8C", "icon": "paint-brush",    "prefix": "fa"},
    "Coffee Shop":    {"color": "#795548", "icon": "coffee",         "prefix": "fa"},
    "Jazz Lounge":    {"color": "#1ABC9C", "icon": "music",          "prefix": "fa"},
}
DEFAULT_STYLE = {"color": "#7F8C8D", "icon": "map-marker", "prefix": "fa"}


# ─────────────────────────────────────────────
# CSV PARSER  (handles the transposed layout)
# ─────────────────────────────────────────────
def load_csv(filepath: str):
    """
    The CSV has locations as *columns* across 5 rows:
        Row 0 – names
        Row 1 – addresses
        Row 2 – types
        Row 3 – descriptions
        Row 4 – image URLs
    Returns a list of location dicts.
    """
    path = Path(filepath)
    if not path.exists():
        print(f"[CSV] '{filepath}' not found – using built-in data.")
        return DEFAULT_LOCATIONS

    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    if len(rows) < 5:
        print("[CSV] Unexpected format – using built-in data.")
        return DEFAULT_LOCATIONS

    names       = rows[0]
    addresses   = rows[1]
    types       = rows[2]
    descriptions= rows[3]
    images      = rows[4]
    num_cols    = len(names)

    locations = []
    for i in range(num_cols):
        locations.append({
            "name":        names[i].strip(),
            "address":     addresses[i].strip(),
            "type":        types[i].strip(),
            "description": descriptions[i].strip(),
            "image_url":   images[i].strip(),
        })
    return locations


# ─────────────────────────────────────────────
# GEOCODING  via Mapbox Geocoding API
# ─────────────────────────────────────────────
def geocode(address: str):
    """
    Returns (latitude, longitude) for a given address string,
    or None if the request fails.
    """
    url = "https://api.mapbox.com/geocoding/v5/mapbox.places/" \
          + requests.utils.quote(address) + ".json"
    params = {
        "access_token": MAPBOX_TOKEN,
        "limit": 1,
        "country": "us",
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        features = data.get("features", [])
        if features:
            lon, lat = features[0]["geometry"]["coordinates"]
            return lat, lon
    except Exception as e:
        print(f"  [Geocode error] {address}: {e}")
    return None


# ─────────────────────────────────────────────
# POP-UP HTML TEMPLATE
# ─────────────────────────────────────────────
def build_popup(loc: dict) -> str:
    """
    Builds a styled HTML string for the Folium pop-up.
    """
    style = TYPE_STYLES.get(loc["type"], DEFAULT_STYLE)
    accent = style["color"]
    return f"""
    <div style="
        font-family: 'Georgia', serif;
        width: 280px;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.18);
        background: #fff;
    ">
      <!-- Image -->
      <div style="
          width: 100%;
          height: 160px;
          background: #eee url('{loc['image_url']}') center/cover no-repeat;
      "></div>

      <!-- Content -->
      <div style="padding: 14px 16px 16px;">
        <!-- Type badge -->
        <span style="
            display: inline-block;
            background: {accent};
            color: #fff;
            font-size: 10px;
            font-family: 'Arial', sans-serif;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            padding: 3px 8px;
            border-radius: 20px;
            margin-bottom: 8px;
        ">{loc['type']}</span>

        <!-- Name -->
        <h3 style="
            margin: 0 0 8px 0;
            font-size: 17px;
            color: #1a1a1a;
            line-height: 1.3;
        ">{loc['name']}</h3>

        <!-- Description -->
        <p style="
            margin: 0;
            font-size: 13px;
            color: #555;
            line-height: 1.6;
            font-family: 'Arial', sans-serif;
        ">{loc['description']}</p>
      </div>
    </div>
    """


# ─────────────────────────────────────────────
# LEGEND HTML
# ─────────────────────────────────────────────
def build_legend() -> str:
    items = ""
    for type_name, style in TYPE_STYLES.items():
        items += f"""
        <div style="display:flex; align-items:center; margin-bottom:6px;">
          <div style="
              width:14px; height:14px; border-radius:50%;
              background:{style['color']}; margin-right:8px; flex-shrink:0;
          "></div>
          <span style="font-size:13px; color:#333;">{type_name}</span>
        </div>"""
    return f"""
    <div style="
        position: fixed;
        bottom: 40px; right: 20px; z-index: 1000;
        background: rgba(255,255,255,0.95);
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        font-family: Arial, sans-serif;
        min-width: 170px;
        border: 1px solid #e0e0e0;
    ">
      <p style="margin:0 0 10px 0; font-weight:700; font-size:13px;
                color:#111; letter-spacing:0.5px; text-transform:uppercase;">
        Location Types
      </p>
      {items}
    </div>
    """


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  Fort Worth Hometown Map Builder")
    print("=" * 55)

    # 1. Load locations
    locations = load_csv(CSV_FILE)
    print(f"\n✓ Loaded {len(locations)} locations from CSV\n")

    # 2. Geocode each address
    print("Geocoding addresses via Mapbox …")
    geocoded = []
    for loc in locations:
        print(f"  → {loc['name']} …", end=" ", flush=True)
        coords = geocode(loc["address"])
        if coords:
            loc["lat"], loc["lon"] = coords
            geocoded.append(loc)
            print(f"({coords[0]:.5f}, {coords[1]:.5f})")
        else:
            print("FAILED – skipping")
        time.sleep(0.15)   # be polite to the API

    if not geocoded:
        print("\n✗  No locations were geocoded. Check your Mapbox token.")
        return

    print(f"\n✓ Geocoded {len(geocoded)} / {len(locations)} locations\n")

    # 3. Compute map centre
    avg_lat = sum(l["lat"] for l in geocoded) / len(geocoded)
    avg_lon = sum(l["lon"] for l in geocoded) / len(geocoded)

    # 4. Build Folium map with Mapbox basemap
    m = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=13,
        tiles=MAPBOX_TILE_URL,
        attr=MAPBOX_ATTRIBUTION,
        control_scale=True,
    )

    # 5. Add markers
    for loc in geocoded:
        style = TYPE_STYLES.get(loc["type"], DEFAULT_STYLE)

        icon = folium.Icon(
            color="white",
            icon_color=style["color"],
            icon=style["icon"],
            prefix=style["prefix"],
        )

        popup_html = build_popup(loc)
        popup = folium.Popup(
            folium.IFrame(popup_html, width=300, height=310),
            max_width=310,
        )

        folium.Marker(
            location=[loc["lat"], loc["lon"]],
            popup=popup,
            tooltip=f"<b>{loc['name']}</b><br><i>{loc['type']}</i>",
            icon=icon,
        ).add_to(m)

    # 6. Add legend
    m.get_root().html.add_child(folium.Element(build_legend()))

    # 7. Add a title banner
    title_html = """
    <div style="
        position: fixed; top: 16px; left: 50%; transform: translateX(-50%);
        z-index: 1000; background: rgba(255,255,255,0.95);
        border-radius: 30px; padding: 10px 28px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        font-family: Georgia, serif; text-align: center;
        border: 1px solid #e0e0e0;
    ">
      <span style="font-size:20px; font-weight:700; color:#1a1a1a;">
        📍 My Fort Worth
      </span>
      <span style="font-size:13px; color:#666; margin-left:10px;
                   font-family:Arial,sans-serif;">
        10 meaningful places
      </span>
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    # 8. Save
    m.save(OUTPUT_FILE)
    print(f"✓ Map saved to  →  {OUTPUT_FILE}")
    print("\nOpening in your browser …")
    webbrowser.open(OUTPUT_FILE)


if __name__ == "__main__":
    main()
