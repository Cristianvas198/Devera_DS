##########################################
#####            Librerias           #####
##########################################

from fastapi import FastAPI, HTTPException     
from pydantic import BaseModel                                                       
from src.agente_scrapping.utils import primer_scraping
from typing import Optional 
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.agente_co2.agent import agente
from src.agente_co2.db_utils import guardar_todo_en_db
from docxtpl import DocxTemplate
from firebase_admin import credentials, initialize_app, storage
import firebase_admin
from dotenv import load_dotenv
from uuid import uuid4
import re
import json
import tempfile
import os
import psycopg2
load_dotenv() # Iniciar el para el .env


# ---------------------------------------------------------------------------------------------------------------------

app = FastAPI()

origins = [
    "https://deveraai.netlify.app",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


cred_json = os.getenv("FIREBASE_CREDENTIALS")

# Manejo de error si está vacío
if not cred_json:
    raise ValueError("FIREBASE_CREDENTIALS is not set or is empty")

cred_dict = json.loads(cred_json)
cred = credentials.Certificate(cred_dict)

initialize_app(cred, {
    'storageBucket': 'deveraai.firebasestorage.app' 
})



# --------------------------------------------------------------------------------------------------------------------- 

class ScrapeRequest(BaseModel):           
    url: str     

class Producto(BaseModel):
    name: str
    href: str
    price: Optional[str] = None
    image: Optional[str] = None
                              
# --------------------------------------------------------------------------------------------------------------------- 

@app.get("/")
async def inicio():
    return {"message": "Hola, API está corriendo"}

# --------------------------------------------------------------------------------------------------------------------- 
@app.post("/scrapear")
async def scrapear_endpoint(body: ScrapeRequest):
    try:
        resultado_json_text = primer_scraping(body.url)  
        resultado_obj = json.loads(resultado_json_text)  
        return JSONResponse(content=resultado_obj)      
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------------------------------------------------------------------------------------------------- 

@app.post("/analizar_co2")
def calculo_co2(product_name: str, url_docs: str, id_brand:int):
    """
    Analiza el producto y devuelve el CO2 asociado, guardar en bbdd y generar .docx.
    """
    conn = psycopg2.connect(
        host=os.getenv("host"),
        database=os.getenv("database"),
        user=os.getenv("user"),
        password=os.getenv("password")
    )

    cursor = conn.cursor()
    cursor.execute("""
    SELECT id_products FROM products
    WHERE product_name = %s AND id_brand = %s
    """, (product_name, id_brand))
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="No se encontró un producto con ese nombre y marca.")

    id_products = row[0]

    cursor.execute("""
        UPDATE products_impacts_resume
        SET status = %s
        WHERE id_products = %s
    """, (
        'Processing',
        id_products
    ))

    conn.commit()
    conn.close()

    data = agente(url_docs, id_brand)

    # Convertir en JSON el STR
    json_str = re.search(r'\{.*\}', data, re.DOTALL)
    if not json_str:
        raise HTTPException(status_code=404, detail="No se encontró un JSON válido en el resultado")
    context = json.loads(json_str.group())

    # Redondear valores necesarios
    context["products_impacts_resume"]["co2_fingerprint"] = round(context["products_impacts_resume"]["co2_fingerprint"], 2)
    
    # Generar DOCX
    doc = DocxTemplate("./docs/plantilla_producto.docx")
    doc.render(context)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmpfile:
        doc.save(tmpfile.name)
        local_filename = tmpfile.name  # Ruta temporal

    # Subir a Firebase
    bucket = storage.bucket()
    blob_name = f"reports/Devera_{id_products}_{uuid4().hex}.docx"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_filename)
    blob.make_public()
    
    # Eliminar archivo local
    os.remove(local_filename)

    guardar_todo_en_db(context, id_products, blob.public_url)
    
    return context

