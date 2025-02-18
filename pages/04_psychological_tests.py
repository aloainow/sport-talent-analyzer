import streamlit as st
from config.config import TESTS_CONFIG

def show_psychological_tests():
    st.title("🧪 Testes Psicológicos")
    
    tests = TESTS_CONFIG["psychological"]["tests"]
    
    st.info("""
    Avalie honestamente suas características psicológicas.
    Use a escala de 1 a 10, onde:
    1 = Muito baixo/fraco
    10 = Muito alto/forte
    """)
    
    for test_id, test in tests.items():
        st.subheader(test["name"])
        st.write(test["description"])
        
        value = st.slider(
            f"Nível ({test['unit']})",
            min_value=float(test["min"]),
            max_value=float(test["max"]),
            value=float(test["min"]),
            key=f"psychological_{test_id}"
        )
        
        # Adicionar descrições específicas baseadas no valor
        if value <= 3:
            st.caption("Área que precisa de desenvolvimento")
        elif value <= 7:
            st.caption("Nível moderado")
        else:
            st.caption("Ponto forte")
            
        # Salvar resultado no session state
        if value:
            st.session_state.test_results["psychological"][test_id] = value
    
    # Botões de navegação
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Voltar: Testes Táticos"):
            st.switch_page("pages/03_tactical_tests.py")
    with col2:
        if st.button("Ver Recomendações →"):
            st.switch_page("pages/05_recommendations.py")

if __name__ == "__main__":
    show_psychological_tests()
