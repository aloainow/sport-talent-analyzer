import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
from utils.openai_helper import get_sport_recommendations
from utils.test_processor import process_test_results
import json

# Configuração da página
st.set_page_config(
    page_title="Analisador de Talentos Esportivos",
    page_icon="🏃‍♂️",
    layout="wide"
)

# Inicialização do estado da sessão
def init_session_state():
    if 'test_results' not in st.session_state:
        st.session_state.test_results = {
            'physical': {},
            'technical': {},
            'tactical': {},
            'psychological': {}
        }
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None

init_session_state()

# Função para criar o gráfico radar
def create_radar_chart(results):
    categories = ['Físico', 'Técnico', 'Tático', 'Psicológico']
    values = [
        results.get('physical', {}).get('average', 0),
        results.get('technical', {}).get('average', 0),
        results.get('tactical', {}).get('average', 0),
        results.get('psychological', {}).get('average', 0)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # Fechando o polígono
        theta=categories + [categories[0]],  # Fechando o polígono
        fill='toself',
        name='Seu Perfil'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=False
    )
    
    return fig

# Interface principal
def main():
    # Cabeçalho
    st.title("🏃‍♂️ Analisador de Talentos Esportivos")
    
    # Menu lateral
    with st.sidebar:
        selected = option_menu(
            "Menu Principal",
            ["Home", "Testes Físicos", "Testes Técnicos", "Testes Táticos", "Testes Psicológicos", "Recomendações"],
            icons=['house', 'activity', 'bullseye', 'diagram-3', 'person', 'star'],
            menu_icon="cast",
            default_index=0,
        )
    
    # Página inicial
    if selected == "Home":
        st.header("Bem-vindo ao Analisador de Talentos Esportivos!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Como Funciona")
            st.write("""
            1. Complete os testes em cada categoria
            2. Nosso sistema analisa seus resultados
            3. Receba recomendações personalizadas de esportes
            """)
            
            if st.button("Começar Avaliação", type="primary"):
                st.switch_page("pages/01_physical_tests.py")
        
        with col2:
            st.subheader("Seu Progresso")
            progress_data = {
                "Testes Físicos": len(st.session_state.test_results['physical']),
                "Testes Técnicos": len(st.session_state.test_results['technical']),
                "Testes Táticos": len(st.session_state.test_results['tactical']),
                "Testes Psicológicos": len(st.session_state.test_results['psychological'])
            }
            
            for test, count in progress_data.items():
                progress = count / 5  # Assumindo 5 testes por categoria
                st.progress(progress, text=f"{test}: {int(progress * 100)}%")
    
    # Recomendações
    elif selected == "Recomendações":
        if all(len(v) > 0 for v in st.session_state.test_results.values()):
            if st.session_state.recommendations is None:
                with st.spinner("Processando seus resultados..."):
                    # Processar resultados dos testes
                    processed_results = process_test_results(st.session_state.test_results)
                    
                    # Obter recomendações via OpenAI
                    st.session_state.recommendations = get_sport_recommendations(processed_results)
            
            # Mostrar resultados
            st.header("Suas Recomendações de Esportes")
            
            # Mostrar gráfico radar
            st.subheader("Seu Perfil")
            radar_chart = create_radar_chart(st.session_state.test_results)
            st.plotly_chart(radar_chart, use_container_width=True)
            
            # Mostrar recomendações
            st.subheader("Esportes Recomendados")
            for sport in st.session_state.recommendations:
                with st.expander(f"{sport['name']} - {sport['compatibility']}% compatível"):
                    st.write("**Pontos Fortes:**")
                    for strength in sport['strengths']:
                        st.write(f"- {strength}")
                    
                    st.write("\n**Áreas para Desenvolvimento:**")
                    for area in sport['development']:
                        st.write(f"- {area}")
        else:
            st.warning("Complete todos os testes para receber suas recomendações!")
            if st.button("Ir para Testes"):
                st.switch_page("pages/01_physical_tests.py")

if __name__ == "__main__":
    main()
