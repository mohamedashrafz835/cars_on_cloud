from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import time

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # عشان أي يوزر يقدر يتصل
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OIL_THRESHOLD = 10000
BRAKE_THRESHOLD = 20000

time.sleep(5)  # عشان DB يشتغل كويس

# 🔹 Database connection
conn = psycopg2.connect(
    host="db",
    database="carsdb",
    user="postgres",
    password="postgres"
)

# 🔹 Serve HTML Front-end
@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Car Maintenance Portal</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body { background-color: #f0f4f8; font-family: Arial, sans-serif; }
.container { margin-top: 50px; max-width: 700px; }
.status-ok { color: green; font-weight: bold; }
.status-alert { color: red; font-weight: bold; }
table { background-color: white; }
</style>
</head>
<body>
<div class="container">
<h2 class="text-center mb-4">Car Maintenance Portal</h2>
<div class="mb-3">
<label for="vinInput" class="form-label">Enter VIN:</label>
<input type="text" class="form-control" id="vinInput" placeholder="e.g. ABC123">
</div>
<button class="btn btn-primary mb-4 w-100" id="getCarBtn">Get Car Data</button>
<table class="table table-striped table-bordered" id="carTable">
<thead class="table-dark">
<tr><th>Attribute</th><th>Value</th></tr>
</thead>
<tbody></tbody>
</table>
</div>
<script>
document.getElementById("getCarBtn").addEventListener("click", async () => {
    const vin = document.getElementById("vinInput").value.trim();
    if(!vin) return;
    try {
        const response = await fetch(`/car/${vin}`);
        if(!response.ok) { alert("Car not found!"); return; }
        const data = await response.json();
        const tbody = document.querySelector("#carTable tbody");
        tbody.innerHTML = "";
        for(const [key,value] of Object.entries(data)) {
            const tr = document.createElement("tr");
            const tdKey = document.createElement("td"); tdKey.textContent = key;
            const tdValue = document.createElement("td"); tdValue.textContent = value;
            if(key==="oil_status" || key==="brake_status")
                tdValue.className = value.includes("Change") ? "status-alert" : "status-ok";
            tr.appendChild(tdKey); tr.appendChild(tdValue);
            tbody.appendChild(tr);
        }
    } catch(err){ console.error(err); alert("Error fetching data from API."); }
});
</script>
</body>
</html>
"""

# 🔹 API endpoint
@app.get("/car/{vin}")
def get_car(vin: str):
    cur = conn.cursor()
    cur.execute("SELECT * FROM cars WHERE vin=%s", (vin,))
    car = cur.fetchone()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    vin, current_km, oil_last_km, brake_last_km = car
    oil_used = current_km - oil_last_km
    brake_used = current_km - brake_last_km
    return {
        "vin": vin,
        "current_km": current_km,
        "oil_km_used": oil_used,
        "brake_km_used": brake_used,
        "oil_status": "Change Oil" if oil_used > OIL_THRESHOLD else "Oil OK",
        "brake_status": "Change Brakes" if brake_used > BRAKE_THRESHOLD else "Brakes OK"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
