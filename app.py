import streamlit as st

st.set_page_config(
    page_title="Analisador de Talentos Esportivos",
    page_icon="🏃‍♂️",
    layout="wide"
)

# Agora os outros imports podem vir abaixo
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
from utils.test_processor import normalize_score, calculate_average, process_test_results
from utils.openai_helper import get_sport_recommendations, get_recommendations_without_api

def reset_session_state():
    """Reseta completamente o estado da sessão"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Reinicializa com valores padrão
    st.session_state.test_results = {
        'dados_fisicos': None,  # Mudado de {} para None
        'habilidades_tecnicas': None,  # Mudado de {} para None
        'aspectos_taticos': None,  # Mudado de {} para None
        'fatores_psicologicos': None  # Mudado de {} para None
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
            'dados_fisicos': None,  # Mudado de {} para None
            'habilidades_tecnicas': None,  # Mudado de {} para None
            'aspectos_taticos': None,  # Mudado de {} para None
            'fatores_psicologicos': None  # Mudado de {} para None
        }
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    if 'personal_info' not in st.session_state:
        st.session_state.personal_info = {}
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0
    if 'processed_scores' not in st.session_state:
        st.session_state.processed_scores = None
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        
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
            idade = st.number_input("Idade", 
                                  min_value=10, 
                                  max_value=18, 
                                  value=st.session_state.personal_info.get('idade', 15))
            
            altura = st.number_input("Altura (cm)", 
                                   min_value=100, 
                                   max_value=220, 
                                   value=st.session_state.personal_info.get('altura', 170))
            
            peso = st.number_input("Peso (kg)", 
                                 min_value=30, 
                                 max_value=150, 
                                 value=st.session_state.personal_info.get('peso', 60))

        with col2:
            envergadura = st.number_input("Envergadura (cm)", 
                                        min_value=100, 
                                        max_value=230, 
                                        value=st.session_state.personal_info.get('envergadura', 170))
            
            genero = st.selectbox(
                "Gênero",
                ["Masculino", "Feminino"],
                index=0 if st.session_state.personal_info.get('genero') == "Masculino" else 1
            )

            ano_nascimento = st.number_input(
                "Ano de Nascimento",
                min_value=2006,
                max_value=2014,
                value=st.session_state.personal_info.get('ano_nascimento', 2009)
            )

        # Localização
        st.write("**Localização**")
        col3, col4, col5 = st.columns(3)

        with col3:
            cidade = st.text_input("Cidade", value=st.session_state.personal_info.get('cidade', ''))
        with col4:
            estado = st.text_input("Estado", value=st.session_state.personal_info.get('estado', ''))
        with col5:
            pais = st.text_input("País", value=st.session_state.personal_info.get('pais', ''))

        submitted = st.form_submit_button("Salvar Informações")

        if submitted:
            # Atualizar informações pessoais
            st.session_state.personal_info = {
                'idade': idade,
                'altura': altura,
                'peso': peso,
                'envergadura': envergadura,
                'genero': genero,
                'ano_nascimento': ano_nascimento,
                'cidade': cidade,
                'estado': estado,
                'pais': pais,
                # Adicionar biotipo estruturado
                'biotipo': {
                    'altura': altura,
                    'peso': peso,
                    'envergadura': envergadura
                }
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
        'Físico', 
        'Técnico',
        'Tático', 
        'Psicológico'
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
        line_color='rgb(147, 112, 219)',
        fillcolor='rgba(147, 112, 219, 0.5)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
    visible=True,
    range=[0, 100],
    showticklabels=False,  # REMOVE OS NÚMEROS
    showline=True,
    linewidth=1,
    linecolor='white',
    gridcolor='rgba(255, 255, 255, 0.1)'
),

            angularaxis=dict(
                tickmode='array',
                ticktext=categories[:-1],
                tickvals=list(range(len(categories[:-1]))),
                direction='clockwise',
                tickfont=dict(
                    size=14,
                    color="white"
                ),
                gridcolor='rgba(255, 255, 255, 0.1)',
                linecolor='rgba(255, 255, 255, 0.1)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=30, l=30, r=30),
        height=400
    )
    
    return fig

def analyze_user_attributes(test_results, personal_info):
    """Analisa os atributos do usuário e retorna pontos fortes e a desenvolver."""
    attributes = {}
    
    # Análise física
    if test_results['dados_fisicos']:
        dados_fisicos = test_results['dados_fisicos']
        attributes['velocidade'] = normalize_score(dados_fisicos['velocidade'], 2.5, 5.0, inverse=True)
        attributes['forca_superior'] = normalize_score(dados_fisicos['forca_superior'], 0, 50)
        attributes['forca_inferior'] = normalize_score(dados_fisicos['forca_inferior'], 0, 60)
    
    # Análise técnica
    if test_results['habilidades_tecnicas']:
        hab_tecnicas = test_results['habilidades_tecnicas']
        attributes['coordenacao'] = normalize_score(hab_tecnicas['coordenacao'], 0, 50)
        attributes['precisao'] = normalize_score(hab_tecnicas['precisao'], 0, 10)
        attributes['agilidade'] = normalize_score(hab_tecnicas['agilidade'], 5, 15, inverse=True)
        attributes['equilibrio'] = normalize_score(hab_tecnicas['equilibrio'], 0, 60)
    
    # Análise tática
    if test_results['aspectos_taticos']:
        aspectos_taticos = test_results['aspectos_taticos']
        attributes['tomada_decisao'] = normalize_score(aspectos_taticos['tomada_decisao'], 0, 10)
        attributes['visao_jogo'] = normalize_score(aspectos_taticos['visao_jogo'], 0, 10)
        attributes['posicionamento'] = normalize_score(aspectos_taticos['posicionamento'], 1, 10)
    
    # Análise psicológica (médias das subcategorias)
    if test_results['fatores_psicologicos']:
        fatores_psic = test_results['fatores_psicologicos']
        attributes['motivacao'] = calculate_average([
            fatores_psic['motivacao']['dedicacao'],
            fatores_psic['motivacao']['frequencia'],
            fatores_psic['motivacao']['comprometimento']
        ])
        attributes['resiliencia'] = calculate_average([
            fatores_psic['resiliencia']['derrotas'],
            fatores_psic['resiliencia']['criticas'],
            fatores_psic['resiliencia']['erros']
        ])
        attributes['trabalho_equipe'] = calculate_average([
            fatores_psic['trabalho_equipe']['comunicacao'],
            fatores_psic['trabalho_equipe']['opinioes'],
            fatores_psic['trabalho_equipe']['contribuicao']
        ])
    
    # Análise das informações pessoais
    if personal_info:
        attributes['altura'] = normalize_score(personal_info.get('altura', 170), 150, 210)
        attributes['peso'] = normalize_score(personal_info.get('peso', 70), 45, 120)
        attributes['envergadura'] = normalize_score(personal_info.get('envergadura', 170), 150, 210)
    
    # Identificar pontos fortes e a desenvolver
    sorted_attrs = sorted(attributes.items(), key=lambda x: x[1], reverse=True)
    
    pontos_fortes = [f"{attr.replace('_', ' ').title()}: {score:.0f}%" 
                     for attr, score in sorted_attrs[:5] if score >= 60]
    
    desenvolver = [f"{attr.replace('_', ' ').title()}: {score:.0f}%" 
                  for attr, score in sorted_attrs[-5:] if score < 60]
    
    return pontos_fortes, desenvolver
    
def show_dados_fisicos():
    st.title("💪 Dados Físicos")
    
    st.info("Complete os testes físicos abaixo. Realize cada teste conforme as instruções.")
    
    # Pegar o gênero do usuário do session state
    genero = st.session_state.personal_info.get('genero', 'Masculino')
    
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
        if genero == "Masculino":
            st.write("""
            - Iniciante: >4.0s
            - Intermediário: 3.5-4.0s
            - Avançado: <3.5s
            """)
        else:  # Feminino
            st.write("""
            - Iniciante: >4.5s
            - Intermediário: 4.0-4.5s
            - Avançado: <4.0s
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
        if genero == "Masculino":
            st.write("""
            - Iniciante: 10-15 repetições
            - Intermediário: 16-25 repetições
            - Avançado: 26+ repetições
            """)
        else:  # Feminino
            st.write("""
            - Iniciante: 5-10 repetições
            - Intermediário: 11-20 repetições
            - Avançado: 21+ repetições
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
        if genero == "Masculino":
            st.write("""
            - Iniciante: 20-30 repetições
            - Intermediário: 31-40 repetições
            - Avançado: 41+ repetições
            """)
        else:  # Feminino
            st.write("""
            - Iniciante: 15-25 repetições
            - Intermediário: 26-35 repetições
            - Avançado: 36+ repetições
            """)
        forca_inferior = st.number_input("Número de agachamentos", min_value=0, max_value=100)
    
    if st.button("Salvar Dados Físicos"):
        st.session_state.test_results['dados_fisicos'] = {
            'velocidade': velocidade,
            'forca_superior': forca_superior,
            'forca_inferior': forca_inferior,
            'genero': genero  # Adicionando o gênero aos dados salvos
        }
        st.success("Resultados salvos com sucesso!")        
def show_habilidades_tecnicas():
    st.title("🎯 Habilidades Técnicas")
    
    st.info("Complete os testes técnicos abaixo. Realize cada teste conforme as instruções.")
    
    # Pegar o gênero do usuário do session state
    genero = st.session_state.personal_info.get('genero', 'Masculino')
    
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
        if genero == "Masculino":
            st.write("""
            - Iniciante: <20 alternâncias
            - Intermediário: 20-30 alternâncias
            - Avançado: >30 alternâncias
            """)
        else:  # Feminino
            st.write("""
            - Iniciante: <25 alternâncias
            - Intermediário: 25-35 alternâncias
            - Avançado: >35 alternâncias
            """)
        coordenacao = st.number_input("Número de alternâncias", min_value=0, max_value=100, key="coord")
    
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
        if genero == "Masculino":
            st.write("""
            - Iniciante: 3-4 acertos
            - Intermediário: 5-7 acertos
            - Avançado: 8-10 acertos
            """)
        else:  # Feminino
            st.write("""
            - Iniciante: 4-5 acertos
            - Intermediário: 6-8 acertos
            - Avançado: 9-10 acertos
            """)
        precisao = st.number_input("Número de acertos", min_value=0, max_value=10, key="prec")
    
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
        if genero == "Masculino":
            st.write("""
            - Iniciante: >12s
            - Intermediário: 10-12s
            - Avançado: <10s
            """)
        else:  # Feminino
            st.write("""
            - Iniciante: >13s
            - Intermediário: 11-13s
            - Avançado: <11s
            """)
        agilidade = st.number_input("Tempo (segundos)", min_value=0.0, max_value=20.0, step=0.1, key="agil")
    
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
        if genero == "Masculino":
            st.write("""
            - Iniciante: <20s
            - Intermediário: 20-40s
            - Avançado: >40s
            """)
        else:  # Feminino
            st.write("""
            - Iniciante: <25s
            - Intermediário: 25-45s
            - Avançado: >45s
            """)
        equilibrio = st.number_input("Tempo de equilíbrio (segundos)", min_value=0, max_value=120, key="equil")
    
    if st.button("Salvar Habilidades Técnicas"):
        st.session_state.test_results['habilidades_tecnicas'] = {
            'coordenacao': coordenacao,
            'precisao': precisao,
            'agilidade': agilidade,
            'equilibrio': equilibrio,
            'genero': genero  # Adicionando o gênero aos dados salvos
        }
        st.success("Resultados salvos com sucesso!")
def show_aspectos_taticos():
    st.title("🧠 Aspectos Táticos")
    
    st.info("Complete os testes táticos abaixo. Realize cada teste conforme as instruções.")
    
    # Pegar o gênero do usuário do session state
    genero = st.session_state.personal_info.get('genero', 'Masculino')
    
    # Tomada de Decisão
    with st.expander("Tomada de Decisão - Jogo de Reação", expanded=True):
        st.write("**Material necessário:** Cartões coloridos")
        st.write("**Como realizar:**")
        st.write("""
        1. Reagir a cores diferentes
        2. Executar movimentos específicos
        3. 10 tentativas em 30 segundos
        """)
        st.write("**Classificação:**")
        if genero == "Masculino":
            st.write("""
            - Iniciante: 3-4 acertos
            - Intermediário: 5-7 acertos
            - Avançado: 8-10 acertos
            """)
        else:  # Feminino
            st.write("""
            - Iniciante: 4-5 acertos
            - Intermediário: 6-8 acertos
            - Avançado: 9-10 acertos
            """)
        decisao = st.number_input("Número de acertos", min_value=0, max_value=10, key="decisao")
    
    # Visão de Jogo
    with st.expander("Visão de Jogo - Memorização", expanded=True):
        st.write("**Material necessário:** 10 objetos diferentes")
        st.write("**Como realizar:**")
        st.write("""
        1. Memorizar posições em 30s
        2. Reposicionar objetos
        3. Contar acertos
        """)
        st.write("**Classificação:**")
        if genero == "Masculino":
            st.write("""
            - Iniciante: 3-4 posições
            - Intermediário: 5-7 posições
            - Avançado: 8-10 posições
            """)
        else:  # Feminino
            st.write("""
            - Iniciante: 4-5 posições
            - Intermediário: 6-8 posições
            - Avançado: 9-10 posições
            """)
        visao = st.number_input("Posições corretas", min_value=0, max_value=10, key="visao")
    
    # Posicionamento
    with st.expander("Posicionamento - Reação Sonora", expanded=True):
        st.write("**Material necessário:** Aplicativo de som ou ajudante")
        st.write("**Como realizar:**")
        st.write("""
        1. Aguardar sinais sonoros
        2. Mover para posições marcadas
        3. Avaliar precisão
        """)
        st.write("**Classificação:**")
        if genero == "Masculino":
            st.write("""
            - Iniciante: 1-3 pontos
            - Intermediário: 4-7 pontos
            - Avançado: 8-10 pontos
            """)
        else:  # Feminino
            st.write("""
            - Iniciante: 2-4 pontos
            - Intermediário: 5-8 pontos
            - Avançado: 9-10 pontos
            """)
        posicionamento = st.slider("Precisão de movimento", min_value=1, max_value=10, key="posic")
    
    if st.button("Salvar Aspectos Táticos"):
        st.session_state.test_results['aspectos_taticos'] = {
            'tomada_decisao': decisao,
            'visao_jogo': visao,
            'posicionamento': posicionamento,
            'genero': genero  # Adicionando o gênero aos dados salvos
        }
        st.success("Resultados salvos com sucesso!")

def show_fatores_psicologicos():
    st.title("🎯 Fatores Psicológicos")
    
    st.info("Complete a auto-avaliação abaixo. Avalie cada aspecto em uma escala de 1 a 10.")
    
    # Pegar o gênero do usuário do session state
    genero = st.session_state.personal_info.get('genero', 'Masculino')
    
    # Motivação
    with st.expander("Motivação", expanded=True):
        st.write("**Auto-avaliação de Motivação**")
        st.write("**Classificação geral:**")
        if genero == "Masculino":
            st.write("""
            - Baixa: 1-4 pontos
            - Média: 5-7 pontos
            - Alta: 8-10 pontos
            """)
        else:  # Feminino
            st.write("""
            - Baixa: 1-4 pontos
            - Média: 5-7 pontos
            - Alta: 8-10 pontos
            """)
        dedicacao = st.slider("Quanto você se dedica aos treinos?", 1, 10, key="ded")
        frequencia = st.slider("Com que frequência pratica atividades físicas?", 1, 10, key="freq")
        comprometimento = st.slider("Qual seu nível de comprometimento com objetivos?", 1, 10, key="comp")
    
    # Resiliência
    with st.expander("Resiliência", expanded=True):
        st.write("**Auto-avaliação de Resiliência**")
        st.write("**Classificação geral:**")
        if genero == "Masculino":
            st.write("""
            - Baixa: 1-4 pontos
            - Média: 5-7 pontos
            - Alta: 8-10 pontos
            """)
        else:  # Feminino
            st.write("""
            - Baixa: 1-4 pontos
            - Média: 5-7 pontos
            - Alta: 8-10 pontos
            """)
        derrotas = st.slider("Como lida com derrotas?", 1, 10, key="derr")
        criticas = st.slider("Como reage a críticas?", 1, 10, key="crit")
        erros = st.slider("Como se recupera de erros?", 1, 10, key="err")
    
    # Trabalho em Equipe
    with st.expander("Trabalho em Equipe", expanded=True):
        st.write("**Auto-avaliação de Trabalho em Equipe**")
        st.write("**Classificação geral:**")
        if genero == "Masculino":
            st.write("""
            - Baixa: 1-4 pontos
            - Média: 5-7 pontos
            - Alta: 8-10 pontos
            """)
        else:  # Feminino
            st.write("""
            - Baixa: 1-4 pontos
            - Média: 5-7 pontos
            - Alta: 8-10 pontos
            """)
        comunicacao = st.slider("Como se comunica em grupo?", 1, 10, key="com")
        opinioes = st.slider("Como lida com diferentes opiniões?", 1, 10, key="opin")
        contribuicao = st.slider("Como contribui para objetivos coletivos?", 1, 10, key="cont")
    
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
            },
            'genero': genero  # Adicionando o gênero aos dados salvos
        }
        st.success("Resultados salvos com sucesso!")
def show_recommendations():
    st.title("⭐ Suas Recomendações de Esportes")

    # Verificar se todos os testes foram completados
    all_tests_completed = all(st.session_state.test_results.values())

    if not all_tests_completed:
        st.warning("Complete todos os testes para ver suas recomendações completas.")
        return

    # Processar scores e gerar recomendações
    try:
        with st.spinner("Analisando seus resultados..."):
            user_data = {
                'altura': st.session_state.personal_info.get('altura'),
                'peso': st.session_state.personal_info.get('peso'),
                'envergadura': st.session_state.personal_info.get('envergadura'),
                'dados_fisicos': st.session_state.test_results['dados_fisicos'],
                'habilidades_tecnicas': st.session_state.test_results['habilidades_tecnicas'],
                'aspectos_taticos': st.session_state.test_results['aspectos_taticos'],
                'fatores_psicologicos': st.session_state.test_results['fatores_psicologicos']
            }

            # Processar scores para o gráfico radar
            processed_scores = process_test_results(st.session_state.test_results)
            st.session_state.processed_scores = processed_scores

            # Gerar recomendações
            st.session_state.recommendations = get_sport_recommendations(user_data)

    except Exception as e:
        st.error(f"Erro ao processar recomendações: {str(e)}")
        return

    # Exibir Radar Chart (Perfil do usuário)
    st.subheader("📊 Seu Perfil")
    fig = create_radar_chart(st.session_state.processed_scores)
    st.plotly_chart(fig, use_container_width=True)

    if not st.session_state.recommendations:
        st.warning("Não foram encontradas recomendações compatíveis com seu perfil.")
        return

    # Exibir contagem de esportes recomendados
    total_recomendacoes = len(st.session_state.recommendations)
    st.write(f"**Esportes recomendados: {total_recomendacoes}**")

    # Exibir Top 5 recomendações em cartões
    st.subheader("🏆 Top 5 Esportes Recomendados")

    # Pegar apenas os 5 primeiros esportes da lista
    top_5_recomendacoes = st.session_state.recommendations[:5]

    for index, sport in enumerate(top_5_recomendacoes, start=1):
        strengths = sport['strengths'] or ["Não informado"]
        development = sport['development'] or ["Não informado"]

        strengths_html = "".join(f"<li>{s}</li>" for s in strengths)
        development_html = "".join(f"<li>{d}</li>" for d in development)

        with st.container():
            st.markdown(
                f"""
                <div style="
                    background-color: #1e1e1e;
                    padding: 15px;
                    border-radius: 12px;
                    margin-bottom: 10px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                    color: white;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h3 style="margin: 0; color: white;">{index}. {sport['name']}</h3>
                        <span style="color: #4caf50; font-weight: bold; font-size: 18px;">
                            {sport['compatibility']}% compatível
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <div style="flex: 1; margin-right: 20px;">
                            <strong style="color: #81c784;">Pontos Fortes:</strong>
                            <ul style="margin-top: 5px; color: white;">
                                {strengths_html}
                            </ul>
                        </div>
                        <div style="flex: 1;">
                            <strong style="color: #64b5f6;">Áreas para Desenvolver:</strong>
                            <ul style="margin-top: 5px; color: white;">
                                {development_html}
                            </ul>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
def main():
    # Verifica se é um reset
    if "reset" in st.query_params:
        reset_session_state()
        st.query_params.clear()
    
    # Inicializa o estado da sessão
    if 'initialized' not in st.session_state:
        init_session_state()
    
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
