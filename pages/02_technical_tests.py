import streamlit as st
from config.config import TESTS_CONFIG

def show_technical_tests():
    st.title("🎯 Testes Técnicos")
    
    tests = TESTS_CONFIG["technical"]["tests"]
    
    st.info("Complete os testes técnicos abaixo. Avalie cada habilidade conforme as instruções.")
    
    for test_id, test in tests.items():
        st.subheader(test["name"])
        st.write(test["description"])
        
        value = st.slider(
            f"Resultado ({test['unit']})",
            min_value=float(test["min"]),
            max_value=float(test["max"]),
            value=float(test["min"]),
            key=f"technical_{test_id}"
        )
        
        # Salvar resultado no session state
        if value:
            st.session_state.test_results["technical"][test_id] = value
    
    # Botões de navegação
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Voltar: Testes Físicos"):
            st.switch_page("pages/01_physical_tests.py")
    with col2:
        if st.button("Próximo: Testes Táticos →"):
            st.switch_page("pages/03_tactical_tests.py")

if __name__ == "__main__":
    show_technical_tests()
