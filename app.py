from flask import Flask, render_template, request, redirect, url_for, session
from collections import deque
import database

app = Flask(__name__)
app.secret_key = 'sua-chave-secreta-aqui-mude-em-producao'  # Mude para uma chave segura em produção

# Registrar função para fechar DB
app.teardown_appcontext(database.close_db)

# Inicializar banco de dados na primeira execução
with app.app_context():
    database.init_db()
    database.populate_initial_data()

# Função auxiliar para calcular a pontuação de um hospital
def calcular_pontuacao_hospital(ocupacao, distancia):
    # Normaliza ocupação (0 = lotado, 1 = vazio)
    taxa_ocupacao = 1 - ocupacao
    
    # Normaliza distância (0 = longe, 1 = perto)
    # Usa distância máxima + 1 para evitar divisão por zero e valores negativos
    taxa_proximidade = max(0, 1 - (distancia / 4))
    
    # Peso maior para ocupação (0.6) do que para distância (0.4)
    return (0.6 * taxa_ocupacao) + (0.4 * taxa_proximidade)

# Função de busca atualizada para usar o banco
def encontrar_hospital(bairro_inicial):
    db = database.get_db()
    visitados = set()
    fila = deque([(bairro_inicial, 0)])
    opcoes_hospitais = []
    
    while fila:
        bairro, dist = fila.popleft()
        if dist > 3:
            break
        if bairro in visitados:
            continue
        visitados.add(bairro)
        
        # Busca hospitais do bairro no banco
        hospitais_bairro = db.execute('''
            SELECT nome, bairro, total_leitos, leitos_ocupados, latitude, longitude
            FROM hospitais WHERE bairro = ?
        ''', (bairro,)).fetchall()
        
        for hospital in hospitais_bairro:
            total = hospital['total_leitos']
            ocupados = hospital['leitos_ocupados']
            taxa_ocupacao = ocupados / total if total > 0 else 1
            pontuacao = calcular_pontuacao_hospital(taxa_ocupacao, dist)
            
            opcoes_hospitais.append({
                'nome': hospital['nome'],
                'ocupacao': taxa_ocupacao,
                'distancia': dist,
                'pontuacao': pontuacao,
                'total': total,
                'ocupados': ocupados,
                'coords': [hospital['latitude'], hospital['longitude']]
            })
        
        # Busca adjacências no banco
        adjacentes = db.execute('''
            SELECT bairro_destino FROM adjacencias WHERE bairro_origem = ?
        ''', (bairro,)).fetchall()
        
        for adj in adjacentes:
            adj_nome = adj['bairro_destino']
            if adj_nome not in visitados:
                fila.append((adj_nome, dist + 1))
                visitados.add(adj_nome)
    
    if opcoes_hospitais:
        # Ordena por pontuação (maior primeiro)
        opcoes_hospitais.sort(key=lambda x: x['pontuacao'], reverse=True)
        melhor_opcao = opcoes_hospitais[0]
        
        # Retorna não só o melhor hospital, mas todas as opções para exibir no mapa
        return melhor_opcao['nome'], opcoes_hospitais
    
    return "Nenhum hospital encontrado", []

# Função auxiliar para obter bairros do banco
def get_bairros():
    db = database.get_db()
    bairros = db.execute('SELECT nome, latitude, longitude FROM bairros').fetchall()
    return {b['nome']: [b['latitude'], b['longitude']] for b in bairros}

# ROTAS EXISTENTES
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario', '').strip()
    senha = request.form.get('senha', '')
    
    if usuario == 'admin' and senha == '1234':
        session['usuario'] = usuario
        return redirect(url_for('home'))
    return render_template('login.html', erro="Usuário ou senha incorretos")

@app.route('/home')
def home():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    coordenadas_bairros = get_bairros()
    bairros = list(coordenadas_bairros.keys())
    
    return render_template('home.html', 
                         bairros=bairros, 
                         coordenadas_bairros=coordenadas_bairros)

