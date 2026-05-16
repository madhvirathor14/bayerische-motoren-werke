import pyTigerGraph as tg
import csv
from dotenv import load_dotenv

load_dotenv()

HOST  = "https://tg-c71f2e24-bcc8-42ca-9a0b-49a8766b50fa.tg-2635877100.i.tgcloud.io"
USER  = "madhvirathor14"
PASS  = "Sakshu@x098765"
GRAPH = "bmw_luxecar"

conn = tg.TigerGraphConnection(
    host=HOST, graphname=GRAPH,
    username=USER, password=PASS,
    tgCloud=True, restppPort=443, gsPort=443
)
conn.getToken(conn.createSecret())
print("Connected!")

# ── Load Cars ────────────────────────────────────────────────
print("\nLoading Cars...")
cars = []
with open("data/raw_documents/cars.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        cars.append({
            "car_id":            row["car_id"],
            "brand":             row["brand"],
            "horsepower":        int(row["horsepower"]),
            "price_usd":         int(row["price_usd"]),
            "top_speed":         int(row["top_speed"]),
            "engine_type":       row["engine_type"],
            "acceleration_0_60": float(row["acceleration_0_60"])
        })

result = conn.upsertVertices("Car", 
    [(c["car_id"], {k:v for k,v in c.items() if k != "car_id"}) for c in cars])
print(f"Cars loaded: {result}")

# ── Load Brands ──────────────────────────────────────────────
print("\nLoading Brands...")
brands = []
with open("data/raw_documents/brands.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        brands.append({
            "brand_name": row["brand_name"],
            "country":    row["country"],
            "founded":    int(row["founded"]),
            "specialty":  row["specialty"]
        })

result = conn.upsertVertices("Brand",
    [(b["brand_name"], {k:v for k,v in b.items() if k != "brand_name"}) for b in brands])
print(f"Brands loaded: {result}")

# ── Load Features ────────────────────────────────────────────
print("\nLoading Features...")
features = []
with open("data/raw_documents/features.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        features.append({
            "feature_name": row["feature_name"],
            "category":     row["category"],
            "description":  row["description"]
        })

result = conn.upsertVertices("Feature",
    [(ft["feature_name"], {k:v for k,v in ft.items() if k != "feature_name"}) for ft in features])
print(f"Features loaded: {result}")

# ── Load MANUFACTURES Edges ──────────────────────────────────
print("\nLoading MANUFACTURES edges...")
edges = []
with open("data/raw_documents/manufactures_edges.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        edges.append((row["from_brand"], row["to_car"], {}))

result = conn.upsertEdges("Brand", "MANUFACTURES", "Car", edges)
print(f"MANUFACTURES edges loaded: {result}")

# ── Load COMPETES_WITH Edges ─────────────────────────────────
print("\nLoading COMPETES_WITH edges...")
comp_edges = []
with open("data/raw_documents/competes_edges.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        comp_edges.append((row["from_car"], row["to_car"], {}))

result = conn.upsertEdges("Car", "COMPETES_WITH", "Car", comp_edges)
print(f"COMPETES_WITH edges loaded: {result}")

# ── Final Count ──────────────────────────────────────────────
print("\n" + "="*50)
print(f"Cars:     {conn.getVertexCount('Car')}")
print(f"Brands:   {conn.getVertexCount('Brand')}")
print(f"Features: {conn.getVertexCount('Feature')}")
print("ALL DATA LOADED SUCCESSFULLY!")
print("="*50)