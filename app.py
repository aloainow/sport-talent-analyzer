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

def show_força_tests():
    st.title("💪 Testes de Força")
    
    st.info("Complete os testes de força abaixo. Realize cada teste conforme as instruções.")
    
    # Teste 1: Flexões
    with st.expander("Flexões de Braço", expanded=True):
        st.write("**Descrição:** Realize o máximo de flexões em 1 minuto")
        st.write("**Equipamento necessário:** Cronômetro")
        st.write("**Como realizar:**")
        st.write("""
        1. Posição inicial: prancha
        2. Desça o corpo mantendo alinhado
        3. Suba até estender os braços
        4. Conte repetições em 1 minuto
        """)
        st.write("**Classificação:**")
        st.write("""
        - Iniciante: 10-15 repetições
        - Intermediário: 16-25 repetições
        - Avançado: 26+ repetições
        """)
        flexoes = st.number_input("Número de flexões", min_value=0, max_value=100)
    
    # Teste 2: Abdominais
    with st.expander("Abdominais", expanded=True):
        st.write("**Descrição:** Máximo de abdominais em 1 minuto")
        st.write("**Equipamento necessário:** Cronômetro, tapete")
        st.write("**Como realizar:**")
        st.write("""
        1. Deitado, joelhos flexionados
        2. Mãos na nuca
        3. Eleve o tronco até tocar joelhos
        4. Conte em 1 minuto
        """)
        st.write("**Classificação:**")
        st.write("""
        - Iniciante: 15-20 repetições
        - Intermediário: 21-30 repetições
        - Avançado: 31+ repetições
        """)
        abdominais = st.number_input("Número de abdominais", min_value=0, max_value=100)
    
    if st.button("Salvar Resultados"):
        st.session_state.test_results['força'] = {
            'flexoes': flexoes,
            'abdominais': abdominais
        }
        st.success("Resultados salvos com sucesso!")

def show_velocidade_tests():
    st.title("⚡ Testes de Velocidade")
    
    st.info("Complete os testes de velocidade abaixo. Realize cada teste conforme as instruções.")
    
    # Teste 1: Corrida 20m
    with st.expander("Corrida de 20m", expanded=True):
        st.write("**Descrição:** Tempo para percorrer 20 metros")
        st.write("**Equipamento necessário:** Cronômetro, fita métrica")
        st.write("**Como realizar:**")
        st.write("""
        1. Marque 20m em linha reta
        2. Posição inicial agachado
        3. Corra o mais rápido possível
        4. Registre o tempo
        """)
        corrida = st.number_input("Tempo (segundos)", min_value=0.0, max_value=20.0, step=0.1)
    
    # Teste 2: Agilidade
    with st.expander("Teste de Agilidade", expanded=True):
        st.write("**Descrição:** Corrida em zigue-zague entre 4 pontos")
        st.write("**Equipamento necessário:** 4 marcadores, cronômetro")
        st.write("**Como realizar:**")
        st.write("""
        1. Coloque 4 marcadores em quadrado (5m x 5m)
        2. Corra entre eles em zigue-zague
        3. Complete 2 voltas
        4. Registre o tempo
        """)
        agilidade = st.number_input("Tempo de agilidade (segundos)", min_value=0.0, max_value=30.0, step=0.1)
    
    if st.button("Salvar Resultados"):
        st.session_state.test_results['velocidade'] = {
            'corrida_20m': corrida,
            'agilidade': agilidade
        }
        st.success("Resultados salvos com sucesso!")


