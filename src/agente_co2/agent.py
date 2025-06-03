##########################################
#####            Librerias           #####
##########################################

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import tempfile
import requests
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredExcelLoader, CSVLoader
import os
import psycopg2
from urllib.parse import urlparse

#----------------------------------------------------------------------------------------------------------------------------------

load_dotenv() # Iniciar el para el .env

#----------------------------------------------------------------------------------------------------------------------------------
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
Eres un analista ambiental experto en cálculo de huella de carbono (CO₂) según las normas ISO 14040 y 14067. Con base en el siguiente documento de producto, devuelve los campos de JSON detallados y calcula el CO₂ para cada etapa del ciclo de vida.

Haz estimaciones de CO₂ usando los siguientes factores estándar:
- 0.233 kg CO₂/kWh para electricidad
- 0.12 kg CO₂/ton-km para camión
- 1 kg CO₂/kg para materiales vírgenes
- 0.3 kg CO₂/kg para materiales reciclados
- 0.05 kg CO₂/L para agua

Letras de seal: Se asignan según impact_score.
81–100 puntos → A
61–80 puntos → B
41–60 puntos → C
21–40 puntos → D
0–20 puntos → E

### FORMATO DE SALIDA (JSON estructurado):

{{
  "products": {{
    "total_weight": <float>,
    "transporting_distance": <float>,
    "pct_recycling": <float>,
    "transporting_type": "<camión|tren|avión|otro>"
  }},
  "products_processes": [
    {{
      "name_process": "<nombre>",
      "quantity_energy": <float>,
      "country": "España",
      "type_consumption": "eléctrico",
      "quantity_water": <float>,
      "co2_impact": <float>
    }}
  ],
  "products_materials": [
    {{
      "name_material": "<nombre>",
      "quantity": <float>,
      "pct_recycling": <float>,
      "pct_product": <float>,
      "country": "España",
      "co2_impact": <float>
    }}
  ],
  "products_packing": [
    {{
      "packing_name": "<nombre>",
      "packing_weight": <float>,
      "packing_material": "<material>",
      "pct_recycling": <float>,
      "country": "España",
      "type_use": "<primario|secundario>"
    }}
  ],
  "products_impacts": {{
    "raw_materials": <suma de co2_impact de todos los materiales>,
    "manufacturing":  <suma de co2_impact de los procesos>,
    "transport": < resultado de peso en toneladas * distancia * 0.12>,
    "packaging": <calculo del total estimado en base a peso packaging y % reciclaje>,
    "product_use": 0,
    "end_of_life": <estimación con base en % reciclaje>
  }},
  "products_impacts_resume": {{
    "co2_fingerprint": <suma de co2_impact de todos los procesos>,
    "pct_benchmark": <total>,
    "impact_score": <de 0 a 100 es 80 puntos de huella de carbono y 20 puntos de sostenibilidad de la marca, siguiendo criterios sociales y medioambientales.>,
    "seal": "<A|B|C|D|E>"
  }},
  "products_conclusions": {{
    "general_summary": "Redacta un párrafo introductorio (aprox. 4-6 líneas) explicando brevemente los principales hallazgos del ACV, el total de emisiones CO₂, y el posicionamiento ambiental del producto.",
    "strong_points": [
      "Escribe entre 2 y 4 frases describiendo fortalezas clave del producto, como uso de materiales naturales, procesos eficientes o bajo impacto logístico."
    ],
    "areas_for_improvement": [
      "Escribe entre 2 y 4 frases que sugieran mejoras posibles, como cambiar materiales, reducir consumo energético o mejorar reciclabilidad."
    ]
  }},
  "stage_analysis": {{
    "raw_materials": "<análisis técnico detallado de 800-1000 caracteres sobre impacto de materias primas y cómo mejorarlo>",
    "Manufacturing": "<análisis técnico detallado de 800-1000 caracteres sobre procesos de fabricación y oportunidades de eficiencia energética>",
    "Transport": "<análisis técnico sobre distancia, medio de transporte y mejoras posibles>",
    "Packaging": "<análisis técnico sobre los materiales usados en empaque y propuestas para mejora ambiental>",
    "Use Phase": "<análisis de impacto durante el uso (si aplica)>",
    "End of Life": "<análisis de impacto al final de vida útil y posibilidades de reciclaje o compostaje>"
  }}
}}

### CONTEXTO DEL PRODUCTO:
{context}

### PREGUNTA:
{question}

