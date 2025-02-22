import pandas as pd
import json

def clean_event_name(event_name: str) -> str:
    """Remove duplicações e limpa o nome do evento"""
    # Remover gênero em inglês
    event_name = event_name.replace("Men's ", "").replace("Women's ", "")
    
    # Remover duplicações antes da tradução
    parts = event_name.split()
    clean_parts = []
    for part in parts:
        if not clean_parts or part != clean_parts[-1]:
            clean_parts.append(part)
    
    return " ".join(clean_parts)

def get_base_sport_name(event_name: str) -> str:
    """Extrai o nome base do esporte do evento"""
    # Remover gênero
    event_name = event_name.replace("Men's ", "").replace("Women's ", "")
    
    # Pegar primeira ou duas primeiras palavras dependendo do caso
    parts = event_name.split()
    if len(parts) >= 2 and (parts[0] + " " + parts[1]) in [
        "Beach Volleyball", "Water Polo", "Table Tennis", "Figure Skating",
        "Speed Skating", "Ice Hockey"
    ]:
        return parts[0] + " " + parts[1]
    
    return parts[0] if parts else event_name

def traduzir_evento(evento: str) -> str:
    """Traduz eventos olímpicos de inglês para português"""
    # Primeiro limpa o nome do evento
    evento = clean_event_name(evento)
    
    # Dicionário de traduções
    traducoes = {
        # Esportes
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
        'Figure Skating': 'Patinação Artística',
        'Speed Skating': 'Patinação de Velocidade',
        'Alpine Skiing': 'Esqui Alpino',
        'Cross-Country Skiing': 'Esqui Cross-Country',
        'Ski Jumping': 'Salto de Esqui',
        'Snowboard': 'Snowboard',
        'Ice Hockey': 'Hóquei no Gelo',
        'Curling': 'Curling',
        'Bobsleigh': 'Bobsled',
        'Luge': 'Luge',
        'Skeleton': 'Skeleton',
        'Biathlon': 'Biatlo',
        
        # Eventos específicos
        'Singles': 'Individual',
        'Doubles': 'Duplas',
        'Mixed Doubles': 'Duplas Mistas',
        'Team': 'Equipe',
        'Relay': 'Revezamento',
        'Marathon': 'Maratona',
        'Race': 'Corrida',
        'Sprint': 'Velocidade',
        'Long Jump': 'Salto em Distância',
        'High Jump': 'Salto em Altura',
        'Triple Jump': 'Salto Triplo',
        'Pole Vault': 'Salto com Vara',
        'Shot Put': 'Arremesso de Peso',
        'Discus Throw': 'Lançamento de Disco',
        'Hammer Throw': 'Lançamento de Martelo',
        'Javelin Throw': 'Lançamento de Dardo',
        'Decathlon': 'Decatlo',
        'Heptathlon': 'Heptatlo',
        'Floor Exercise': 'Solo',
        'Balance Beam': 'Trave',
        'Uneven Bars': 'Barras Assimétricas',
        'Parallel Bars': 'Barras Paralelas',
        'Horizontal Bar': 'Barra Fixa',
        'Rings': 'Argolas',
        'Pommel Horse': 'Cavalo com Alças',
        'Vault': 'Salto',
        'All-Around': 'Individual Geral',
        
        # Estilos de natação
        'Freestyle': 'Livre',
        'Backstroke': 'Costas',
        'Breaststroke': 'Peito',
        'Butterfly': 'Borboleta',
        'Medley': 'Medley',
        
        # Unidades de medida
        'metres': 'metros',
        'm': 'm',
        'km': 'km',
        
        # Categorias de peso
        'Flyweight': 'Peso Mosca',
        'Bantamweight': 'Peso Galo',
        'Featherweight': 'Peso Pena',
        'Lightweight': 'Peso Leve',
        'Welterweight': 'Peso Meio-Médio',
        'Middleweight': 'Peso Médio',
        'Light Heavyweight': 'Peso Meio-Pesado',
        'Heavyweight': 'Peso Pesado',
        'Super Heavyweight': 'Peso Super-Pesado'
    }
    
    # Traduzir usando o dicionário
    for en, pt in sorted(traducoes.items(), key=len, reverse=True):
        evento = evento.replace(en, pt)
    
    # Adicionar gênero no final
    if "Men's" in evento:
        evento = evento.replace("Men's", "").strip() + " Masculino"
    elif "Women's" in evento:
        evento = evento.replace("Women's", "").strip() + " Feminino"
        
    # Limpar espaços extras
    evento = ' '.join(evento.split())
    
    return evento