def show_resistencia_tests():
    st.title("🏃 Testes de Resistência")
    
    st.info("Complete os testes de resistência abaixo. Realize cada teste conforme as instruções.")
    
    # Teste 1: Burpee
    with st.expander("Teste de Burpee", expanded=True):
        st.write("**Descrição:** Máximo de burpees em 3 minutos")
        st.write("**Equipamento necessário:** Cronômetro")
        st.write("**Como realizar:**")
        st.write("""
        1. Em pé
        2. Agache e apoie as mãos
        3. Estenda as pernas
        4. Volte e salte
        5. Conte em 3 minutos
        """)
        st.write("**Classificação:**")
        st.write("""
        - Iniciante: 25-35 repetições
        - Intermediário: 36-50 repetições
        - Avançado: 51+ repetições
        """)
        burpees = st.number_input("Número de burpees", min_value=0, max_value=100)
    
    # Teste 2: Cooper Adaptado
    with st.expander("Teste de Cooper Adaptado", expanded=True):
        st.write("**Descrição:** Distância percorrida em 6 minutos")
        st.write("**Equipamento necessário:** Cronômetro, área para correr")
        st.write("**Como realizar:**")
        st.write("""
        1. Marque um percurso conhecido
        2. Corra/ande por 6 minutos
        3. Meça a distância total
        """)
        st.write("**Classificação:**")
        st.write("""
        - Iniciante: <1000m
        - Intermediário: 1000-1400m
        - Avançado: >1400m
        """)
        cooper = st.number_input("Distância (metros)", min_value=0, max_value=3000, step=50)
    
    if st.button("Salvar Resultados"):
        st.session_state.test_results['resistencia'] = {
            'burpees': burpees,
            'cooper': cooper
        }
        st.success("Resultados salvos com sucesso!")

def show_coordenacao_tests():
    st.title("🎯 Testes de Coordenação")
    
    st.info("Complete os testes de coordenação abaixo. Realize cada teste conforme as instruções.")
    
    # Teste 1: Equilíbrio
    with st.expander("Teste de Equilíbrio", expanded=True):
        st.write("**Descrição:** Tempo em equilíbrio em uma perna só")
        st.write("**Equipamento necessário:** Cronômetro")
        st.write("**Como realizar:**")
        st.write("""
        1. Fique em uma perna
        2. Olhos fechados
        3. Braços cruzados
        4. Meça o tempo até desequilibrar
        """)
        st.write("**Classificação:**")
        st.write("""
        - Iniciante: <20 segundos
        - Intermediário: 20-40 segundos
        - Avançado: >40 segundos
        """)
        equilibrio = st.number_input("Tempo (segundos)", min_value=0, max_value=120)
    
    # Teste 2: Saltos Alternados
    with st.expander("Saltos Alternados", expanded=True):
        st.write("**Descrição:** Coordenação de saltos em 30 segundos")
        st.write("**Equipamento necessário:** Cronômetro")
        st.write("**Como realizar:**")
        st.write("""
        1. Salte alternando pernas
        2. Toque joelho oposto
        3. Conte repetições em 30s
        """)
        st.write("**Classificação:**")
        st.write("""
        - Iniciante: <20 repetições
        - Intermediário: 20-30 repetições
        - Avançado: >30 repetições
        """)
        saltos = st.number_input("Número de saltos", min_value=0, max_value=100)
    
    if st.button("Salvar Resultados"):
        st.session_state.test_results['coordenacao'] = {
            'equilibrio': equilibrio,
            'saltos': saltos
        }
        st.success("Resultados salvos com sucesso!")

