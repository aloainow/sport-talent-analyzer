import pandas as pd
import json

def traduzir_evento(evento):
    """
    Traduz eventos olímpicos de inglês para português
    """
    # Dicionários de traduções base
    traducoes_esportes = {
        'Athletics': 'Atletismo',
        'Swimming': 'Natação',
        'Gymnastics': 'Ginástica',
        'Wrestling': 'Luta',
        'Boxing': 'Boxe',
        'Volleyball': 'Vôlei',
        'Basketball': 'Basquete',
        'Football': 'Futebol',
        'Handball': 'Handebol',
        'Hockey': 'Hóquei',
        'Water Polo': 'Polo Aquático',
        'Cycling': 'Ciclismo',
        'Rowing': 'Remo',
        'Fencing': 'Esgrima',
        'Judo': 'Judô',
        'Taekwondo': 'Taekwondo',
        'Tennis': 'Tênis'
    }

    traducoes_termos = {
        # Distâncias e medidas
        'metres': 'metros',
        'Marathon': 'Maratona',
        'Individual': 'Individual',
        'All-Around': 'Geral',
        'Team': 'Equipe',
        'Road Race': 'Corrida de Estrada',
        
        # Modalidades de nado
        'Freestyle': 'Nado Livre',
        'Backstroke': 'Costas', 
        'Breaststroke': 'Peito',
        'Butterfly': 'Borboleta',
        
        # Eventos ginástica
        'Floor Exercise': 'Solo',
        'Horizontal Bar': 'Barra Fixa',
        'Parallel Bars': 'Barras Paralelas',
        'Rings': 'Argolas',
        'Balance Beam': 'Trave',
        'Uneven Bars': 'Barras Assimétricas',
        
        # Saltos e arremessos
        'High Jump': 'Salto em Altura',
        'Long Jump': 'Salto em Distância', 
        'Triple Jump': 'Salto Triplo',
        'Pole Vault': 'Salto com Vara',
        'Shot Put': 'Arremesso de Peso',
        'Discus Throw': 'Lançamento de Disco',
        'Hammer Throw': 'Lançamento de Martelo', 
        'Javelin Throw': 'Lançamento de Dardo',
        
        # Categorias de peso
        'Flyweight': 'Peso Mosca',
        'Bantamweight': 'Peso Galo',
        'Featherweight': 'Peso Pena', 
        'Lightweight': 'Peso Leve',
        'Welterweight': 'Peso Meio-Médio',
        'Middleweight': 'Peso Médio', 
        'Light-Heavyweight': 'Peso Meio-Pesado',
        'Heavyweight': 'Peso Pesado',
        
        # Tipos de lutas
        'Greco-Roman': 'Greco-Romana',
        'Freestyle': 'Estilo Livre'
    }

    # Substituições em ordem
    for en, pt in sorted(traducoes_esportes.items(), key=len, reverse=True):
        evento = evento.replace(en, pt)
    
    for en, pt in sorted(traducoes_termos.items(), key=len, reverse=True):
        evento = evento.replace(en, pt)
    
    # Ajustar gênero
    if "Men's" in evento:
        evento = evento.replace("Men's", "").strip() + " Masculino"
    elif "Women's" in evento:
        evento = evento.replace("Women's", "").strip() + " Feminino"
    
    return evento.strip()

# Ler o CSV de eventos olímpicos
df = pd.read_csv('data/perfil_eventos_olimpicos_verao.csv')

# Gerar dicionário de traduções
EVENT_TRANSLATIONS = {event: traduzir_evento(event) for event in df['Event'].unique()}

# Salvar traduções em JSON para verificação
with open('event_translations.json', 'w', encoding='utf-8') as f:
    json.dump(EVENT_TRANSLATIONS, f, ensure_ascii=False, indent=2)

# Imprimir algumas traduções
print("Traduções de exemplo:")
for orig, trad in list(EVENT_TRANSLATIONS.items())[:20]:
    print(f"{orig}: {trad}")
