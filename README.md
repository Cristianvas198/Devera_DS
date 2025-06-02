# Devera - Dashboard de Impacto de Productos 🌍

## 📢 Introducción  
En Devera creemos que cualquier marca, sin importar su tamaño, debe poder medir, comparar y comunicar el impacto ambiental de sus productos. Para ello, automatizamos el **Análisis de Ciclo de Vida (ACV)** con inteligencia artificial y desarrollamos una **aplicación web** que transforma estos datos en valor real para el usuario.  

## 🚀 Objetivo  
Diseñar y desarrollar una aplicación web que permita a nuestros clientes vivir todo el recorrido Devera, desde compartir la información de sus productos hasta visualizar informes detallados con datos accionables.

## 🏆 El Reto  
Construir el **Dashboard de Impacto de Productos** más inteligente del mundo, proporcionando un flujo intuitivo y preciso de información:

### 🔄 Flujo del usuario  
1. **Onboarding inteligente**  
   - Un chatbot o asistente guiado ayuda al usuario a recopilar información de sus productos.  
   - Integración con web scraping para listar productos automáticamente.  
   - Posibilidad de subir información en diferentes formatos (PDF, Excel, Word).  

2. **Dashboard interactivo**  
   - Visualización de productos analizados con opciones de búsqueda y filtrado.  
   - Comparativas, gráficas de mercado y análisis detallados.  
   - Exportación de datos en formatos CSV y Excel.  

3. **Detalle completo de producto**  
   - Análisis modular con características clave del producto.  
   - Impacto ambiental detallado, incluyendo huella de carbono (CO₂).  
   - Generación automática de sellos de sostenibilidad y QR embebible.  

## 🔬 Implementación Técnica  
### 📊 Cálculo de huella de carbono  
La solución se basa en un **modelo de IA** que analiza el impacto ambiental siguiendo las normas **ISO 14040 y 14067**, usando factores estándar de conversión para energía, materiales y transporte.

### 🛠️ Tecnologías empleadas  
- **Procesamiento de documentos**: `PyPDFLoader`, `Docx2txtLoader`, `UnstructuredExcelLoader`.  
- **Vectorización semántica**: `FAISS` con `HuggingFaceEmbeddings`.  
- **Modelos de IA**: `LangChain`, `Gemini 2.0` para análisis avanzado.  
- **Bases de datos**: PostgreSQL, almacenamiento y actualización de impacto ambiental.  
- **API FastAPI**: Servicio para analizar productos y almacenar resultados.  

## 🔗 API Endpoints  
### `POST /analizar`  
Analiza el producto y devuelve el CO₂ asociado.  

#### **Ejemplo de uso**  
```bash
curl -X POST "https://tu-api.com/analizar" -d '{"id_products": 123, "url_docs": "https://documento.pdf"}'
```

## 📈 Contribuciones  
Si quieres mejorar esta plataforma, ¡eres bienvenido! Haz un fork del repositorio, envía pull requests y contribuye al desarrollo de la herramienta. 🚀  
