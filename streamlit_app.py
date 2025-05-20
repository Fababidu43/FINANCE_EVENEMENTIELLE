import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from io import BytesIO

# --- Configuration de la page ---
st.set_page_config(
    page_title="ERP Événementiel",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("📊 ERP de Gestion Événementielle")

# --- Sidebar : paramètres communs ---
with st.sidebar.expander("⚙️ Hypothèses Générales", expanded=True):
    brasero_cost = st.number_input("Coût initial Brasero (€)", value=1500, help="Investissement matériel brasero")
    brasero_life = st.number_input("Durée d'amortissement Brasero (ans)", value=5)
    brasero_days = st.number_input("Jours loués/an (Brasero)", value=50)
    chiffres_cost = st.number_input("Coût initial Chiffres (€)", value=1000)
    chiffres_life = st.number_input("Durée d'amortissement Chiffres (ans)", value=5)
    chiffres_rate = st.slider("Taux d’occupation Chiffres (%)", 0, 100, 20) / 100
    chiffres_days = chiffres_rate * 365

with st.sidebar.expander("🗂 Répartition & tarifs", expanded=False):
    st.subheader("Brasero packs %")
    b_pack1 = st.number_input("Pack1 (%)", 40) / 100
    b_pack2 = st.number_input("Pack2 (%)", 40) / 100
    b_pack3 = st.number_input("Pack3 (%)", 20) / 100
    st.subheader("Chiffres packs %")
    c_pack1 = st.number_input("Pack1 (%)", 60) / 100
    c_pack2 = st.number_input("Pack2 (%)", 30) / 100
    c_pack3 = st.number_input("Pack3 (%)", 10) / 100
    st.subheader("Tarifs journaliers (€)")
    t_b1 = st.number_input("Brasero P1", 150)
    t_b2 = st.number_input("Brasero P2", 300)
    t_b3 = st.number_input("Brasero P3", 400)
    t_c1 = st.number_input("Chiffres P1", 50)
    t_c2 = st.number_input("Chiffres P2", 100)
    t_c3 = st.number_input("Chiffres P3", 140)

with st.sidebar.expander("🧾 Charges & prélèvements", expanded=False):
    social_rate = st.number_input("Cotisations (%)", 21.2) / 100
    lib_rate    = st.number_input("IR libératoire (%)", 1.7) / 100
    cpf_rate    = st.number_input("Formation (%)", 0.3) / 100
    threshold   = st.number_input("Seuil AE (€)", 77700)

with st.sidebar.expander("🚚 Déplacement", expanded=False):
    avg_distance   = st.number_input("Distance/trajet (km)", 30.0)
    st.info("Consommation fixe : 8 L/100 km\nPrix carburant : 1,80 €/L")
    fuel_price = 1.80

with st.sidebar.expander("🔧 Maintenance", expanded=False):
    maint_bras_m = st.number_input("Entretien mensuel Brasero (€)", 30.00)
    maint_chif_m = st.number_input("Entretien mensuel Chiffres (€)", 15.00)

# --- Fonction de calcul KPI ---
def compute_metrics(br_days, ch_days, tbs, tcs, fuel_p):
    # CA
    br_pack = [br_days * v for v in (b_pack1, b_pack2, b_pack3)]
    ch_pack = [ch_days * v for v in (c_pack1, c_pack2, c_pack3)]
    ca_b = sum(d * tb for d, tb in zip(br_pack, tbs))
    ca_c = sum(d * tc for d, tc in zip(ch_pack, tcs))
    ca = ca_b + ca_c
    # Amortissements
    amort = brasero_cost / brasero_life + chiffres_cost / chiffres_life
    # Prélèvements
    charges_p = ca * (social_rate + lib_rate + cpf_rate)
    res_net = ca - charges_p
    # Carburant
    trips = br_days * (b_pack2 + b_pack3) + ch_days * (c_pack2 + c_pack3)
    fuel_l = avg_distance * trips * (8/100)
    cost_fuel = fuel_l * fuel_p
    # Maintenance annuel
    maint = (maint_bras_m + maint_chif_m) * 12
    # Résultat après ops
    res_ops = res_net - (cost_fuel + maint)
    # Indicateurs
    roi_b = ca_b / brasero_cost * 100
    roi_c = ca_c / chiffres_cost * 100
    roi_t = ca / (brasero_cost + chiffres_cost) * 100
    marge_net = res_net / ca * 100 if ca else 0
    marge_ops = res_ops / ca * 100 if ca else 0
    pct_th = ca / threshold * 100 if threshold else 0
    return {
        "ca": ca, "res_net": res_net, "res_ops": res_ops,
        "roi_b": roi_b, "roi_c": roi_c, "roi_t": roi_t,
        "marge_net": marge_net, "marge_ops": marge_ops, "pct_th": pct_th
    }

# Calculs de base
base = compute_metrics(
    brasero_days, chiffres_days,
    [t_b1, t_b2, t_b3], [t_c1, t_c2, t_c3],
    fuel_price
)
ca_per_day = base["ca"] / (brasero_days + chiffres_days) if (brasero_days + chiffres_days) else 0
be_days = (brasero_cost + chiffres_cost) / ca_per_day if ca_per_day else np.nan

# Données pour l'affichage tabulaire d'origine
# Hypothèses modélisation
df_hypo = pd.DataFrame({
    "Hypothèse": [
        "Coût initial (€)", "Durée amort. (ans)", "Jours loués/an",
        "Taux occ. chiffres (%)", "Pack1 (%)", "Pack2 (%)", "Pack3 (%)"
    ],
    "Brasero": [
        brasero_cost, brasero_life, brasero_days,
        np.nan, b_pack1*100, b_pack2*100, b_pack3*100
    ],
    "Chiffres lumineux": [
        chiffres_cost, chiffres_life, round(chiffres_days, 1),
        chiffres_rate*100, c_pack1*100, c_pack2*100, c_pack3*100
    ]
})
# Résultats avant prélèvements
df_before = pd.DataFrame({
    "Segment": ["Brasero", "Chiffres lumineux", "Total"],
    "CA (€)": [round(sum([brasero_days*b_pack1*t_b1, brasero_days*b_pack2*t_b2, brasero_days*b_pack3*t_b3]), 2),
               round(sum([chiffres_days*c_pack1*t_c1, chiffres_days*c_pack2*t_c2, chiffres_days*c_pack3*t_c3]), 2),
               round(base["ca"], 2)],
    "Amort. annuel (€)": [round(brasero_cost/brasero_life, 2),
                          round(chiffres_cost/chiffres_life, 2),
                          round(brasero_cost/brasero_life + chiffres_cost/chiffres_life, 2)],
    "Bénéfice net avant charges (€)": [
        round(sum([brasero_days*b_pack1*t_b1, brasero_days*b_pack2*t_b2, brasero_days*b_pack3*t_b3]) - (brasero_cost/brasero_life), 2),
        round(sum([chiffres_days*c_pack1*t_c1, chiffres_days*c_pack2*t_c2, chiffres_days*c_pack3*t_c3]) - (chiffres_cost/chiffres_life), 2),
        round(base["ca"] - (brasero_cost/brasero_life + chiffres_cost/chiffres_life), 2)
    ]
})
# Charges & prélèvements
df_ch = pd.DataFrame({
    "Poste": ["Cotisations sociales", "Versement libératoire IR", "Formation pro", "Total prélèvements"],
    "Montant (€)": [
        round(base["ca"] * social_rate, 2),
        round(base["ca"] * lib_rate, 2),
        round(base["ca"] * cpf_rate, 2),
        round(base["ca"] * (social_rate + lib_rate + cpf_rate), 2)
    ]
})

# --- Onglets principaux ---
tabs = st.tabs(["Résumé","Scénarios","Trésorerie","Suivi réel","Matériel"])

# --- Tab Résumé ---
with tabs[0]:
    st.header("📋 Résumé complet")
    st.subheader("Hypothèses de la modélisation")
    st.dataframe(df_hypo, use_container_width=True)

    st.subheader("Résultats avant prélèvements")
    st.dataframe(df_before, use_container_width=True)

    st.subheader("💸 Charges & Prélèvements obligatoires")
    st.dataframe(df_ch, use_container_width=True)

    st.subheader("🏁 Résultats finaux & KPI")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("CA total (€)", f"{base['ca']:.2f}")
        st.metric("Bénéfice net avant ops (€)", f"{base['res_net']:.2f}")
        st.metric("Bénéfice net après ops (€)", f"{base['res_ops']:.2f}")
        st.metric("Marge nette (%)", f"{base['marge_net']:.2f}%")
    with col2:
        st.metric("CA/jour moyen (€)", f"{ca_per_day:.2f}")
        st.metric("Break-even (jours)", f"{be_days:.1f}")
        st.metric("ROI Brasero (%)", f"{base['roi_b']:.2f}%")
        st.metric("ROI Chiffres (%)", f"{base['roi_c']:.2f}%")
        st.metric("ROI Total (%)", f"{base['roi_t']:.2f}%")
        st.metric("CA vs Seuil (%)", f"{base['pct_th']:.2f}%")

    if base["ca"] > threshold:
        st.warning(f"⚠️ Votre CA estimé ({base['ca']:.2f} €) dépasse le seuil de {threshold:.0f} €.")

# --- Tab Scénarios ---
with tabs[1]:
    st.header("🔮 Analyse de scénarios")
    scenarios = {
        "Pessimiste": {"d":0.9,"r":0.9,"p":0.9,"f":1.1},
        "Médian":     {"d":1.0,"r":1.0,"p":1.0,"f":1.0},
        "Optimiste":  {"d":1.1,"r":1.1,"p":1.1,"f":0.9},
    }
    rows = []
    for name, f in scenarios.items():
        bd = brasero_days * f["d"]
        cd = min(365, chiffres_days * f["r"])
        tb = [t_b1*f["p"], t_b2*f["p"], t_b3*f["p"]]
        tc = [t_c1*f["p"], t_c2*f["p"], t_c3*f["p"]]
        m = compute_metrics(bd, cd, tb, tc, fuel_price * f["f"])
        rows.append({
            "Scénario": name,
            "CA (€)": round(m["ca"],2),
            "Net (€)": round(m["res_net"],2),
            "Ops (€)": round(m["res_ops"],2),
            "ROI (%)": round(m["roi_t"],2)
        })
    df_s = pd.DataFrame(rows)
    st.dataframe(df_s, use_container_width=True)
    df_m = df_s.melt(id_vars="Scénario", var_name="KPI", value_name="Valeur")
    chart = alt.Chart(df_m).mark_bar().encode(
        x="Scénario:N", y="Valeur:Q", color="KPI:N", column="KPI:N",
        tooltip=["Scénario","KPI","Valeur"]
    ).properties(height=200)
    st.altair_chart(chart, use_container_width=True)

# --- Tab Trésorerie ---
with tabs[2]:
    st.header("💰 Prévision de trésorerie (12 mois)")
    rev_m = base["ca"] / 12
    depr_m = (brasero_cost/brasero_life + chiffres_cost/chiffres_life) / 12
    maint_m = (maint_bras_m + maint_chif_m)
    q_ch = base["ca"]*(social_rate+lib_rate+cpf_rate)/4
    months = pd.date_range(pd.Timestamp.today().replace(day=1), periods=12, freq="MS")
    cash = []; cum = 0
    for mth in months:
        charge_q = q_ch if mth.month % 3 == 0 else 0
        exp = depr_m + maint_m + charge_q
        net = rev_m - exp
        cum += net
        cash.append({"Mois": mth.strftime("%b %Y"), "Net (€)": net, "Cumul (€)": cum})
    df_cash = pd.DataFrame(cash)
    st.subheader("Trésorerie cumulée")
    st.line_chart(df_cash.set_index("Mois")["Cumul (€)"])
    st.subheader("Détail mensuel")
    st.dataframe(df_cash.style.format({"Net (€)":"{:.2f}","Cumul (€)":"{:.2f}"}))

# --- Tab Suivi réel ---
with tabs[3]:
    st.header("📈 Suivi réel vs prévision")
    upl = st.file_uploader("Importez .xlsx (date, CA)", type="xlsx")
    if upl:
        df_act = pd.read_excel(upl, parse_dates=["date"])
        act = df_act.set_index("date").resample("M")["CA"].sum().rename("Réel")
        idx = pd.period_range(act.index.min(), act.index.max(), freq="M")
        pre = pd.Series(base["ca"]/12, index=idx).rename("Prévi")
        df_cmp = pd.concat([pre, act], axis=1).fillna(0).reset_index().melt(
            id_vars="index", value_vars=["Prévi","Réel"], var_name="Type", value_name="CA"
        ).rename(columns={"index":"Mois"})
        chart = alt.Chart(df_cmp).mark_line(point=True).encode(
            x="Mois:T", y="CA:Q", color="Type:N", tooltip=["Mois","Type","CA"]
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
        st.table(df_cmp.pivot(index="Mois", columns="Type", values="CA").style.format("{:.2f}"))

# --- Tab Matériel ---
with tabs[4]:
    st.header("🔧 Suivi Stock & Matériel")
    col1, col2 = st.columns(2)
    with col1:
        n_bras = st.number_input("Nb braseros", value=1, step=1)
        wear_b = st.slider("Usure braseros (%)", 0, 100, 20)
        life_b = st.number_input("Vie braseros (ans)", value=brasero_life)
        cost_b = st.number_input("Coût unitaire brasero (€)", value=brasero_cost/n_bras if n_bras else brasero_cost)
        next_b = st.date_input("Prochaine maintenance braseros")
    with col2:
        n_chi = st.number_input("Nb chiffres", value=2, step=1)
        wear_c = st.slider("Usure chiffres (%)", 0, 100, 10)
        life_c = st.number_input("Vie chiffres (ans)", value=chiffres_life)
        cost_c = st.number_input("Coût unitaire chiffre (€)", value=chiffres_cost/n_chi if n_chi else chiffres_cost)
        next_c = st.date_input("Prochaine maintenance chiffres")

    df_mat = pd.DataFrame([
        {
            "Équipement": "Brasero",
            "Nb": n_bras,
            "Usure (%)": wear_b,
            "Vie reste (ans)": round(life_b*(1-wear_b/100),2),
            "Proch. maint.": next_b
        },
        {
            "Équipement": "Chiffres",
            "Nb": n_chi,
            "Usure (%)": wear_c,
            "Vie reste (ans)": round(life_c*(1-wear_c/100),2),
            "Proch. maint.": next_c
        }
    ])
    st.table(df_mat)
    chart_mat = alt.Chart(df_mat).mark_bar().encode(
        x="Équipement:N", y="Usure (%):Q", tooltip=["Équipement","Usure (%)"]
    ).properties(height=250)
    st.altair_chart(chart_mat, use_container_width=True)
