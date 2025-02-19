import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
from utils.openai_helper import get_sport_recommendations
from utils.test_processor import process_test_results, normalize_score, calculate_average

# Configuração da página
st.set_page_config(
    page_title="Analisador de Talentos Esportivos",
    page_icon="🏃‍♂️",
    layout="wide"
)

def reset_session_state():
    """Reseta completamente o estado da sessão"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Reinicializa com valores padrão
    st.session_state.test_results = {
        'dados_fisicos': {},
        'habilidades_tecnicas': {},
        'aspectos_taticos': {},
        'fatores_psicologicos': {}
    }
    st.session_state.recommendations = None
    st.session_state.personal_info = {}
    st.session_state.form_key = 0
    st.session_state.processed_scores = None
    st.session_state.initialized = True

# Inicialização do estado da sessão
def init_session_state():
    if 'test_results' not in st.session_state:
        st.session_state.test_results = {
            'dados_fisicos': {},
            'habilidades_tecnicas': {},
            'aspectos_taticos': {},
            'fatores_psicologicos': {}
        }
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    if 'personal_info' not in st.session_state:
        st.session_state.personal_info = {}
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0

def show_home():
    """Exibe a página inicial do aplicativo"""
    st.title("🏃‍♂️ Analisador de Talentos Esportivos")
    st.header("Bem-vindo ao Analisador de Talentos Esportivos!")
    
    # Informações Pessoais
    st.subheader("Informações Pessoais")
    form_key = f"personal_info_form_{st.session_state.form_key}"
    
    with st.form(key=form_key):
        col1, col2 = st.columns(2)
        
        with col1:
            altura = st.number_input(
                "Altura (cm)", 
                min_value=0, 
                max_value=300,
                value=st.session_state.personal_info.get('altura', 170),
                key=f"altura_{st.session_state.form_key}"
            )
            peso = st.number_input(
                "Peso (kg)", 
                min_value=0, 
                max_value=300,
                value=st.session_state.personal_info.get('peso', 70),
                key=f"peso_{st.session_state.form_key}"
            )
            envergadura = st.number_input(
                "Envergadura (cm)", 
                min_value=0, 
                max_value=300,
                value=st.session_state.personal_info.get('envergadura', 170),
                key=f"envergadura_{st.session_state.form_key}"
            )
        
        with col2:
            idade = st.number_input(
                "Idade", 
                min_value=0, 
                max_value=150,
                value=st.session_state.personal_info.get('idade', 25),
                key=f"idade_{st.session_state.form_key}"
            )
            ano_nascimento = st.number_input(
                "Ano de Nascimento", 
                min_value=1900, 
                max_value=2024,
                value=st.session_state.personal_info.get('ano_nascimento', 2000),
                key=f"ano_nascimento_{st.session_state.form_key}"
            )
        
        # Localização
        st.write("**Localização**")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            cidade = st.text_input(
                "Cidade",
                value=st.session_state.personal_info.get('cidade', ''),
                key=f"cidade_{st.session_state.form_key}"
            )
        with col4:
            estado = st.text_input(
                "Estado",
                value=st.session_state.personal_info.get('estado', ''),
                key=f"estado_{st.session_state.form_key}"
            )
        with col5:
            pais = st.text_input(
                "País",
                value=st.session_state.personal_info.get('pais', ''),
                key=f"pais_{st.session_state.form_key}"
            )
        
        submitted = st.form_submit_button("Salvar Informações")
        
        if submitted:
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
            st.session_state.form_key += 1
            st.success("Informações pessoais salvas com sucesso!")
    
    # Progresso dos Testes
    st.subheader("Seu Progresso")
    
    test_categories = {
        "Dados Físicos": 'dados_fisicos',
        "Habilidades Técnicas": 'habilidades_tecnicas',
        "Aspectos Táticos": 'aspectos_taticos',
        "Fatores Psicológicos": 'fatores_psicologicos'
    }
    
    for label, category in test_categories.items():
        progress = 1.0 if category in st.session_state.test_results and st.session_state.test_results[category] else 0.0
        st.progress(progress, text=f"{label}: {int(progress * 100)}%")
        

def create_radar_chart(scores):
    """Cria um gráfico radar com os scores processados."""
    categories = [
        'Dados Físicos', 
        'Habilidades Técnicas',
        'Aspectos Táticos', 
        'Fatores Psicológicos'
    ]
    
    values = [
        scores.get('dados_fisicos', 0),
        scores.get('habilidades_tecnicas', 0),
        scores.get('aspectos_taticos', 0),
        scores.get('fatores_psicologicos', 0)
    ]
    
    # Adiciona o primeiro valor novamente para fechar o polígono
    categories.append(categories[0])
    values.append(values[0])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Perfil do Atleta',
        line_color='#1f77b4',
        fillcolor='rgba(31, 119, 180, 0.5)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='%',
                tickmode='linear',
                tick0=0,
                dtick=20,
                showline=True,
                linewidth=1,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            angularaxis=dict(
                tickmode='array',
                ticktext=categories[:-1],  # Remove o valor duplicado
                tickvals=list(range(len(categories[:-1]))),
                direction='clockwise',
                gridcolor='rgba(0,0,0,0.1)'
            )
        ),
        showlegend=True,
        legend=dict(
            x=0.85,
            y=1.1
        ),
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig
def show_dados_fisicos():
    st.title("💪 Dados Físicos")
    
    st.info("Complete os testes físicos abaixo. Realize cada teste conforme as instruções.")
    
    # Teste de Velocidade
    with st.expander("Corrida de 20 metros", expanded=True):
        st.write("**Material necessário:** Fita métrica/trena, cronômetro, 2 marcadores")
        st.write("**Como realizar:**")
        st.write("""
        1. Marque 20 metros em linha reta
        2. Posição inicial em pé
        3. Corra o mais rápido possível
        4. Registre o tempo
        """)
        st.write("**Classificação:**")
        st.write("""
        - Iniciante: >4.0s
        - Intermediário: 3.5-4.0s
        - Avançado: <3.5s
        """)
        velocidade = st.number_input("Tempo (segundos)", min_value=0.0, max_value=10.0, step=0.1)
    
    # Força Superior
    with st.expander("Força Superior - Flexões", expanded=True):
        st.write("**Material necessário:** Cronômetro")
        st.write("**Como realizar:**")
        st.write("""
        1. Posição de prancha
        2. Execute flexões por 1 minuto
        3. Conte o número máximo de repetições
        """)
        st.write("**Classificação:**")
        st.write("""
        - Iniciante: 10-15 repetições
        - Intermediário: 16-25 repetições
        - Avançado: 26+ repetições
        """)
        forca_superior = st.number_input("Número de flexões", min_value=0, max_value=100)

    # Força Inferior
    with st.expander("Força Inferior - Agachamentos", expanded=True):
        st.write("**Material necessário:** Cronômetro")
        st.write("**Como realizar:**")
        st.write("""
        1. Posição em pé
        2. Execute agachamentos por 1 minuto
        3. Conte o número máximo de repetições
        """)
        st.write("**Classificação:**")
        st.write("""
        - Iniciante: 20-30 repetições
        - Intermediário: 31-40 repetições
        - Avançado: 41+ repetições
        """)
        forca_inferior = st.number_input("Número de agachamentos", min_value=0, max_value=100)
    
    if st.button("Salvar Dados Físicos"):
        st.session_state.test_results['dados_fisicos'] = {
            'velocidade': velocidade,
            'forca_superior': forca_superior,
            'forca_inferior': forca_inferior
        }
        st.success("Resultados salvos com sucesso!")

def show_habilidades_tecnicas():
    st.title("🎯 Habilidades Técnicas")
    
    st.info("Complete os testes técnicos abaixo. Realize cada teste conforme as instruções.")
    
    # Teste de Coordenação
    with st.expander("Coordenação - Pular Corda", expanded=True):
        st.write("**Material necessário:** Corda de pular, cronômetro")
        st.write("**Como realizar:**")
        st.write("""
        1. Posição inicial com corda
        2. Pule alternando os pés
        3. Conte alternâncias em 30 segundos
        """)
        st.write("**Classificação:**")
        st.write("""
        - Iniciante: <20 alternâncias
        - Intermediário: 20-30 alternâncias
        - Avançado: >30 alternâncias
        """)
        coordenacao = st.number_input("Número de alternâncias", min_value=0, max_value=100)
    
    # Teste de Precisão
    with st.expander("Precisão - Alvos", expanded=True):
        st.write("**Material necessário:** Bola pequena, alvos na parede")
        st.write("**Como realizar:**")
        st.write("""
        1. Marque alvos na parede
        2. Posicione-se a 3 metros
        3. Execute 10 tentativas
        """)
        st.write("**Classificação:**")
        st.write("""
        - Iniciante: 3-4 acertos
        - Intermediário: 5-7 acertos
        - Avançado: 8-10 acertos
        """)
        precisao = st.number_input("Número de acertos", min_value=0, max_value=10)
    
    # Teste de Agilidade
    with st.expander("Agilidade - Teste do Quadrado", expanded=True):
        st.write("**Material necessário:** 4 marcadores, cronômetro")
        st.write("**Como realizar:**")
        st.write("""
        1. Monte quadrado 4x4 metros
        2. Corra em zigue-zague
        3. Registre o tempo
        """)
        st.write("**Classificação:**")
        st.write("""
        - Iniciante: >12s
        - Intermediário: 10-12s
        - Avançado: <10s
        """)
        agilidade = st.number_input("Tempo (segundos)", min_value=0.0, max_value=20.0, step=0.1)
    
    # Teste de Equilíbrio
    with st.expander("Equilíbrio", expanded=True):
        st.write("**Material necessário:** Cronômetro")
        st.write("**Como realizar:**")
        st.write("""
        1. Fique em uma perna
        2. Feche os olhos
        3. Registre o tempo máximo
        """)
        st.write("**Classificação:**")
        st.write("""
        - Iniciante: <20s
        - Intermediário: 20-40s
        - Avançado: >40s
        """)
        equilibrio = st.number_input("Tempo de equilíbrio (segundos)", min_value=0, max_value=120)
    
    if st.button("Salvar Habilidades Técnicas"):
        st.session_state.test_results['habilidades_tecnicas'] = {
            'coordenacao': coordenacao,
            'precisao': precisao,
            'agilidade': agilidade,
            'equilibrio': equilibrio
        }
        st.success("Resultados salvos com sucesso!")

def show_aspectos_taticos():
    st.title("🧠 Aspectos Táticos")
    
    st.info("Complete os testes táticos abaixo. Realize cada teste conforme as instruções.")
    
    # Tomada de Decisão
    with st.expander("Tomada de Decisão - Jogo de Reação", expanded=True):
        st.write("**Material necessário:** Cartões coloridos")
        st.write("**Como realizar:**")
        st.write("""
        1. Reagir a cores diferentes
        2. Executar movimentos específicos
        3. 10 tentativas em 30 segundos
        """)
        decisao = st.number_input("Número de acertos", min_value=0, max_value=10)
    
    # Visão de Jogo
    with st.expander("Visão de Jogo - Memorização", expanded=True):
        st.write("**Material necessário:** 10 objetos diferentes")
        st.write("**Como realizar:**")
        st.write("""
        1. Memorizar posições em 30s
        2. Reposicionar objetos
        3. Contar acertos
        """)
        visao = st.number_input("Posições corretas", min_value=0, max_value=10)
    
    # Posicionamento
    with st.expander("Posicionamento - Reação Sonora", expanded=True):
        st.write("**Material necessário:** Aplicativo de som ou ajudante")
        st.write("**Como realizar:**")
        st.write("""
        1. Aguardar sinais sonoros
        2. Mover para posições marcadas
        3. Avaliar precisão
        """)
        posicionamento = st.slider("Precisão de movimento", min_value=1, max_value=10)
    
    if st.button("Salvar Aspectos Táticos"):
        st.session_state.test_results['aspectos_taticos'] = {
            'tomada_decisao': decisao,
            'visao_jogo': visao,
            'posicionamento': posicionamento
        }
        st.success("Resultados salvos com sucesso!")

def show_fatores_psicologicos():
    st.title("🎯 Fatores Psicológicos")
    
    st.info("Complete a auto-avaliação abaixo. Avalie cada aspecto em uma escala de 1 a 10.")
    
    # Motivação
    with st.expander("Motivação", expanded=True):
        st.write("**Auto-avaliação de Motivação**")
        dedicacao = st.slider("Quanto você se dedica aos treinos?", 1, 10)
        frequencia = st.slider("Com que frequência pratica atividades físicas?", 1, 10)
        comprometimento = st.slider("Qual seu nível de comprometimento com objetivos?", 1, 10)
    
    # Resiliência
    with st.expander("Resiliência", expanded=True):
        st.write("**Auto-avaliação de Resiliência**")
        derrotas = st.slider("Como lida com derrotas?", 1, 10)
        criticas = st.slider("Como reage a críticas?", 1, 10)
        erros = st.slider("Como se recupera de erros?", 1, 10)
    
    # Trabalho em Equipe
    with st.expander("Trabalho em Equipe", expanded=True):
        st.write("**Auto-avaliação de Trabalho em Equipe**")
        comunicacao = st.slider("Como se comunica em grupo?", 1, 10)
        opinioes = st.slider("Como lida com diferentes opiniões?", 1, 10)
        contribuicao = st.slider("Como contribui para objetivos coletivos?", 1, 10)
    
    if st.button("Salvar Fatores Psicológicos"):
        st.session_state.test_results['fatores_psicologicos'] = {
            'motivacao': {
                'dedicacao': dedicacao,
                'frequencia': frequencia,
                'comprometimento': comprometimento
            },
            'resiliencia': {
                'derrotas': derrotas,
                'criticas': criticas,
                'erros': erros
            },
            'trabalho_equipe': {
                'comunicacao': comunicacao,
                'opinioes': opinioes,
                'contribuicao': contribuicao
            }
        }
        st.success("Resultados salvos com sucesso!")

def show_recommendations():
    st.title("⭐ Suas Recomendações de Esportes")
    
    # Verificar se todos os testes foram completados
    test_categories = ['dados_fisicos', 'habilidades_tecnicas', 
                      'aspectos_taticos', 'fatores_psicologicos']
    
    all_tests_completed = all(
        category in st.session_state.test_results 
        for category in test_categories
    )
    
    if not all_tests_completed:
        missing_categories = [cat for cat in test_categories 
                            if cat not in st.session_state.test_results]
        st.warning("Complete os seguintes testes para receber suas recomendações:")
        for cat in missing_categories:
            st.write(f"- {cat.replace('_', ' ').title()}")
        return
    
    # Processar resultados e obter recomendações
# Processar resultados e obter recomendações
    if 'recommendations' not in st.session_state or st.session_state.recommendations is None:
        with st.spinner("Analisando seus resultados..."):
            try:
                processed_scores = process_test_results(st.session_state.test_results)
                st.session_state.recommendations = get_sport_recommendations(processed_scores)
                st.session_state.processed_scores = processed_scores
            except Exception as e:
                st.error(f"Erro ao processar recomendações: {str(e)}")
                return    
    # Layout em duas colunas
    col1, col2 = st.columns([2, 3])
    
    with col1:
        # Mostrar gráfico radar
        st.subheader("Seu Perfil de Habilidades")
        try:
            radar_chart = create_radar_chart(st.session_state.processed_scores)
            st.plotly_chart(radar_chart, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao criar gráfico: {str(e)}")
    
    with col2:
        # Mostrar recomendações
        st.subheader("Top 5 Esportes Recomendados")
        
        for sport in st.session_state.recommendations:
            with st.expander(f"{sport['name']} - {sport['compatibility']}% compatível"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🎯 Pontos Fortes:**")
                    for strength in sport['strengths']:
                        st.markdown(f"- {strength}")
                
                with col2:
                    st.markdown("**💪 Áreas para Desenvolvimento:**")
                    for area in sport['development']:
                        st.markdown(f"- {area}")
    
    # Botões de ação
    # Botões de ação
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Exportar Relatório", use_container_width=True):
            st.info("Funcionalidade de exportação em desenvolvimento")
    
    with col2:
        if st.button("🔄 Recomeçar Testes", use_container_width=True):
            reset_session_state()
            st.experimental_set_query_params(reset=True)
            st.rerun()

def main():

     # Verifica se é um reset
    query_params = st.experimental_get_query_params()
    if query_params.get("reset"):
        reset_session_state()
        st.experimental_set_query_params()
        
    # Menu lateral
    with st.sidebar:
        selected = option_menu(
            "Menu Principal",
            ["Home", "Dados Físicos", "Habilidades Técnicas", 
             "Aspectos Táticos", "Fatores Psicológicos", "Recomendações"],
            icons=['house', 'activity', 'bullseye', 'diagram-3', 'person', 'star'],
            menu_icon="cast",
            default_index=0,
        )
    
    # Conteúdo baseado na seleção do menu
    if selected == "Home":
        show_home()
    elif selected == "Dados Físicos":
        show_dados_fisicos()
    elif selected == "Habilidades Técnicas":
        show_habilidades_tecnicas()
    elif selected == "Aspectos Táticos":
        show_aspectos_taticos()
    elif selected == "Fatores Psicológicos":
        show_fatores_psicologicos()
    elif selected == "Recomendações":
        show_recommendations()
        
        # Informações Pessoais
        st.subheader("Informações Pessoais")
        form_key = f"personal_info_form_{st.session_state.form_key}"
        
        with st.form(key=form_key):
            col1, col2 = st.columns(2)
            
            with col1:
                altura = st.number_input(
                    "Altura (cm)", 
                    min_value=0, 
                    max_value=300,
                    value=170,
                    key=f"altura_{st.session_state.form_key}"
                )
                peso = st.number_input(
                    "Peso (kg)", 
                    min_value=0, 
                    max_value=300,
                    value=70,
                    key=f"peso_{st.session_state.form_key}"
                )
                envergadura = st.number_input(
                    "Envergadura (cm)", 
                    min_value=0, 
                    max_value=300,
                    value=170,
                    key=f"envergadura_{st.session_state.form_key}"
                )
            
            with col2:
                idade = st.number_input(
                    "Idade", 
                    min_value=0, 
                    max_value=150,
                    value=25,
                    key=f"idade_{st.session_state.form_key}"
                )
                ano_nascimento = st.number_input(
                    "Ano de Nascimento", 
                    min_value=1900, 
                    max_value=2024,
                    value=2000,
                    key=f"ano_nascimento_{st.session_state.form_key}"
                )
            
            # Localização
            st.write("**Localização**")
            col3, col4, col5 = st.columns(3)
            
            with col3:
                cidade = st.text_input(
                    "Cidade",
                    key=f"cidade_{st.session_state.form_key}"
                )
            with col4:
                estado = st.text_input(
                    "Estado",
                    key=f"estado_{st.session_state.form_key}"
                )
            with col5:
                pais = st.text_input(
                    "País",
                    key=f"pais_{st.session_state.form_key}"
                )
            
            submitted = st.form_submit_button("Salvar Informações")
            
            if submitted:
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
                st.session_state.form_key += 1
                st.success("Informações pessoais salvas com sucesso!")
        
        # Progresso dos Testes
        st.subheader("Seu Progresso")
        
        test_categories = {
            "Dados Físicos": 'dados_fisicos',
            "Habilidades Técnicas": 'habilidades_tecnicas',
            "Aspectos Táticos": 'aspectos_taticos',
            "Fatores Psicológicos": 'fatores_psicologicos'
        }
        
        for label, category in test_categories.items():
            progress = 1.0 if category in st.session_state.test_results else 0.0
            st.progress(progress, text=f"{label}: {int(progress * 100)}%")
            
    elif selected == "Dados Físicos":
        show_dados_fisicos()
    elif selected == "Habilidades Técnicas":
        show_habilidades_tecnicas()
    elif selected == "Aspectos Táticos":
        show_aspectos_taticos()
    elif selected == "Fatores Psicológicos":
        show_fatores_psicologicos()
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
