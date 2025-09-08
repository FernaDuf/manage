import os
import httpx
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, constr

SMARTOLT_SUBDOMAIN = os.getenv("SMARTOLT_SUBDOMAIN")  # p.ej. "tusubdominio"
SMARTOLT_TOKEN = os.getenv("SMARTOLT_API_TOKEN")

app = FastAPI(title="WiFi Password Changer Proxy")

class ChangeWifiBody(BaseModel):
    numero_cliente: int
    password: constr(min_length=8, max_length=63)  # WPA2/3 PSK 8..63

async def get_current_user():
    # TODO: integra tu auth (JWT/cookies). Aquí asumimos autenticado.
    return {"role": "customer"}

async def resolve_onu_external_id(numero_cliente: int) -> str:
    # TODO: consulta tu base (tabla clientes) para devolver el external_id de la ONU
    raise NotImplementedError("Implementa la resolución de ONU por cliente")

async def smartolt_request(method: str, url: str, json: dict | None = None):
    headers = {"X-Token": SMARTOLT_TOKEN}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.request(method, url, headers=headers, json=json)
        if r.status_code >= 400:
            raise HTTPException(status_code=502, detail={"smartolt": r.text})
        return r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text

@app.post("/wifi/change")
async def change_wifi(body: ChangeWifiBody, user = Depends(get_current_user)):
    if not SMARTOLT_SUBDOMAIN or not SMARTOLT_TOKEN:
        raise HTTPException(500, "Faltan variables SMARTOLT_SUBDOMAIN o SMARTOLT_API_TOKEN")

    onu_id = await resolve_onu_external_id(body.numero_cliente)

    url = f"https://{SMARTOLT_SUBDOMAIN}.smartolt.com/api/onu/zte/set_wifi"
    payload = {
        "onu_id": onu_id,
        "wifi": {
            "2.4g": {
                "password": body.password
            },
            "5g": {
                "password": body.password
            }
        }
    }

    resp = await smartolt_request("POST", url, json=payload)
    return {"status": "ok", "detail": resp}
