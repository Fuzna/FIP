import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import streamlit.components.v1 as components

# Configuração da página
st.set_page_config(page_title="RH Digital - DMAE", layout="wide")
st.title("📊 Auditoria de Frequência Inteligente - DMAE")

# Barra lateral para a chave
api_key = st.sidebar.text_input("Insira sua Gemini API Key:", type="password")

def gerar_html_original(analise_ia):
    # Limpeza de markdown para o HTML
    texto_limpo = analise_ia.replace('**', '').replace('###', '').strip()
    
    # Template com CSS e HTML idênticos ao dashboard_fip.html
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <style>
            :root {{
                --dmae-blue: #004a8d;
                --dmae-light: #f4f7f6;
                --success: #28a745;
                --warning: #ffc107;
                --danger: #dc3545;
                --text: #333;
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--dmae-light);
                margin: 0;
                color: var(--text);
            }}

            header {{
                background-color: var(--dmae-blue);
                color: white;
                padding: 1rem 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}

            .container {{
                padding: 2rem;
                max-width: 1200px;
                margin: auto;
            }}

            h1 {{ margin: 0; font-size: 1.5rem; }}
            
            /* Classe idêntica à imagem enviada */
            .servidor-info {{ 
                margin-bottom: 2rem; 
                background: white; 
                padding: 1rem; 
                border-radius: 8px; 
                border-left: 5px solid var(--dmae-blue); 
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }}

            .dashboard-cards {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }}

            .card {{
                padding: 1.5rem;
                border-radius: 10px;
                color: white;
                display: flex;
                flex-direction: column;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}

            .card h2 {{ margin: 0; font-size: 1rem; opacity: 0.9; }}
            .card .value {{ font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0; }}
            .card .footer {{ font-size: 0.8rem; opacity: 0.8; }}

            .bg-success {{ background-color: var(--success); }}
            .bg-warning {{ background-color: var(--warning); color: #856404; }}
            .bg-danger {{ background-color: var(--danger); }}

            .report-box {{
                background: white;
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                line-height: 1.6;
            }}
            .analise-texto {{ white-space: pre-wrap; font-size: 1rem; }}
        </style>
    </head>
    <body>

    <header>
        <h1>DMAE - Analista de Frequência</h1>
        <span>IDG 614 | IDG 513</span>
    </header>

    <div class="container">
        <div class="servidor-info">
            <strong>Servidor:</strong> Ronaldo Paris de Moura (172916001) <br>
            <strong>Lotação:</strong> Diretoria de Proteção Contra Cheias e Drenagem Urb <br>
            <strong>Mês:</strong> Dezembro / 2025
        </div>

        <div class="dashboard-cards">
            <div class="card bg-success">
                <h2>Dias Regulares</h2>
                <div class="value">09</div>
                <div class="footer">Jornada completa e conformidade</div>
            </div>

            <div class="card bg-warning">
                <h2>Justificativas</h2>
                <div class="value">10</div>
                <div class="footer">Cód. 15 e 37 identificados</div>
            </div>

            <div class="card bg-danger">
                <h2>Pendências</h2>
                <div class="value">01</div>
                <div class="footer">Ação requerida via IDG 614/513</div>
            </div>
        </div>

        <div class="report-box">
            <h3 style="color: var(--dmae-blue); border-bottom: 2px solid #eee; padding-bottom: 10px;">
                Detalhamento da Auditoria e Sugestões de Correção
            </h3>
            <div class="analise-texto">{texto_limpo}</div>
        </div>
    </div>

    </body>
    </html>
    """
    return html_template

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-flash-preview')

        uploaded_fip = st.file_uploader("Suba a FIP (PDF)", type="pdf")

        if uploaded_fip:
            with st.spinner('Gerando Dashboard...'):
                reader = PdfReader(uploaded_fip)
                text_fip = "".join([p.extract_text() for p in reader.pages])

                prompt = f"""
                Analise esta FIP como RH do DMAE (IDG 614 e 513).
                1. Liste Ocorrências.
                2. Sugira Correções Técnicas (Ex: lançar Cód 15).
                3. Cite a Base Legal.
                
                Regras: Sem asteriscos (**), linguagem profissional.
                FIP: {text_fip}
                """

                response = model.generate_content(prompt)
                
                # Monta o HTML com o layout fiel à imagem
                html_final = gerar_html_original(response.text)
                
                components.html(html_final, height=800, scrolling=True)

                st.download_button(
                    label="📥 Baixar Dashboard Completo (HTML)",
                    data=html_final,
                    file_name="Dashboard_Auditoria_DMAE.html",
                    mime="text/html"
                )
    except Exception as e:
        st.error(f"Erro: {e}")
else:
    st.info("Insira a API Key para visualizar o Dashboard.")