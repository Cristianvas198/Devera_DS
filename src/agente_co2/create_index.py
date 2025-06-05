##########################################
#####            Librerias           #####
##########################################

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

#----------------------------------------------------------------------------------------------------------------------------------
def load_documents_from_folder(folder_path: str):
    '''
    Funcion que unifica los archivos de una carpeta en un archivo.
    
    Input:
        folder_path:str
    
    Output:
        all_documents
    '''
    all_documents = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if filename.lower().endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif filename.lower().endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        elif filename.lower().endswith(".xlsx"):
            loader = UnstructuredExcelLoader(file_path)
        elif filename.lower().endswith(".xls"):
            loader = UnstructuredExcelLoader(file_path)            
        else:
            print(f"Archivo ignorado (tipo no soportado): {filename}")
            continue

        try:
            docs = loader.load()
            all_documents.extend(docs)
            print(f"Cargado: {filename} ({len(docs)} documentos)")
        except Exception as e:
            print(f"Error al cargar {filename}: {e}")

    return all_documents

#----------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    documents = load_documents_from_folder("./docs/entrenamiento")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs_chunked = text_splitter.split_documents(documents)

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2") 
    faiss_vectorstore = FAISS.from_documents(docs_chunked, embedding_model)
    faiss_vectorstore.save_local("src/agente_co2/faiss_index_co2")

print('Base de datos creada.')

