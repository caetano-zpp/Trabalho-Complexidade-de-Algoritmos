from flask import Flask, render_template, request, redirect, url_for, jsonify
from collections import deque
import os

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration (SQLite for demo / presentation)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Coordenadas dos bairros
coordenadas_bairros = {
    "Pinheiros": [-23.5667, -46.6908],
    "Vila Madalena": [-23.5559, -46.6879],
    "Butantã": [-23.5716, -46.7080],
    "Lapa": [-23.5227, -46.6916],
    "Perdizes": [-23.5338, -46.6750],
    "Barra Funda": [-23.5266, -46.6629],
    "Alto de Pinheiros": [-23.5472, -46.7051],
    "Vila Leopoldina": [-23.5271, -46.7285],
    "Jaguaré": [-23.5471, -46.7526],
    "Vila Sônia": [-23.5885, -46.7358],
    "Morumbi": [-23.5961, -46.7097],
    "Rio Pequeno": [-23.5671, -46.7526],
    "Pompéia": [-23.5338, -46.6833],
    "Jardim Paulista": [-23.5653, -46.6608],
    "Itaim Bibi": [-23.5813, -46.6747]
}

# Lista de bairros
bairros = list(coordenadas_bairros.keys())

#Conexões (bairros adjacentes)
adjacencias = {
    "Pinheiros": ["Vila Madalena", "Butantã", "Alto de Pinheiros", "Jardim Paulista"],
    "Vila Madalena": ["Pinheiros", "Perdizes"],
    "Butantã": ["Pinheiros", "Jaguaré", "Vila Sônia"],
    "Lapa": ["Perdizes", "Barra Funda"],
    "Perdizes": ["Vila Madalena", "Lapa", "Pompéia"],
    "Barra Funda": ["Lapa"],
    "Alto de Pinheiros": ["Pinheiros"],
    "Vila Leopoldina": ["Jaguaré"],
    "Jaguaré": ["Butantã", "Vila Leopoldina"],
    "Vila Sônia": ["Butantã", "Morumbi"],
    "Morumbi": ["Vila Sônia", "Rio Pequeno"],
    "Rio Pequeno": ["Morumbi"],
    "Pompéia": ["Perdizes"],
    "Jardim Paulista": ["Pinheiros", "Itaim Bibi"],
    "Itaim Bibi": ["Jardim Paulista"]
}

#Hospitais (nome, bairro, total de leitos, ocupados, coordenadas)
hospitais = [
    ("Hospital das Clínicas", "Pinheiros", 50, 50, [-23.5573, -46.6685]),
    ("UPA Vila Madalena", "Vila Madalena", 20, 20, [-23.5559, -46.6879]),
    ("Hospital Universitário USP", "Butantã", 60, 45, [-23.5665, -46.7404]),
    ("UPA Lapa", "Lapa", 30, 30, [-23.5227, -46.6916]),
    ("Hospital São Camilo", "Perdizes", 40, 39, [-23.5338, -46.6750]),
    ("Santa Casa Barra Funda", "Barra Funda", 35, 35, [-23.5266, -46.6629]),
    ("UPA Alto de Pinheiros", "Alto de Pinheiros", 25, 25, [-23.5472, -46.7051]),
    ("Hospital Vila Penteado", "Vila Leopoldina", 30, 30, [-23.5271, -46.7285]),
    ("UPA Jaguaré", "Jaguaré", 20, 18, [-23.5471, -46.7526]),
    ("Hospital Leforte", "Vila Sônia", 45, 44, [-23.5885, -46.7358]),
    ("Albert Einstein Morumbi", "Morumbi", 50, 50, [-23.6001, -46.7144]),
    ("UPA Rio Pequeno", "Rio Pequeno", 30, 28, [-23.5671, -46.7526]),
    ("São Camilo Pompéia", "Pompéia", 40, 40, [-23.5338, -46.6833]),
    ("Sírio-Libanês Jardins", "Jardim Paulista", 60, 60, [-23.5653, -46.6608]),
    ("São Luiz Itaim", "Itaim Bibi", 55, 55, [-23.5813, -46.6747])
]


