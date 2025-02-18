import streamlit as st
from config.config import TESTS_CONFIG

def show_physical_tests():
    st.title("🏃‍♂️ Testes Físicos")
    
    tests = TESTS_CONFIG["physical"]["tests"]
    
    st.info("Complete os testes físicos abaixo. Realize cada teste conforme as instruções.")
    
    for test_id, test in tests.items():
        st.subheader(test["name"])
        st.write(test["description"])
        
        col1, col2 = st.columns(2)
        with col1:
            value = st.number_input(
                f"Resultado ({test['unit']})",
                min_value=float(test["min"]),
                max_value=float(test["max"]),
                value=float(test["min"]),
                key=f"physical_{test_id}"
            )
            
            # Salvar resultado no session state
            if value:
                st.session_state.test_results["physical"][test_id] = value
        
        with col2:
            st.write(f"Faixa esperada: {test['min']} - {test['max']} {test['unit']}")
    
    # Botão para próxima página
    if st.button("Próximo: Testes Técnicos"):
        st.switch_page("pages/02_technical_tests.py")

if __name__ == "__main__":
    show_physical_tests()
