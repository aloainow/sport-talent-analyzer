import streamlit as st
from config.config import TESTS_CONFIG

def show_tactical_tests():
    st.title("🧠 Testes Táticos")
    
    tests = TESTS_CONFIG["tactical"]["tests"]
    
    st.info("Avalie suas habilidades táticas conforme as situações descritas.")
    
    for test_id, test in tests.items():
        st.subheader(test["name"])
        st.write(test["description"])
        
        value = st.slider(
            f"Resultado ({test['unit']})",
            min_value=float(test["min"]),
            max_value=float(test["max"]),
            value=float(test["min"]),
            key=f"tactical_{test_id}"
        )
        
        # Salvar resultado no session state
        if value:
            st.session_state.test_results["tactical"][test_id] = value
    
    # Botões de navegação
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Voltar: Testes Técnicos"):
            st.switch_page("pages/02_technical_tests.py")
    with col2:
        if st.button("Próximo: Testes Psicológicos →"):
            st.switch_page("pages/04_psychological_tests.py")

if __name__ == "__main__":
    show_tactical_tests()
