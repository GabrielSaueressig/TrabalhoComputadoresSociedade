import streamlit as st

# Configuração base da página
st.set_page_config(
    page_title="JuridicAI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos customizados carregados de forma modular
with open("src/ui/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Layout Principal: Header e Logo
col_logo, col_title = st.columns([1, 11])
with col_logo:
    st.markdown(
        "<h1 style='color: #007BFF; font-size: 3rem;'>⚖️</h1>", unsafe_allow_html=True
    )
with col_title:
    st.markdown(
        "<h1 style='margin-bottom: 0px;'>JuridicAI</h1>", unsafe_allow_html=True
    )
    st.markdown(
        "<p style='font-size: 1.2rem; margin-top: -10px;'>Tradução inteligente de documentos jurídicos complexos.</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# Sidebar estilizada
with st.sidebar:
    st.markdown("<h2 style='color: #007BFF;'>Navegação</h2>", unsafe_allow_html=True)
    opcao = st.radio(
        "",
        ["📂 Adicionar Documentos", "💬 Assistente / Chat"],
        label_visibility="collapsed",
    )

# Área de Conteúdo
if opcao == "📂 Adicionar Documentos":
    st.markdown("### 📥 Nova Análise")
    st.markdown(
        "Arraste seus contratos, petições e processos para desmistificar o *juridiquês*."
    )

    with st.container():
        uploaded_file = st.file_uploader("Upload de PDF", type=["pdf"])
        if uploaded_file:
            st.success("Documento carregado com sucesso! Pronto para análise.")

elif opcao == "💬 Assistente / Chat":
    st.markdown("### 💬 Converse com o JuridicAI")
    st.markdown("Tire dúvidas sobre os documentos enviados de forma simples e direta.")

    # Mock visual de chat
    with st.container():
        st.info(
            "👋 Olá! Sou o JuridicAI. Sobre qual cláusula ou documento você quer falar hoje?"
        )
        user_input = st.chat_input("Digite sua dúvida aqui...")
        if user_input:
            st.warning("Função de chat será ativada em breve com LLM!")