@app.route('/mapa', methods=['POST'])
def mapa():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    try:
        bairro_origem = request.form.get('bairro', '').strip()
        coordenadas_bairros = get_bairros()
        
        if not bairro_origem or bairro_origem not in coordenadas_bairros:
            bairros = list(coordenadas_bairros.keys())
            return render_template('home.html', 
                                 bairros=bairros, 
                                 coordenadas_bairros=coordenadas_bairros,
                                 erro="Bairro inválido. Por favor, selecione um bairro válido.")
        
        hospital_nome, opcoes_hospitais = encontrar_hospital(bairro_origem)
        bairro_coord = coordenadas_bairros.get(bairro_origem)
        
        return render_template('mapa.html', 
                             bairro=bairro_origem, 
                             hospital=hospital_nome,
                             bairro_coord=bairro_coord,
                             hospitais=opcoes_hospitais)
    except Exception as e:
        app.logger.error(f"Erro ao processar mapa: {str(e)}")
        coordenadas_bairros = get_bairros()
        bairros = list(coordenadas_bairros.keys())
        return render_template('home.html', 
                             bairros=bairros, 
                             coordenadas_bairros=coordenadas_bairros,
                             erro="Erro ao processar solicitação. Tente novamente.")

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

# NOVAS ROTAS PARA ADMINISTRAÇÃO
@app.route('/admin')
def admin():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    db = database.get_db()
    hospitais = db.execute('''
        SELECT h.id, h.nome, h.bairro, h.total_leitos, h.leitos_ocupados, 
               h.latitude, h.longitude, b.nome as bairro_nome
        FROM hospitais h
        JOIN bairros b ON h.bairro = b.nome
        ORDER BY h.nome
    ''').fetchall()
    
    bairros = db.execute('SELECT nome FROM bairros ORDER BY nome').fetchall()
    
    return render_template('admin.html', 
                         hospitais=hospitais, 
                         bairros=[b['nome'] for b in bairros])

@app.route('/admin/hospital/novo', methods=['POST'])
def criar_hospital():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    try:
        db = database.get_db()
        db.execute('''
            INSERT INTO hospitais (nome, bairro, total_leitos, leitos_ocupados, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            request.form['nome'],
            request.form['bairro'],
            int(request.form['total_leitos']),
            int(request.form['leitos_ocupados']),
            float(request.form['latitude']),
            float(request.form['longitude'])
        ))
        db.commit()
        return redirect(url_for('admin'))
    except Exception as e:
        app.logger.error(f"Erro ao criar hospital: {str(e)}")
        return f"Erro ao criar hospital: {str(e)}", 400

@app.route('/admin/hospital/<int:hospital_id>/editar', methods=['POST'])
def editar_hospital(hospital_id):
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    try:
        db = database.get_db()
        db.execute('''
            UPDATE hospitais 
            SET nome = ?, bairro = ?, total_leitos = ?, leitos_ocupados = ?, 
                latitude = ?, longitude = ?
            WHERE id = ?
        ''', (
            request.form['nome'],
            request.form['bairro'],
            int(request.form['total_leitos']),
            int(request.form['leitos_ocupados']),
            float(request.form['latitude']),
            float(request.form['longitude']),
            hospital_id
        ))
        db.commit()
        return redirect(url_for('admin'))
    except Exception as e:
        app.logger.error(f"Erro ao editar hospital: {str(e)}")
        return f"Erro ao editar hospital: {str(e)}", 400

@app.route('/admin/hospital/<int:hospital_id>/deletar', methods=['POST'])
def deletar_hospital(hospital_id):
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    try:
        db = database.get_db()
        db.execute('DELETE FROM hospitais WHERE id = ?', (hospital_id,))
        db.commit()
        return redirect(url_for('admin'))
    except Exception as e:
        app.logger.error(f"Erro ao deletar hospital: {str(e)}")
        return f"Erro ao deletar hospital: {str(e)}", 400

if __name__ == '__main__':
    app.run(debug=True)
