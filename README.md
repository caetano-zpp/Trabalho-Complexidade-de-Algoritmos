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

2. Ativar o ambiente (PowerShell):

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   Alternativas:
   - CMD: ` .\venv\Scripts\activate.bat `
   - Git Bash / WSL: ` source venv/bin/activate `

3. Instalar dependências:

   ```powershell
   pip install -r requirements.txt
   ```

4. Executar a aplicação Flask (exemplo):

   ```powershell
   set FLASK_APP=app.py; flask run
   ```

Observações:
- O arquivo `requirements.txt` contém dependências mínimas (Flask). Se você adicionar outras bibliotecas, atualize esse arquivo com `pip freeze > requirements.txt` dentro do virtualenv.
- A pasta `venv/` está listada em `.gitignore` para não ser versionada.