# ---------- SQLAlchemy models ----------
class Bairro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), unique=True, nullable=False)
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)
    hospitais = db.relationship('Hospital', backref='bairro', lazy=True)

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    bairro_id = db.Column(db.Integer, db.ForeignKey('bairro.id'), nullable=False)
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)
    leitos_totais = db.Column(db.Integer, default=0)
    leitos_ocupados = db.Column(db.Integer, default=0)

class Adjacencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bairro_id = db.Column(db.Integer, db.ForeignKey('bairro.id'), nullable=False)
    adj_bairro_id = db.Column(db.Integer, db.ForeignKey('bairro.id'), nullable=False)


def init_db(seed=True):
    """Criar o banco (data.db) e popular com os dados em memória se não existir."""
    if not os.path.exists('data.db'):
        db.create_all()
        if seed:
            # popular bairros
            for nome, coord in coordenadas_bairros.items():
                if not Bairro.query.filter_by(nome=nome).first():
                    b = Bairro(nome=nome, lat=float(coord[0]), lon=float(coord[1]))
                    db.session.add(b)
            db.session.commit()

            # popular hospitais
            for nome, bnome, total, ocupados, coords in hospitais:
                b = Bairro.query.filter_by(nome=bnome).first()
                if b:
                    if not Hospital.query.filter_by(nome=nome, bairro_id=b.id).first():
                        h = Hospital(nome=nome, bairro_id=b.id, lat=coords[0], lon=coords[1], leitos_totais=total, leitos_ocupados=ocupados)
                        db.session.add(h)
            db.session.commit()

            # popular adjacências
            for origem, lista in adjacencias.items():
                b_origem = Bairro.query.filter_by(nome=origem).first()
                if not b_origem:
                    continue
                for destino in lista:
                    b_dest = Bairro.query.filter_by(nome=destino).first()
                    if b_dest:
                        # evitar duplicatas
                        exists = Adjacencia.query.filter_by(bairro_id=b_origem.id, adj_bairro_id=b_dest.id).first()
                        if not exists:
                            a = Adjacencia(bairro_id=b_origem.id, adj_bairro_id=b_dest.id)
                            db.session.add(a)
            db.session.commit()


def carregar_estruturas_do_db():
    """Retorna (coordenadas_bairros, hospitais_list, adjacencias_dict) a partir do DB."""
    coord = {}
    adj = {}
    hosp_list = []

    for b in Bairro.query.all():
        coord[b.nome] = [b.lat, b.lon]
        adj[b.nome] = []
    # adjacencias
    for a in Adjacencia.query.all():
        origem = Bairro.query.get(a.bairro_id)
        destino = Bairro.query.get(a.adj_bairro_id)
        if origem and destino:
            adj.setdefault(origem.nome, []).append(destino.nome)

    # hospitais
    for h in Hospital.query.all():
        bairro = Bairro.query.get(h.bairro_id)
        if bairro:
            hosp_list.append((h.nome, bairro.nome, h.leitos_totais, h.leitos_ocupados, [h.lat, h.lon, h.id]))

    return coord, hosp_list, adj


# Inicializa o DB automaticamente se não existir (útil para demonstração)
if not os.path.exists('data.db'):
    init_db(seed=True)


# Função auxiliar para calcular a pontuação de um hospital
def calcular_pontuacao_hospital(ocupacao, distancia):
    # Normaliza ocupação (0 = lotado, 1 = vazio)
    taxa_ocupacao = 1 - ocupacao
    
    # Normaliza distância (0 = longe, 1 = perto)
    # Assume que 3 é a distância máxima
    taxa_proximidade = 1 - (distancia / 3)
    
    # Peso maior para ocupação (0.6) do que para distância (0.4)
    return (0.6 * taxa_ocupacao) + (0.4 * taxa_proximidade)
