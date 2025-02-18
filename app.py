import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
from utils.openai_helper import get_sport_recommendations
from utils.test_processor import process_test_results

# Configuração da página - DEVE SER A PRIMEIRA CHAMADA STREAMLIT
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
        r=values + [values[0]],
        theta=categories + [categories[0]],
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

def show_physical_tests():
    st.header("Testes Físicos")
    with st.form("physical_tests_form"):
        st.number_input("Velocidade (segundos)", key="velocity")
        st.number_input("Força (repetições)", key="strength")
        st.number_input("Resistência (metros)", key="endurance")
        st.number_input("Agilidade (segundos)", key="agility")
        
        if st.form_submit_button("Salvar Resultados"):
            st.session_state.test_results['physical'] = {
                'velocity': st.session_state.velocity,
                'strength': st.session_state.strength,
                'endurance': st.session_state.endurance,
                'agility': st.session_state.agility
            }
            st.success("Resultados salvos com sucesso!")

def show_technical_tests():
    st.header("Testes Técnicos")
    with st.form("technical_tests_form"):
        st.number_input("Coordenação (0-10)", key="coordination", min_value=0, max_value=10)
        st.number_input("Equilíbrio (segundos)", key="balance")
        st.number_input("Precisão (0-10)", key="precision", min_value=0, max_value=10)
        
        if st.form_submit_button("Salvar Resultados"):
            st.session_state.test_results['technical'] = {
                'coordination': st.session_state.coordination,
                'balance': st.session_state.balance,
                'precision': st.session_state.precision
            }
            st.success("Resultados salvos com sucesso!")

def show_tactical_tests():
    st.header("Testes Táticos")
    with st.form("tactical_tests_form"):
        st.slider("Tomada de Decisão (0-10)", min_value=0, max_value=10, key="decision_making")
        st.slider("Visão de Jogo (0-10)", min_value=0, max_value=10, key="game_vision")
        
        if st.form_submit_button("Salvar Resultados"):
            st.session_state.test_results['tactical'] = {
                'decision_making': st.session_state.decision_making,
                'game_vision': st.session_state.game_vision
            }
            st.success("Resultados salvos com sucesso!")

def show_psychological_tests():
    st.header("Testes Psicológicos")
    with st.form("psychological_tests_form"):
        attributes = ["Motivação", "Trabalho em Equipe", "Liderança", 
                     "Resiliência", "Concentração", "Competitividade"]
        results = {}
        
        for attr in attributes:
            key = attr.lower().replace(" ", "_")
            results[key] = st.slider(f"{attr} (0-10)", min_value=0, max_value=10, key=key)
        
        if st.form_submit_button("Salvar Resultados"):
            st.session_state.test_results['psychological'] = results
            st.success("Resultados salvos com sucesso!")

def main():
    # Menu lateral
    with st.sidebar:
        selected = option_menu(
            "Menu Principal",
            ["Home", "Testes Físicos", "Testes Técnicos", "Testes Táticos", "Testes Psicológicos", "Recomendações"],
            icons=['house', 'activity', 'bullseye', 'diagram-3', 'person', 'star'],
            menu_icon="cast",
            default_index=0,
        )
    
    # Conteúdo baseado na seleção do menu
    if selected == "Home":
        st.title("🏃‍♂️ Analisador de Talentos Esportivos")
        st.header("Bem-vindo ao Analisador de Talentos Esportivos!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Como Funciona")
            st.write("""
            1. Complete os testes em cada categoria
            2. Nosso sistema analisa seus resultados
            3. Receba recomendações personalizadas de esportes
            """)
            
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
    
    elif selected == "Testes Físicos":
        show_physical_tests()
    elif selected == "Testes Técnicos":
        show_technical_tests()
    elif selected == "Testes Táticos":
        show_tactical_tests()
    elif selected == "Testes Psicológicos":
        show_psychological_tests()
    elif selected == "Recomendações":
        if all(len(v) > 0 for v in st.session_state.test_results.values()):
            if st.session_state.recommendations is None:
                with st.spinner("Processando seus resultados..."):
                    processed_results = process_test_results(st.session_state.test_results)
                    st.session_state.recommendations = get_sport_recommendations(processed_results)
            
            st.header("Suas Recomendações de Esportes")
            st.subheader("Seu Perfil")
            radar_chart = create_radar_chart(st.session_state.test_results)
            st.plotly_chart(radar_chart, use_container_width=True)
            
            st.subheader("Esportes Recomendados")
            if isinstance(st.session_state.recommendations, list):
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

if __name__ == "__main__":
    # Esconder menu hamburger e outros elementos do Streamlit
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)
    
    main()
