import streamlit as st

st.set_page_config(page_title="App de Hemoterapia", layout="centered")
modo_estudante = st.sidebar.checkbox("🧑‍🎓 Modo Estudante")

st.title("💉 App de Hemoterapia")
st.markdown("Este aplicativo auxilia na decisão transfusional com base em dados clínicos do paciente.")

# ========================
# Formulário Clínico
# ========================
st.header("📋 Dados do Paciente")

col1, col2 = st.columns(2)

with col1:
    idade = st.number_input("Idade (anos)", min_value=0, max_value=120, step=1)
    peso = st.number_input("Peso (kg)", min_value=1.0, step=0.5, format="%.1f")
    hb = st.number_input("Hemoglobina (g/dL)", min_value=0.0, step=0.1, format="%.1f")
    plaquetas = st.number_input("Plaquetas (mil/mm³)", min_value=0, step=1000)

with col2:
    inr = st.number_input("INR", min_value=0.0, step=0.1, format="%.2f")
    sangramento = st.radio("Há sangramento ativo?", ["Sim", "Não"])
    instabilidade = st.radio("Instabilidade hemodinâmica?", ["Sim", "Não"])

st.header("🔎 Fatores clínicos especiais")

col3, col4 = st.columns(2)
with col3:
    imunossuprimido = st.checkbox("Imunossuprimido?")
    falciforme = st.checkbox("Doença falciforme?")
    aloimunizado = st.checkbox("Aloimunizado?")
with col4:
    reacoes_alergicas = st.checkbox("Reações alérgicas graves recorrentes?")
    uso_imunossupressor = st.checkbox("Uso de imunossupressores sistêmicos?")

# ========================
# Funções clínicas
# ========================

def avaliar_transfusao(hb, plaquetas, inr, sangramento, instabilidade):
    indicacoes = []

    if hb < 7:
        indicacoes.append(("Hemácias", "Hb < 7 g/dL"))
    elif hb < 8 and instabilidade == "Sim":
        indicacoes.append(("Hemácias", "Hb < 8 g/dL com instabilidade hemodinâmica"))

    if plaquetas < 10000:
        indicacoes.append(("Plaquetas", "Contagem < 10.000/mm³"))
    elif plaquetas < 50000 and sangramento == "Sim":
        indicacoes.append(("Plaquetas", "Contagem < 50.000/mm³ com sangramento"))

    if inr > 1.8 and sangramento == "Sim":
        indicacoes.append(("Plasma Fresco Congelado", "INR > 1.8 com sangramento ativo"))

    return indicacoes


def calcular_quantidade_bolsas(tipo, idade, peso, hb, plaquetas, inr, sangramento):
    bolsas = 0
    texto = ""

    if tipo == "Hemácias":
        if idade >= 15:
            alvo_hb = 7.0 if sangramento == "Não" else 8.0
            deficit = alvo_hb - hb
            bolsas = max(1, round(abs(deficit)))
            texto = f"{bolsas} bolsa(s) de concentrado de hemácias"
        else:
            volume_min = int(peso * 10)
            volume_max = int(peso * 15)
            texto = f"{volume_min}–{volume_max} mL de concentrado de hemácias (10–15 mL/kg)"

    elif tipo == "Plaquetas":
        if idade >= 15:
            if plaquetas < 10000:
                texto = "1 unidade de aférese ou 5–10 concentrados randômicos"
            elif sangramento == "Sim":
                texto = "1 unidade de aférese (ou equivalente randômico)"
        else:
            volume_min = int(peso * 5)
            volume_max = int(peso * 10)
            texto = f"{volume_min}–{volume_max} mL de concentrado de plaquetas (5–10 mL/kg)"

    elif tipo == "Plasma Fresco Congelado":
        if idade >= 15:
            volume_total = peso * 10
            bolsas = round(volume_total / 200)
            texto = f"{bolsas} bolsa(s) de plasma fresco congelado"
        else:
            volume_min = int(peso * 10)
            volume_max = int(peso * 15)
            texto = f"{volume_min}–{volume_max} mL de plasma fresco congelado (10–15 mL/kg)"

    return texto


