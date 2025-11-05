from flask import Flask, render_template, request, redirect, url_for
from collections import deque

app = Flask(__name__)

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


# Função auxiliar para calcular a pontuação de um hospital
def calcular_pontuacao_hospital(ocupacao, distancia):
    # Normaliza ocupação (0 = lotado, 1 = vazio)
    taxa_ocupacao = 1 - ocupacao
    
    # Normaliza distância (0 = longe, 1 = perto)
    # Assume que 3 é a distância máxima
    taxa_proximidade = 1 - (distancia / 3)
    
    # Peso maior para ocupação (0.6) do que para distância (0.4)
    return (0.6 * taxa_ocupacao) + (0.4 * taxa_proximidade)

#FUNÇÃO DE BUSCA
def encontrar_hospital(bairro_inicial):
    visitados = set()
    fila = deque([(bairro_inicial, 0)])
    opcoes_hospitais = []
    
    while fila:
        bairro, dist = fila.popleft()
        if dist > 3:
            break
        visitados.add(bairro)
        
        # Verifica todos os hospitais deste bairro
        for nome, b, total, ocupados, coords in hospitais:
            if b == bairro:
                taxa_ocupacao = ocupados / total
                pontuacao = calcular_pontuacao_hospital(taxa_ocupacao, dist)
                opcoes_hospitais.append({
                    'nome': nome,
                    'ocupacao': taxa_ocupacao,
                    'distancia': dist,
                    'pontuacao': pontuacao,
                    'total': total,
                    'ocupados': ocupados,
                    'coords': coords
                })
        
        # Adiciona bairros adjacentes
        for adj in adjacencias.get(bairro, []):
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
    return render_template('home.html', 
                         bairros=bairros, 
                         coordenadas_bairros=coordenadas_bairros)

@app.route('/mapa', methods=['POST'])
def mapa():
    bairro_origem = request.form['bairro']
    hospital_nome, opcoes_hospitais = encontrar_hospital(bairro_origem)
    bairro_coord = coordenadas_bairros.get(bairro_origem)
    
    return render_template('mapa.html', 
                         bairro=bairro_origem, 
                         hospital=hospital_nome,
                         bairro_coord=bairro_coord,
                         hospitais=opcoes_hospitais)


if __name__ == '__main__':
    app.run(debug=True)
