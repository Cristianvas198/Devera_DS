##########################################
#####            Librerias           #####
##########################################

import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
#----------------------------------------------------------------------------------------------------------------------------------
def guardar_todo_en_db(data, id_products, url_doc):
    conn = psycopg2.connect(
        host=os.getenv("host"),
        database=os.getenv("database"),
        user=os.getenv("user"),
        password=os.getenv("password")
    )
    
    cursor = conn.cursor()

    # Actualizar tabla products
    product = data["products"]
    cursor.execute("""
        UPDATE products
        SET total_weight = %s,
            transporting_distance = %s,
            pct_recycling = %s,
            transporting_type = %s
        WHERE id_products = %s
    """, (
        product["total_weight"],
        product["transporting_distance"],
        product["pct_recycling"],
        product["transporting_type"],
        id_products
    ))

    # Insertar en products_processes
    for proc in data["products_processes"]:
        cursor.execute("""
            INSERT INTO products_processes (id_products, name_process, quantity_energy, country, type_consumption, quantity_water, co2_impact)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            id_products,
            proc["name_process"],
            proc["quantity_energy"],
            proc["country"],
            proc["type_consumption"],
            proc["quantity_water"],
            proc["co2_impact"]
        ))

    # Insertar en products_materials
    for mat in data["products_materials"]:
        cursor.execute("""
            INSERT INTO products_materials (id_products, name_material, quantity, pct_recycling, pct_product, country, co2_impact)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            id_products,
            mat["name_material"],
            mat["quantity"],
            mat["pct_recycling"],
            mat["pct_product"],
            mat["country"],
            mat["co2_impact"]
        ))

    # Insertar en products_packing
    for pack in data["products_packing"]:
        cursor.execute("""
            INSERT INTO products_packing (id_products, packing_name, packing_weight, packing_material, pct_recycling, country, type_use)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            id_products,
            pack["packing_name"],
            pack["packing_weight"],
            pack["packing_material"],
            pack["pct_recycling"],
            pack["country"],
            pack["type_use"]
        ))

    # Insertar en products_impacts
    impacts = data["products_impacts"]
    cursor.execute("""
        INSERT INTO products_impacts (id_products, raw_materials, manufacturing, transport, packaging, product_use, end_of_life)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        id_products,
        impacts["raw_materials"],
        impacts["manufacturing"],
        impacts["transport"],
        impacts["packaging"],
        impacts["product_use"],
        impacts["end_of_life"]
    ))

    # Actualizar products_impacts_resume
    resumen = data["products_impacts_resume"]
    cursor.execute("""
        UPDATE products_impacts_resume
        SET co2_firgerprint = %s,
            pct_benchmark = %s,
            impact_score = %s,
            seal = %s,
            status = %s,
            product_pdf = %s
        WHERE id_products = %s
    """, (
        resumen["co2_fingerprint"],
        resumen["pct_benchmark"],
        resumen["impact_score"],
        resumen["seal"],
        'Completed',
        url_doc,
        id_products        
    ))

    conn.commit()
    conn.close()
    return "Data saved successfully"