Instrucciones:
- Calcula todos los valores `co2_impact` como números.
- Devuelve únicamente un JSON estructurado válido. No agregues texto adicional ni explicaciones fuera del JSON.
"""
)

#----------------------------------------------------------------------------------------------------------------------------------

def load_documents_from_urls(urls: str):
    """
    Carga documentos desde URLs separadas por "|", los descarga, detecta su tipo y los carga.
    """
    all_documents = []
    url_list = [url.strip() for url in urls.split("|")]

    for url in url_list:
        try:
            # Descargar contenido
            response = requests.get(url)
            response.raise_for_status()  # Lanza excepción si el estado HTTP no es 200

            # Detectar extensión del archivo
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path).split("?")[0]  # remove query params
            file_ext = filename.split(".")[-1].lower()
            suffix = f".{file_ext}"

            # Guardar temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name

            # Detectar tipo de archivo y cargar
            if file_ext == "pdf":
                loader = PyPDFLoader(tmp_file_path)
            elif file_ext == "docx":
                loader = Docx2txtLoader(tmp_file_path)
            elif file_ext in ["xlsx", "xls"]:
                loader = UnstructuredExcelLoader(tmp_file_path)
            elif file_ext == "csv":
                loader = CSVLoader(file_path=tmp_file_path)
            else:
                print(f"Archivo ignorado (tipo no soportado): {url}")
                continue

            # Cargar documentos
            docs = loader.load()
            all_documents.extend(docs)
            print(f"Cargado: {url} ({len(docs)} documentos)")

        except Exception as e:
            print(f"Error al procesar {url}: {e}")

        finally:
            try:
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
            except Exception as cleanup_error:
                print(f"Error al borrar temporal: {cleanup_error}")

    return all_documents

#----------------------------------------------------------------------------------------------------------------------------------

def get_form_data_from_db(id_brand: int) -> str:
    conn = psycopg2.connect(
        host=os.getenv("host"),
        database=os.getenv("database"),
        user=os.getenv("user"),
        password=os.getenv("password")
    )
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
          company_name, 
          employees, 
          sustainability_report, 
          percent_renewable_sources, 
          plan_carbon_footprint, 
          percent_virgin_material, 
          distance_providers, 
          news_sustainability, 
          equality_plan, 
          wage_gap, 
          conciliation_measures, 
          enps_measurement, 
          proyectossociales, 
          otrainfo, 
          certificados
        FROM form
        WHERE id_brand = %s
    """, (id_brand,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return ""

    campos = [
        "Empresa", "Empleados", "Reporte Sostenibilidad", "% Energías Renovables",
        "Plan CO2", "% Material Virgen", "Distancia Proveedores", "Noticias Sostenibilidad",
        "Plan Igualdad", "Brecha Salarial", "Conciliación", "ENPS", "Proyectos Sociales",
        "Otra info", "Certificaciones"
    ]

    # Concatenar campo + valor
    return "\n".join(f"{campo}: {str(valor)}" for campo, valor in zip(campos, row) if valor)



#----------------------------------------------------------------------------------------------------------------------------------
def agente(folder_path:str, id_brand: int):
    api_key = os.getenv("gemini_api_key")

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local("src/agente_co2/faiss_index_co2", embedding_model, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={"k": 5}, search_type='mmr')

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt_template}
    )

    documents_product = load_documents_from_urls(folder_path)
    product_text_from_docs = " ".join([d.page_content for d in documents_product])

    product_text_from_form = get_form_data_from_db(id_brand)

    full_context = (
    "### FORMULARIO EMPRESA ###\n"
    + product_text_from_form +
    "\n\n### DOCUMENTACIÓN DEL PRODUCTO ###\n"
    + product_text_from_docs)

    prompt = prompt_template.format(
        context=full_context,
        question='Genera el JSON con el calculo total y detallado de emisiones de CO2 para el producto y con esto poblar las tablas SQL.'
    )

    resultado = qa_chain.run(prompt)
    return resultado



from fastapi import FastAPI, HTTPException, Request     
from pydantic import BaseModel                                                       
from typing import Optional 
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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

data =agente("https://firebasestorage.googleapis.com/v0/b/deveraai.firebasestorage.app/o/0a0f4834-9bf2-4134-9688-6c9559a9e353%2FLabial.pdf?alt=media&token=d622e6f4-7198-4f50-93b6-2046667e9309", 1)
print(data)

try:
    data =agente("https://firebasestorage.googleapis.com/v0/b/deveraai.firebasestorage.app/o/0a0f4834-9bf2-4134-9688-6c9559a9e353%2FLabial.pdf?alt=media&token=d622e6f4-7198-4f50-93b6-2046667e9309", 1)
    print(data)
    json_str = re.search(r'\{.*\}', data, re.DOTALL)
    print(json_str)
    if not json_str:
        raise HTTPException(status_code=404, detail="No se encontró un JSON válido en el resultado")
    context = json.loads(json_str.group())
    print(context)
    context["products_impacts_resume"]["co2_fingerprint"] = round(context["products_impacts_resume"]["co2_fingerprint"], 2)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error analizando CO2 o procesando JSON: {e}")