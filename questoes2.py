# app.py
import streamlit as st
import openai
import sqlite3
import time

# Configurações iniciais do Streamlit
st.set_page_config(page_title="Gerador de Questões de Concurso", page_icon="📝", layout="centered")

# Conectar ao banco SQLite
conn = sqlite3.connect('questoes.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS questoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_lei TEXT,
        texto_lei TEXT,
        questoes_geradas TEXT,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Função para salvar no banco
def salvar_questao(nome_lei, texto_lei, questoes_geradas):
    c.execute('''
        INSERT INTO questoes (nome_lei, texto_lei, questoes_geradas)
        VALUES (?, ?, ?)
    ''', (nome_lei, texto_lei, questoes_geradas))
    conn.commit()

# Função para gerar questões com OpenAI
def gerar_questoes(texto_lei, nome_lei):
    openai.api_key = "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"

    prompt = f"""
Você é um especialista em elaboração de questões para concursos públicos.

Sua função é criar questões de múltipla escolha, baseadas exclusivamente no texto da lei fornecida.

Instruções:
- 10 questões.
- Varie entre "marque a alternativa correta" e "marque a alternativa incorreta".
- Sempre informe o GABARITO e explique brevemente citando o artigo da lei.
- NÃO invente informações.

Texto da Lei:
{texto_lei}
"""
    resposta = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um criador de questões para concursos."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return resposta.choices[0].message.content

# Interface Streamlit
st.title("📝 Gerador de Questões para Concursos Públicos")
st.write("Cole abaixo o texto da Lei e gere questões automaticamente!")

nome_lei = st.text_input("📚 Nome da Lei:", placeholder="Exemplo: Constituição Federal")
texto_lei = st.text_area("📜 Cole aqui o texto da Lei:", height=300, placeholder="Cole o texto aqui e gere suas questões...")

# Botão para gerar questões
if st.button("🚀 Gerar Questões"):
    if nome_lei.strip() == "" or texto_lei.strip() == "":
        st.warning("⚠️ Preencha o nome da lei e cole o texto!")
    else:
        with st.spinner("Gerando questões, aguarde..."):
            try:
                questoes_geradas = gerar_questoes(texto_lei, nome_lei)
                salvar_questao(nome_lei, texto_lei, questoes_geradas)

                st.success("✅ Questões geradas com sucesso!")
                st.text_area("🎯 Questões Geradas:", value=questoes_geradas, height=600)

            except Exception as e:
                st.error(f"❌ Erro ao gerar questões: {e}")

# Rodapé
st.markdown("---")
st.caption("© 2025 - Gerador de Questões Automáticas")