def tipo_concentrado_hemacias_completo(imunossuprimido, falciforme, aloimunizado, reacoes_alergicas, uso_imunossupressor):
    tipo = []

    if reacoes_alergicas:
        tipo.append("lavado")
    if aloimunizado or falciforme:
        tipo.append("fenotipado")
    if imunossuprimido:
        tipo.append("filtrado")
    if uso_imunossupressor:
        tipo.append("irradiado")

    if not tipo:
        return "Concentrado de hemácias padrão"

    return "Concentrado de hemácias " + ", ".join(sorted(set(tipo)))


def condutas_terapeuticas_extras(imunossuprimido, falciforme, reacoes_alergicas):
    orientacoes = []

    if falciforme:
        orientacoes.append("💧 Hidratar antes e após a transfusão para prevenir crises.")
    if reacoes_alergicas:
        orientacoes.append("💊 Considerar pré-medicação com anti-histamínico.")
    if imunossuprimido:
        orientacoes.append("🛡️ Monitorar sinais de GVHD se hemocomponente não for irradiado.")

    return orientacoes

# ========================
# Avaliação Final
# ========================
st.header("✅ Indicação Transfusional e Conduta")

if st.button("🔍 Avaliar"):
    resultados = avaliar_transfusao(hb, plaquetas, inr, sangramento, instabilidade)

    if resultados:
        st.success("💡 Indicações e condutas sugeridas:")
        for hemo, motivo in resultados:
            conduta = calcular_quantidade_bolsas(hemo, idade, peso, hb, plaquetas, inr, sangramento)

            if hemo == "Hemácias":
                tipo = tipo_concentrado_hemacias_completo(imunossuprimido, falciforme, aloimunizado, reacoes_alergicas, uso_imunossupressor)
                st.markdown(f"""**🩸 {hemo}**
- Motivo: _{motivo}_
- Tipo ideal: **{tipo}**
- Conduta: **{conduta}**""")

                orientacoes = condutas_terapeuticas_extras(imunossuprimido, falciforme, reacoes_alergicas)
                if orientacoes:
                    st.markdown("**📌 Condutas complementares recomendadas:**")
                    for o in orientacoes:
                        st.markdown(f"- {o}")

                if modo_estudante:
                    st.info("Hemácias: indicadas em anemias sintomáticas ou Hb < 7 g/dL. Cada unidade eleva Hb em ~1 g/dL.")
            elif hemo == "Plaquetas":
                st.markdown(f"""**🩸 {hemo}**
- Motivo: _{motivo}_
- Conduta: **{conduta}**""")
                if modo_estudante:
                    st.info("Plaquetas: indicadas quando < 10.000/mm³ ou < 50.000/mm³ com sangramento.")
            elif hemo == "Plasma Fresco Congelado":
                st.markdown(f"""**🩸 {hemo}**
- Motivo: _{motivo}_
- Conduta: **{conduta}**""")
                if modo_estudante:
                    st.info("Plasma: indicado para coagulopatias com sangramento ativo.")

    else:
        st.info("❌ Nenhuma indicação clara de transfusão com os dados fornecidos.")

# ========================
# Referências
# ========================
with st.expander("📚 Referências utilizadas"):
    st.markdown("""
- [Manual de Hemoterapia - Ministério da Saúde (PDF)](https://bvsms.saude.gov.br/bvs/publicacoes/manual_hemoterapia_hemocomponentes.pdf)  
- [Carson JL, et al. Cochrane Review - Transfusion thresholds (2016)](https://doi.org/10.1002/14651858.CD002042.pub4)  
- [Yazer MH, et al. Transfusion support for SCD (2019)](https://doi.org/10.1111/trf.15130)  
- [Estcourt LJ, et al. Platelet transfusions in hematologic malignancies (2020)](https://doi.org/10.1111/bjh.16410)  
- Roback JD, et al. Technical Manual. 20th ed. AABB; 2020.
""")
