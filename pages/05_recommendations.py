import streamlit as st
import plotly.graph_objects as go
from utils.openai_helper import get_sport_recommendations
from utils.test_processor import process_test_results

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

def show_recommendations():
    st.title("⭐ Suas Recomendações de Esportes")
    
    # Verificar se todos os testes foram completados
    all_tests_completed = all(
        len(st.session_state.test_results[category]) > 0 
        for category in ['physical', 'technical', 'tactical', 'psychological']
    )
    
    if not all_tests_completed:
        st.warning("Por favor, complete todos os testes para receber suas recomendações!")
        if st.button("Voltar para Testes"):
            st.switch_page("pages/01_physical_tests.py")
        return
    
    # Processar resultados e obter recomendações
    if 'recommendations' not in st.session_state:
        with st.spinner("Analisando seus resultados..."):
            processed_results = process_test_results(st.session_state.test_results)
            st.session_state.recommendations = get_sport_recommendations(processed_results)
    
    # Mostrar gráfico radar
    st.subheader("Seu Perfil de Habilidades")
    radar_chart = create_radar_chart(st.session_state.test_results)
    st.plotly_chart(radar_chart, use_container_width=True)
    
    # Mostrar recomendações
    st.subheader("Esportes Recomendados")
    
    for sport in st.session_state.recommendations:
        with st.expander(f"{sport['name']} - {sport['compatibility']}% compatível"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Pontos Fortes:**")
                for strength in sport['strengths']:
                    st.write(f"✓ {strength}")
            
            with col2:
                st.write("**Áreas para Desenvolvimento:**")
                for area in sport['development']:
                    st.write(f"→ {area}")
    
    # Botões de ação
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Voltar aos Testes"):
            st.switch_page("pages/04_psychological_tests.py")
    
    with col2:
        if st.button("📊 Exportar Relatório"):
            # Aqui você pode adicionar a lógica para exportar o relatório
            st.info("Funcionalidade de exportação em desenvolvimento")
    
    with col3:
        if st.button("🔄 Recomeçar"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.switch_page("pages/01_physical_tests.py")

if __name__ == "__main__":
    show_recommendations()
