import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import streamlit.components.v1 as components
import os
import requests
import io

# Configuração da página
st.set_page_config(page_title="RH Digital - DMAE", layout="wide")
st.title("📊 Auditoria de Frequência Inteligente - DMAE")

# Barra lateral para a chave
api_key = st.sidebar.text_input("Insira sua Gemini API Key:", type="password")

def gerar_html_original(analise_ia):
    # Limpeza de markdown para o HTML
    texto_limpo = analise_ia.replace('**', '').replace('###', '').strip()
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <style>
            :root {{
                --dmae-blue: #004a8d; --dmae-light: #f4f7f6;
                --success: #28a745; --warning: #ffc107; --danger: #dc3545; --text: #333;
            }}
            body {{ font-family: 'Segoe UI', sans-serif; background-color: var(--dmae-light); margin: 0; padding: 0; color: var(--text); }}
            header {{ background-color: var(--dmae-blue); color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
            .container {{ padding: 2rem; max-width: 1200px; margin: auto; }}
            .servidor-info {{ margin-bottom: 2rem; background: white; padding: 1.5rem; border-radius: 8px; border-left: 5px solid var(--dmae-blue); box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
            .dashboard-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
            .card {{ padding: 1.5rem; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
            .card h2 {{ margin: 0; font-size: 1rem; opacity: 0.9; }}
            .card .value {{ font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0; }}
            .card .footer {{ font-size: 0.8rem; opacity: 0.8; }}
            .bg-success {{ background-color: var(--success); }}
            .bg-warning {{ background-color: var(--warning); color: #856404; }}
            .bg-danger {{ background-color: var(--danger); }}
            .report-box {{ background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); line-height: 1.7; }}
            .analise-texto {{ white-space: pre-wrap; font-size: 1.05rem; }}
        </style>
    </head>
    <body>
        <header>
            <h1>DMAE - Analista de RH Digital</h1>
            <span>Auditoria Dinâmica IDG 614/513</span>
        </header>
        <div class="container">
            <div class="servidor-info">
                <strong>Status da Auditoria:</strong> Processamento via Biblioteca de Ocorrências <br>
                <strong>Referência Técnica:</strong> IDG 614 e IDG 513 - DMAE
            </div>
            
            <div class="dashboard-cards">
                <div class="card bg-success">
                    <h2>Dias Regulares</h2>
                    <div class="value">Análise</div>
                    <div class="footer">Jornada em conformidade</div>
                </div>
                <div class="card bg-warning">
                    <h2>Justificativas</h2>
                    <div class="value">Verificação</div>
                    <div class="footer">Cód. 15, 37, 77 e outros</div>
                </div>
                <div class="card bg-danger">
                    <h2>Pendências</h2>
                    <div class="value">Ação</div>
                    <div class="footer">Erros de Batida / Faltas</div>
                </div>
            </div>

            <div class="report-box">
                <h2 style="color: var(--dmae-blue); border-bottom: 2px solid #eee; padding-bottom: 10px;">Parecer Técnico Detalhado</h2>
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
        model = genai.GenerativeModel('gemini-1.5-flash')

        uploaded_fip = st.file_uploader("Suba o arquivo PDF da FIP", type="pdf")

        if uploaded_fip:
            with st.spinner('Baixando Normas do GitHub e analisando FIP...'):
                
                # 1. Busca a Biblioteca de Códigos direto do seu repositório GitHub
                url_biblioteca = "https://raw.githubusercontent.com/Fuzna/FIP/main/Ocorr%C3%AAncia%20FIP%20-%20C%C3%B3digos.pdf"
                biblioteca_codigos = ""
                
                try:
                    response_github = requests.get(url_biblioteca)
                    if response_github.status_code == 200:
                        pdf_file = io.BytesIO(response_github.content)
                        reader_ref = PdfReader(pdf_file)
                        for page in reader_ref.pages:
                            biblioteca_codigos += page.extract_text()
                    else:
                        st.sidebar.warning("Aviso: Não foi possível acessar a biblioteca no GitHub. Usando conhecimento geral.")
                except Exception as e:
                    st.sidebar.error(f"Erro ao conectar ao GitHub: {e}")
                
                # 2. Lê a FIP enviada pelo usuário
                reader_fip = PdfReader(uploaded_fip)
                text_fip = ""
                for page in reader_fip.pages:
                    text_fip += page.extract_text()

                # 3. Prompt Inteligente cruzando os dados
                prompt = f"""
                Você é o Especialista de RH do DMAE Porto Alegre.
                Sua base oficial de códigos de ocorrência extraída do PDF normativo é:
                {biblioteca_codigos if biblioteca_codigos else "Use os códigos padrão do DMAE: 1 (Falta), 15 (Justificativa), 37 (Treinamento), 77 (Serviço Externo), 999 (Erro de batida)."}
                
                Analise esta FIP (Folha Individual de Ponto):
                {text_fip}
                
                MISSÃO:
                1. Extraia Nome, Matrícula e Lotação do servidor.
                2. Identifique ocorrências críticas (Faltas, Erros de batida/999, Atrasos).
                3. Sugira a regularização técnica exata usando os códigos da biblioteca acima.
                4. Cite as IDGs 614 e 513 na argumentação para fundamentar o parecer.
                
                REGRAS: Linguagem formal, sem usar asteriscos (**), seja direto ao ponto e técnico.
                """

                response = model.generate_content(prompt)
                html_final = gerar_html_original(response.text)
                
                st.subheader("Resultado da Auditoria Digital")
                components.html(html_final, height=850, scrolling=True)

                st.download_button(
                    label="📥 Baixar Parecer Técnico (HTML)",
                    data=html_final,
                    file_name="Auditoria_RH_DMAE.html",
                    mime="text/html"
                )
    except Exception as e:
        st.error(f"Erro detectado no processamento: {e}")
else:
    st.info("Insira sua Gemini API Key na barra lateral para começar.")