def show_recommendations():
    st.title("⭐ Suas Recomendações de Esportes")
    
    # Verificar se todos os testes foram completados
    test_categories = ['força', 'velocidade', 'resistencia', 'coordenacao']
    all_tests_completed = all(
        len(st.session_state.test_results.get(category, {})) > 0 
        for category in test_categories
    )
    
    if not all_tests_completed:
        st.warning("Por favor, complete todos os testes para receber suas recomendações!")
        return
    
    # Processar resultados e obter recomendações
    if 'recommendations' not in st.session_state or st.session_state.recommendations is None:
        with st.spinner("Analisando seus resultados..."):
            try:
                processed_results = process_test_results(st.session_state.test_results)
                st.session_state.recommendations = get_sport_recommendations(processed_results)
            except Exception as e:
                st.error(f"Erro ao processar recomendações: {str(e)}")
                return
    
    # Mostrar gráfico radar
    st.subheader("Seu Perfil de Habilidades")
    try:
        radar_chart = create_radar_chart(st.session_state.test_results)
        st.plotly_chart(radar_chart, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao criar gráfico: {str(e)}")
    
    # Mostrar recomendações
    st.subheader("Esportes Recomendados")
    
    if not st.session_state.recommendations:
        st.warning("Nenhuma recomendação disponível no momento.")
        return
        
    # Verificar formato das recomendações
    if isinstance(st.session_state.recommendations, list):
        for sport in st.session_state.recommendations:
            if isinstance(sport, dict) and 'name' in sport and 'compatibility' in sport:
                with st.expander(f"{sport['name']} - {sport['compatibility']}% compatível"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Pontos Fortes:**")
                        if 'strengths' in sport and isinstance(sport['strengths'], list):
                            for strength in sport['strengths']:
                                st.write(f"✓ {strength}")
                    
                    with col2:
                        st.write("**Áreas para Desenvolvimento:**")
                        if 'development' in sport and isinstance(sport['development'], list):
                            for area in sport['development']:
                                st.write(f"→ {area}")
            else:
                st.error("Formato de recomendação inválido")
    else:
        st.error("Formato de recomendações inválido")
    
    # Botões de ação
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Exportar Relatório"):
            st.info("Funcionalidade de exportação em desenvolvimento")
    
    with col2:
        if st.button("🔄 Recomeçar"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
            
def main():
    # Menu lateral
    with st.sidebar:
        selected = option_menu(
            "Menu Principal",
            ["Home", "Testes de Força", "Testes de Velocidade", "Testes de Resistência", "Testes de Coordenação", "Recomendações"],
            icons=['house', 'activity', 'bullseye', 'diagram-3', 'person', 'star'],
            menu_icon="cast",
            default_index=0,
        )
    
    # Conteúdo baseado na seleção do menu
    if selected == "Home":
        st.title("🏃‍♂️ Analisador de Talentos Esportivos")
        st.header("Bem-vindo ao Analisador de Talentos Esportivos!")
        
        # Informações Pessoais
        st.subheader("Informações Pessoais")
        with st.form("personal_info"):
            col1, col2 = st.columns(2)
            
            with col1:
                altura = st.number_input("Altura (cm)", min_value=0, max_value=300)
                peso = st.number_input("Peso (kg)", min_value=0, max_value=300)
                envergadura = st.number_input("Envergadura (cm)", min_value=0, max_value=300)
            
            with col2:
                idade = st.number_input("Idade", min_value=0, max_value=150)
                ano_nascimento = st.number_input("Ano de Nascimento", min_value=1900, max_value=2024)
            
            # Localização
            st.write("**Localização**")
            col3, col4, col5 = st.columns(3)
            
            with col3:
                cidade = st.text_input("Cidade")
            with col4:
                estado = st.text_input("Estado")
            with col5:
                pais = st.text_input("País")
            
            if st.form_submit_button("Salvar Informações"):
                st.session_state.personal_info = {
                    'altura': altura,
                    'peso': peso,
                    'envergadura': envergadura,
                    'idade': idade,
                    'ano_nascimento': ano_nascimento,
                    'cidade': cidade,
                    'estado': estado,
                    'pais': pais
                }
                st.success("Informações pessoais salvas com sucesso!")
        
        # Progresso dos Testes
        st.subheader("Seu Progresso")
        progress_data = {
            "Testes de Força": len(st.session_state.test_results['força']),
            "Testes de Velocidade": len(st.session_state.test_results['velocidade']),
            "Testes de Resistência": len(st.session_state.test_results['resistencia']),
            "Testes de Coordenação": len(st.session_state.test_results['coordenacao'])
        }
        
        for test, count in progress_data.items():
            progress = count / 2  # 2 testes por categoria
            st.progress(progress, text=f"{test}: {int(progress * 100)}%")
            
    elif selected == "Testes de Força":
        show_força_tests()
    elif selected == "Testes de Velocidade":
        show_velocidade_tests()
    elif selected == "Testes de Resistência":
        show_resistencia_tests()
    elif selected == "Testes de Coordenação":
        show_coordenacao_tests()
    elif selected == "Recomendações":
        show_recommendations()

if __name__ == "__main__":
    # Esconder menu hamburger e outros elementos do Streamlit
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)
    
    init_session_state()
    main()
