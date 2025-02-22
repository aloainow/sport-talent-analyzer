import pandas as pd
import json

def format_sport_name(sport_name: str) -> str:
    """Formata o nome do esporte com suas especificações"""
    # Mapeamento de categorias
    categorias = {
        'Middleweight': 'Peso Médio',
        'Lightweight': 'Peso Leve',
        'Heavyweight': 'Peso Pesado',
        'Featherweight': 'Peso Pena',
        'Flyweight': 'Peso Mosca',
        'Welterweight': 'Peso Meio-Médio',
        'Light Heavyweight': 'Peso Meio-Pesado',
        'Super Heavyweight': 'Peso Super-Pesado',
        'Discus Throw': 'Lançamento de Disco',
        'Javelin Throw': 'Lançamento de Dardo',
        'Shot Put': 'Arremesso de Peso',
        'Hammer Throw': 'Lançamento de Martelo',
        'Long Jump': 'Salto em Distância',
        'High Jump': 'Salto em Altura',
        'Triple Jump': 'Salto Triplo',
        'Pole Vault': 'Salto com Vara'
    }
    
    # Traduzir especificações (mantendo a ordem correta em português)
    for en, pt in categorias.items():
        if en in sport_name:
            # Remover a especificação em inglês
            sport_name = sport_name.replace(en, '')
            # Adicionar a tradução após o nome do esporte
            parts = sport_name.split()
            if 'Feminino' in parts or 'Masculino' in parts:
                gender = parts[-1]
                parts = parts[:-1]
                return f"{' '.join(parts).strip()} - {pt} {gender}"
            else:
                return f"{sport_name.strip()} - {pt}"
    
    return sport_name

def clean_event_name(event_name: str) -> str:
    """Remove duplicações e limpa o nome do evento"""
    # Guardar o gênero
    gender = ""
    if "Men's" in event_name:
        gender = "Men's"
    elif "Women's" in event_name:
        gender = "Women's"
    
    # Remover gênero temporariamente
    event_name = event_name.replace("Men's ", "").replace("Women's ", "")
    
    # Remover duplicações
    words = event_name.split()
    clean_words = []
    for word in words:
        if not clean_words or word != clean_words[-1]:
            clean_words.append(word)
    
    # Reconstruir o nome com o gênero original
    cleaned_name = " ".join(clean_words)
    if gender:
        cleaned_name = f"{gender} {cleaned_name}"
    
    return cleaned_name

def get_base_sport_name(event_name: str) -> str:
    """Extrai o nome base do esporte do evento"""
    # Remover gênero
    event_name = event_name.replace("Men's ", "").replace("Women's ", "")
    
    # Lista de esportes compostos
    composite_sports = [
        "Beach Volleyball",
        "Water Polo",
        "Table Tennis",
        "Figure Skating",
        "Speed Skating"
    ]
    
    # Verificar se é um esporte composto
    words = event_name.split()
    if len(words) >= 2:
        two_word_sport = f"{words[0]} {words[1]}"
        if two_word_sport in composite_sports:
            return two_word_sport
    
    return words[0] if words else event_name

def traduzir_evento(evento: str) -> str:
    """Traduz eventos olímpicos de inglês para português"""
    # Guardar o gênero
    is_male = "Men's" in evento
    is_female = "Women's" in evento
    
    # Limpar e remover gênero para tradução
    evento = clean_event_name(evento)
    evento = evento.replace("Men's ", "").replace("Women's ", "")
    
    # Dicionário de traduções básicas dos esportes
    traducoes = {
        'Swimming': 'Natação',
        'Athletics': 'Atletismo',
        'Gymnastics': 'Ginástica',
        'Basketball': 'Basquete',
        'Volleyball': 'Vôlei',
        'Beach Volleyball': 'Vôlei de Praia',
        'Water Polo': 'Polo Aquático',
        'Football': 'Futebol',
        'Handball': 'Handebol',
        'Rugby': 'Rugby',
        'Tennis': 'Tênis',
        'Table Tennis': 'Tênis de Mesa',
        'Boxing': 'Boxe',
        'Wrestling': 'Luta Livre',
        'Judo': 'Judô',
        'Taekwondo': 'Taekwondo',
        'Karate': 'Karatê',
        'Fencing': 'Esgrima',
        'Shooting': 'Tiro',
        'Archery': 'Tiro com Arco',
        'Cycling': 'Ciclismo',
        'Rowing': 'Remo',
        'Sailing': 'Vela',
        'Canoe': 'Canoagem',
        'Equestrian': 'Hipismo',
        
        # Eventos específicos
        'Singles': 'Individual',
        'Doubles': 'Duplas',
        'Mixed Doubles': 'Duplas Mistas',
        'Team': 'Equipe',
        'Relay': 'Revezamento',
        'Marathon': 'Maratona',
        'Race': 'Corrida',
        'Sprint': 'Velocidade',
        
        # Estilos de natação
        'Freestyle': 'Livre',
        'Backstroke': 'Costas',
        'Breaststroke': 'Peito',
        'Butterfly': 'Borboleta',
        'Medley': 'Medley',
        
        # Unidades de medida
        'metres': 'metros',
        'm': 'm',
        'km': 'km'
    }
    
    # Traduzir usando o dicionário (do maior para o menor para evitar substituições parciais)
    for en, pt in sorted(traducoes.items(), key=len, reverse=True):
        evento = evento.replace(en, pt)
    
    # Remover duplicações após tradução
    words = evento.split()
    clean_words = []
    for word in words:
        if not clean_words or word != clean_words[-1]:
            clean_words.append(word)
    evento = " ".join(clean_words)
    
    # Adicionar gênero
    if is_male:
        evento = f"{evento} Masculino"
    elif is_female:
        evento = f"{evento} Feminino"
    
    # Formatar o nome final
    return format_sport_name(evento)
