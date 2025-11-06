# SOS Ambulância

Um sistema web para localização de hospitais e UPAs com vagas disponíveis na região.

## Funcionalidades Principais

### 1. Localização Inteligente
- **Detecção Automática**: Sistema detecta automaticamente a localização do usuário
- **Cálculo de Proximidade**: Identifica o bairro mais próximo com base nas coordenadas
- **Seleção Manual**: Opção para selecionar manualmente o bairro desejado

### 2. Interface Intuitiva
- **Design Responsivo**: Interface adaptável a diferentes dispositivos
- **Feedback Visual**: Mensagens claras sobre o status da localização
- **Navegação Simplificada**: Processo de busca em poucos cliques

### 3. Busca de Hospitais
- **Mapeamento de Vagas**: Visualização de hospitais com vagas disponíveis
- **Informações em Tempo Real**: Status atualizado das unidades de saúde
- **Direcionamento Eficiente**: Encaminhamento para o hospital mais adequado

## Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Geolocalização**: API de Geolocalização do Navegador
- **Mapas**: Integração com serviços de mapas para visualização

## Como Funciona

1. **Início**
   - Usuário acessa a página inicial
   - Sistema solicita permissão para acessar localização

2. **Detecção de Localização**
   - Coordenadas são capturadas automaticamente
   - Sistema calcula o bairro mais próximo
   - Usuário pode confirmar ou escolher outro bairro

3. **Busca de Hospitais**
   - Sistema processa a localização selecionada
   - Exibe mapa com hospitais disponíveis
   - Fornece informações sobre vagas e serviços

## Benefícios

- **Rapidez**: Localização imediata de hospitais com vagas
- **Precisão**: Cálculo exato de distâncias e disponibilidade
- **Facilidade**: Interface simples e intuitiva
- **Confiabilidade**: Informações atualizadas em tempo real

## Impacto Social

O sistema contribui para:
- Redução do tempo de busca por atendimento médico
- Melhor distribuição de pacientes entre unidades de saúde
- Otimização do uso de recursos hospitalares
- Maior eficiência no atendimento de emergências

## Setup (Configuração do ambiente)

Siga estes passos para preparar e ativar o ambiente de desenvolvimento (Windows - PowerShell):

1. Criar o ambiente virtual (já criado se você seguiu os passos do projeto):

   ```powershell
   python -m venv venv
   ```

# SOS Ambulância — Apresentação do Projeto

Uma aplicação web simples para localizar hospitais e UPAs com vagas disponíveis, priorizando proximidade e disponibilidade de leitos.

Resumo rápido
- Backend: Flask (Python) com SQLite (Flask-SQLAlchemy)
- Frontend: HTML/CSS/JS (templates Jinja2)
- Funcionalidade principal: localizar a unidade mais adequada a partir do bairro do usuário (BFS até 3 bairros, prioriza leitos livres)

Principais componentes
- `app.py` — rotações Flask, lógica de busca (`encontrar_hospital`), modelos SQLAlchemy (`Bairro`, `Hospital`, `Adjacencia`) e endpoints (incluindo `/api/update_occupancy`).
- `templates/` — páginas: `home.html`, `mapa.html`, `admin.html`, `admin_edit.html`, `login.html`.
- `static/` — estilos e scripts; `static/style.css` contém as variáveis de cor e regras visuais.
- `data.db` — banco SQLite gerado localmente (não versionado).

Como o algoritmo indica unidade
- Busca em largura (BFS) a partir do bairro de origem até profundidade 3.
- Em cada nível (mesma distância em bairros) seleciona-se a unidade com maior número de leitos livres.
- Se nenhuma unidade com leito livre for encontrada até 3 bairros, escolhe-se a unidade menos sobrecarregada entre as pesquisadas.

Execução (rápido — PowerShell)
1. Ativar venv (na raiz do projeto):

```powershell
.\venv\\Scripts\\Activate.ps1
```

2. Instalar dependências (se necessário):

```powershell
pip install -r requirements.txt
```

3. Rodar a aplicação (script incluído):

```powershell
.\run.ps1
# ou: set FLASK_APP=app.py; flask run
```

O app inicializa `data.db` automaticamente na primeira execução (seed com dados de exemplo).

Administração (CRUD)
- Rota admin: `/admin` — lista hospitais e permite adicionar, editar e excluir.
- Credenciais padrão da tela de login (apenas para demo): `admin` / `1234`.

API útil
- `POST /api/update_occupancy` — atualizar ocupação de um hospital (JSON: `{ "hospital_id": <id>, "leitos_ocupados": <n> }`).

Editar dados
- Pelo painel admin `/admin` (recomendado).
- Via Flask shell ou scripts Python: há exemplos em `scripts/` (pode-se adicionar `seed_db.py`, `add_hospital.py`).
- Diretamente no DB: usar `sqlite3` ou DB Browser for SQLite para inspecionar/editar `data.db`.

Extras e recomendações
- Em produção mova o SQLite para Postgres e proteja as rotas administrativas.
- Remover a inicialização automática do DB de `app.py` e usar um script de seed separado para controle.

Contato / Apresentação
- Repositório: https://github.com/caetano-zpp/Trabalho-Complexidade-de-Algoritmos.git
- Se quiser, eu adapto o README para uma versão em slides ou incluirei comandos de demonstração resumidos.

---
Pequena nota: o código foi preparado para apresentação — se desejar, faço hardening (autenticação, validação, logs) e testes unitários.
