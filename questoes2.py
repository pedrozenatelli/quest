# app.py
import streamlit as st
import openai
import sqlite3
import time
import streamlit as st
openai.api_key = st.secrets["openai"]["api_key"]

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
    openai.api_key = st.secrets["openai"]["api_key"]

    prompt = f"""
Você é um especialista em elaboração de questões para concursos públicos.

Sua função é criar questões de múltipla escolha, baseadas exclusivamente no texto da lei fornecida.

Instruções:
Crie exatamente 10 questões de múltipla escolha.

Cada enunciado deve começar com algo semelhante a uma destas variações, substituindo corretamente pela lei fornecida na variável nome_lei (exemplo: Constituição Federal):

"Sobre a/o <b>{nome_lei}</b>, assinale a alternativa correta/incorreta."

"De acordo com a/o <b>{nome_lei}</b>, assinale a alternativa correta/incorreta."

"Acerca da/do <b>{nome_lei}</b>, assinale a alternativa correta/incorreta."

Alterne entre instruções de "assinale a alternativa correta" e "assinale a alternativa incorreta".

As alternativas devem ser nomeadas como A, B, C e D, mas **NÃO** inclua "A)" ou letras antes do texto da alternativa. Em vez disso, insira uma marcação invisível para cada uma, como:

###ALTERNATIVA_A###
texto da alternativa A

###ALTERNATIVA_B###
texto da alternativa B

###ALTERNATIVA_C###
texto da alternativa C

###ALTERNATIVA_D###
texto da alternativa D

O enunciado deve ser precedido por:
###ENUNCIADO###

Sempre informe o gabarito e a explicação com as seguintes marcações:

###GABARITO###
<b>GABARITO:</b> [Letra correta]

Após a [Letra correta] do GABARITO, salte UMA linha

<b>EXPLICAÇÃO:</b> Breve justificativa mencionando o artigo da lei que fundamenta a resposta.

Após a explicação, salte UMA linha e insira o texto literal com a seguinte marcação:

<span style=\"background-color:#ffffcc\">[TEXTO LITERAL]</span>

Essa estrutura permitirá exportar para uma planilha com as seguintes colunas:
COLUNA 1: ENUNCIADO
COLUNA 2: EXPLICAÇÃO
COLUNA 3: ALTERNATIVA A
COLUNA 4: ALTERNATIVA B
COLUNA 5: ALTERNATIVA C
COLUNA 6: ALTERNATIVA D
COLUNA 7: LETRA DO GABARITO (A, B, C ou D)
COLUNA 8: TEXTO DA EXPLICAÇÃO

Não invente dados. Use apenas o texto real da lei fornecida. Seja fiel ao conteúdo legal ao formular tanto as alternativas quanto o gabarito.

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