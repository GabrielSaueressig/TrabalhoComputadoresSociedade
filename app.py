import base64

import streamlit as st

import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

#Transforma o pdf em uma string
@st.cache_data
def pdf_to_text(pdf):
    pdf = fitz.open(filetype="pdf", stream=pdf)
    text = []
    for page in pdf:
        text.append(page.get_text())

    return "".join(text)

#separa a string em pedaços menores de 1000 caracteres cada e retorna um documento com esse pedaço + o nome do documento
def create_chunk(text, document_name):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 150
    )
    chunk = text_splitter.create_documents([text], metadatas=[{"source": document_name}])
    return chunk

#Cria os Embeddings utilizando a IA do google
def create_vectors(chunks):
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")   
        vector_store = FAISS.from_documents(chunks, embeddings)
        return vector_store
    except Exception as e:
        st.error(f"Erro ao Criar Banco de Vetores: {e}")
        return None

# Configuração base da página
st.set_page_config(
    page_title="JuridicAI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilos customizados para remover espaços excessivos e ajustar layout
with open("src/ui/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(
    """
    <style>
        /* Reduz o espaço no topo da página do Streamlit */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Ajuste fino para o título */
        .title-container {
            margin-top: -20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Layout Principal: Header e Logo
col_logo, col_title = st.columns([1, 15])
with col_logo:
    st.markdown(
        "<h1 style='color: #007BFF; font-size: 2.5rem; margin-top: 0;'>⚖️</h1>",
        unsafe_allow_html=True,
    )
with col_title:
    st.markdown(
        "<h2 style='margin-bottom: 0px; margin-top: 5px;'>JuridicAI</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size: 1rem; margin-top: -10px; color: #888;'>Tradução inteligente de documentos jurídicos complexos.</p>",
        unsafe_allow_html=True,
    )

st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

# Inicialização do estado para mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

# Layout de Colunas: Esquerda (Documentos) | Direita (Chat)
col_doc, col_chat = st.columns([1.1, 1])

# Altura para o Chat (Mais comprido que o PDF para melhor experiência)
CHAT_HEIGHT = 800
PDF_HEIGHT = 700

with col_doc:
    st.markdown("### 📂 Documentos")
    uploaded_files = st.file_uploader(
        "Upload de PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        #Guardando temporariamente os arquivos na cache
        if "vector_db" not in st.session_state:
            st.session_state.vector_db = None 
        if "processed_arquives" not in st.session_state:
            st.session_state.processed_arquives = []
            
        file_names = [f.name for f in uploaded_files]
        selected_file_name = st.selectbox("Visualizando:", file_names)
        selected_file = next(f for f in uploaded_files if f.name == selected_file_name)
        
        #Salvando os bytes do pdf e mostrando na tela
        pdf_bytes = selected_file.read()
        selected_file.seek(0)
        base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        
        #Se ja nao estive na cache, le o texto, separa o chunk e salva na cache
        if selected_file.name not in st.session_state.processed_arquives:
            pdf_text = pdf_to_text(pdf_bytes)
            st.session_state.processed_arquives.append(selected_file.name)

            new_chunk = create_chunk(pdf_text, selected_file.name)
            if "total_chunks" not in st.session_state:
                st.session_state.total_chunks = []
            st.session_state.total_chunks.extend(new_chunk)
            st.session_state.needs_update = True
        
        #Verifica se Tem novas atualizações nos chuks, caso tenha usa a função pra criar o vetor de significancia e salva na cache
        if st.session_state.get("needs_update", False) and st.session_state.total_chunks:
            with st.spinner("Sincronizando base de dados"):
                st.session_state.vector_db = create_vectors(st.session_state.total_chunks)
            st.session_state.needs_update = False
        
            

        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="{PDF_HEIGHT}px" style="border-radius: 8px; border: 1px solid #333;"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.info("Carregue seus arquivos PDF para começar.")
        st.image(
            "https://img.freepik.com/free-vector/upload-concept-illustration_114360-1205.jpg",
            width=280,
        )

with col_chat:
    st.markdown("### 💬 Assistente")

    # Container do Chat mais comprido
    chat_container = st.container(height=CHAT_HEIGHT)

    with chat_container:
        if not st.session_state.messages:
            st.chat_message("assistant").write(
                "Olá! Sou o JuridicAI. Carregue seus documentos ao lado e eu te ajudarei a entender cada cláusula ou resumir o conteúdo."
            )

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Input de chat
    input_disabled = not uploaded_files
    placeholder_text = (
        "Pergunte algo sobre os documentos..."
        if uploaded_files
        else "Envie um documento primeiro"
    )

    if user_input := st.chat_input(placeholder_text, disabled=input_disabled):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                if len(uploaded_files) > 1:
                    response = "Analisando os múltiplos documentos carregados... Identifiquei os pontos chave para sua pergunta."
                else:
                    response = "Analisando o documento... Estou pronto para explicar os termos jurídicos para você."

                st.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

    if st.session_state.messages:
        st.button(
            "Limpar conversa",
            on_click=lambda: st.session_state.update({"messages": []}),
            type="secondary",
        )
