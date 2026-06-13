# Safira MusiCloud (Versão Simplificada)

Sistema de gestão para escolas de música. 
Esta versão foi otimizada para rodar com o mínimo de dependências possíveis, usando o banco de dados `sqlite3` nativo do Python.

## Como rodar o sistema

1. **Instalar dependências:**
   No terminal, na raiz do projeto, execute:
   ```bash
   pip install -r requirements.txt
   ```
   *Nota: Agora você só precisa do Flask instalado.*

2. **Iniciar o sistema:**
   Execute o arquivo `run.py` que está na raiz do projeto:
   ```bash
   python run.py
   ```

3. **Acessar e Logar:**
   - Abra o navegador em: `http://127.0.0.1:5000/`
   - **Usuário:** `adm`
   - **Senha:** `adm`

O sistema irá criar automaticamente o banco de dados na primeira execução.
