import sqlite3
from flask import g
import os

DATABASE = 'hospitais.db'

def get_db():
    """Obtém conexão com o banco de dados"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Fecha conexão com o banco de dados"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Inicializa o banco de dados com as tabelas"""
    db = get_db()
    
    # Tabela de bairros
    db.execute('''
        CREATE TABLE IF NOT EXISTS bairros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    ''')
    
    # Tabela de adjacências
    db.execute('''
        CREATE TABLE IF NOT EXISTS adjacencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bairro_origem TEXT NOT NULL,
            bairro_destino TEXT NOT NULL,
            FOREIGN KEY (bairro_origem) REFERENCES bairros(nome),
            FOREIGN KEY (bairro_destino) REFERENCES bairros(nome),
            UNIQUE(bairro_origem, bairro_destino)
        )
    ''')
    
    # Tabela de hospitais
    db.execute('''
        CREATE TABLE IF NOT EXISTS hospitais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            bairro TEXT NOT NULL,
            total_leitos INTEGER NOT NULL,
            leitos_ocupados INTEGER NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            FOREIGN KEY (bairro) REFERENCES bairros(nome)
        )
    ''')
    
    db.commit()

def populate_initial_data():
    """Popula o banco com dados iniciais"""
    db = get_db()
    
    # Verifica se já existe dados
    if db.execute('SELECT COUNT(*) FROM bairros').fetchone()[0] > 0:
        return
    
    # Dados iniciais dos bairros
    bairros_data = [
        ("Pinheiros", -23.5667, -46.6908),
        ("Vila Madalena", -23.5559, -46.6879),
        ("Butantã", -23.5716, -46.7080),
        ("Lapa", -23.5227, -46.6916),
        ("Perdizes", -23.5338, -46.6750),
        ("Barra Funda", -23.5266, -46.6629),
        ("Alto de Pinheiros", -23.5472, -46.7051),
        ("Vila Leopoldina", -23.5271, -46.7285),
        ("Jaguaré", -23.5471, -46.7526),
        ("Vila Sônia", -23.5885, -46.7358),
        ("Morumbi", -23.5961, -46.7097),
        ("Rio Pequeno", -23.5671, -46.7526),
        ("Pompéia", -23.5338, -46.6833),
        ("Jardim Paulista", -23.5653, -46.6608),
        ("Itaim Bibi", -23.5813, -46.6747)
    ]
    
    db.executemany('INSERT OR IGNORE INTO bairros (nome, latitude, longitude) VALUES (?, ?, ?)', bairros_data)
    
    # Adjacências
    adjacencias_data = [
        ("Pinheiros", "Vila Madalena"), ("Pinheiros", "Butantã"), ("Pinheiros", "Alto de Pinheiros"), ("Pinheiros", "Jardim Paulista"),
        ("Vila Madalena", "Pinheiros"), ("Vila Madalena", "Perdizes"),
        ("Butantã", "Pinheiros"), ("Butantã", "Jaguaré"), ("Butantã", "Vila Sônia"),
        ("Lapa", "Perdizes"), ("Lapa", "Barra Funda"),
        ("Perdizes", "Vila Madalena"), ("Perdizes", "Lapa"), ("Perdizes", "Pompéia"),
        ("Barra Funda", "Lapa"),
        ("Alto de Pinheiros", "Pinheiros"),
        ("Vila Leopoldina", "Jaguaré"),
        ("Jaguaré", "Butantã"), ("Jaguaré", "Vila Leopoldina"),
        ("Vila Sônia", "Butantã"), ("Vila Sônia", "Morumbi"),
        ("Morumbi", "Vila Sônia"), ("Morumbi", "Rio Pequeno"),
        ("Rio Pequeno", "Morumbi"),
        ("Pompéia", "Perdizes"),
        ("Jardim Paulista", "Pinheiros"), ("Jardim Paulista", "Itaim Bibi"),
        ("Itaim Bibi", "Jardim Paulista")
    ]
    
    db.executemany('INSERT OR IGNORE INTO adjacencias (bairro_origem, bairro_destino) VALUES (?, ?)', adjacencias_data)
    
    # Hospitais iniciais
    hospitais_data = [
        ("Hospital das Clínicas", "Pinheiros", 50, 50, -23.5573, -46.6685),
        ("UPA Vila Madalena", "Vila Madalena", 20, 20, -23.5559, -46.6879),
        ("Hospital Universitário USP", "Butantã", 60, 45, -23.5665, -46.7404),
        ("UPA Lapa", "Lapa", 30, 30, -23.5227, -46.6916),
        ("Hospital São Camilo", "Perdizes", 40, 39, -23.5338, -46.6750),
        ("Santa Casa Barra Funda", "Barra Funda", 35, 35, -23.5266, -46.6629),
        ("UPA Alto de Pinheiros", "Alto de Pinheiros", 25, 25, -23.5472, -46.7051),
        ("Hospital Vila Penteado", "Vila Leopoldina", 30, 30, -23.5271, -46.7285),
        ("UPA Jaguaré", "Jaguaré", 20, 18, -23.5471, -46.7526),
        ("Hospital Leforte", "Vila Sônia", 45, 44, -23.5885, -46.7358),
        ("Albert Einstein Morumbi", "Morumbi", 50, 50, -23.6001, -46.7144),
        ("UPA Rio Pequeno", "Rio Pequeno", 30, 28, -23.5671, -46.7526),
        ("São Camilo Pompéia", "Pompéia", 40, 40, -23.5338, -46.6833),
        ("Sírio-Libanês Jardins", "Jardim Paulista", 60, 60, -23.5653, -46.6608),
        ("São Luiz Itaim", "Itaim Bibi", 55, 55, -23.5813, -46.6747)
    ]
    
    db.executemany('''
        INSERT OR IGNORE INTO hospitais (nome, bairro, total_leitos, leitos_ocupados, latitude, longitude) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', hospitais_data)
    
    db.commit()