# FUNÇÃO DE BUSCA (aceita estruturas em memória ou carregadas do DB)
def encontrar_hospital(bairro_inicial, hospitais_list=None, adjacencias_dict=None, max_depth=3):
    """Busca por hospital começando em bairro_inicial, procurando até max_depth bairros.
    hospitais_list: lista de tuplas (nome, bairro, total, ocupados, coords)
    adjacencias_dict: dict bairro -> lista de adjacentes
    """
    if hospitais_list is None:
        hospitais_list = hospitais
    if adjacencias_dict is None:
        adjacencias_dict = adjacencias

    visitados = set()
    fila = deque([(bairro_inicial, 0)])
    opcoes_hospitais = []

    while fila:
        bairro, dist = fila.popleft()
        if dist > max_depth:
            break
        visitados.add(bairro)

        # Verifica todos os hospitais deste bairro
        for entry in hospitais_list:
            # entry pode vir do DB como (nome, bairro, total, ocupados, [lat, lon, id])
            nome = entry[0]
            b = entry[1]
            total = entry[2]
            ocupados = entry[3]
            coords = entry[4]
            hosp_id = None
            if isinstance(coords, (list, tuple)) and len(coords) >= 3:
                # quando carregado do DB incluímos id como terceiro elemento
                hosp_id = coords[2]
                coords = coords[:2]

            if b == bairro:
                taxa_ocupacao = ocupados / total if total > 0 else 1.0
                pontuacao = calcular_pontuacao_hospital(taxa_ocupacao, dist)
                opcoes_hospitais.append({
                    'nome': nome,
                    'ocupacao': taxa_ocupacao,
                    'distancia': dist,
                    'pontuacao': pontuacao,
                    'total': total,
                    'ocupados': ocupados,
                    'coords': coords,
                    'id': hosp_id
                })

        # Adiciona bairros adjacentes
        for adj in adjacencias_dict.get(bairro, []):
            if adj not in visitados:
                fila.append((adj, dist + 1))

    if opcoes_hospitais:
        # Ordena por pontuação (maior primeiro)
        opcoes_hospitais.sort(key=lambda x: x['pontuacao'], reverse=True)
        melhor_opcao = opcoes_hospitais[0]

        # Retorna não só o melhor hospital, mas todas as opções para exibir no mapa
        return melhor_opcao['nome'], opcoes_hospitais

    return "Nenhum hospital encontrado", []


#ROTAS
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    senha = request.form['senha']

    if usuario == 'admin' and senha == '1234':
        return redirect(url_for('home'))
    return render_template('login.html', erro="Usuário ou senha incorretos")

@app.route('/home')
def home():
    # Se o DB existir, carregue bairros dinamicamente
    if os.path.exists('data.db'):
        coord_db, hosp_db, adj_db = carregar_estruturas_do_db()
        bairros_db = list(coord_db.keys())
        return render_template('home.html', bairros=bairros_db, coordenadas_bairros=coord_db)

    return render_template('home.html', bairros=bairros, coordenadas_bairros=coordenadas_bairros)

@app.route('/mapa', methods=['POST'])
def mapa():
    bairro_origem = request.form['bairro']
    # Carregar dados do DB se existir, senão usar estruturas em memória
    if os.path.exists('data.db'):
        coord_db, hosp_db, adj_db = carregar_estruturas_do_db()
        hospital_nome, opcoes_hospitais = encontrar_hospital(bairro_origem, hospitais_list=hosp_db, adjacencias_dict=adj_db)
        bairro_coord = coord_db.get(bairro_origem)
    else:
        hospital_nome, opcoes_hospitais = encontrar_hospital(bairro_origem)
        bairro_coord = coordenadas_bairros.get(bairro_origem)

    return render_template('mapa.html', bairro=bairro_origem, hospital=hospital_nome, bairro_coord=bairro_coord, hospitais=opcoes_hospitais)


# API para atualizar ocupação de um hospital (espera JSON: {"hospital_id": 1, "leitos_ocupados": 12})
@app.route('/api/update_occupancy', methods=['POST'])
def update_occupancy():
    if not os.path.exists('data.db'):
        return jsonify({"error": "DB não inicializado"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON inválido"}), 400

    hid = data.get('hospital_id')
    if not hid:
        return jsonify({"error": "hospital_id requerido"}), 400

    h = Hospital.query.get(hid)
    if not h:
        return jsonify({"error": "hospital não encontrado"}), 404

    try:
        h.leitos_ocupados = int(data.get('leitos_ocupados', h.leitos_ocupados))
        db.session.commit()
        return jsonify({"ok": True, "hospital_id": h.id, "ocupados": h.leitos_ocupados})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
