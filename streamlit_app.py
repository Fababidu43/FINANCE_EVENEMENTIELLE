import streamlit as st
import pandas as pd

st.title("Dashboard de Prévision Financière")

# Sidebar : Hypothèses générales
st.sidebar.header("Hypothèses Générales")
brasero_cost = st.sidebar.number_input(
    "Coût initial Brasero (€)",
    value=1500,
    help="Coût total pour acheter ou fabriquer le brasero avec ses accessoires."
)
brasero_life = st.sidebar.number_input(
    "Durée d'amortissement Brasero (ans)",
    value=5,
    help="Durée estimée d'utilisation rentable du brasero en années."
)
brasero_days = st.sidebar.number_input(
    "Jours loués par an (Brasero)",
    value=100,
    help="Nombre estimé de jours de location par an, généralement en période estivale."
)

chiffres_cost = st.sidebar.number_input(
    "Coût initial Chiffres lumineux (€)",
    value=1075,
    help="Coût total pour fabriquer ou acheter les chiffres lumineux et leurs accessoires."
)
chiffres_life = st.sidebar.number_input(
    "Durée d'amortissement Chiffres (ans)",
    value=5,
    help="Durée estimée d'utilisation rentable des chiffres lumineux en années."
)
chiffres_rate = st.sidebar.slider(
    "Taux d'occupation Chiffres (%)",
    0, 100, 50,
    help="Pourcentage estimé des jours où les chiffres lumineux seront loués sur une année complète."
) / 100
chiffres_days = chiffres_rate * 365

# Sidebar : Répartition des Packs
st.sidebar.header("Répartition des Packs (Brasero)")
b_pack1 = st.sidebar.number_input(
    "Pack1 (%)",
    value=40,
    help="Pourcentage estimé de location en Pack 1 (location simple au dépôt)."
) / 100
b_pack2 = st.sidebar.number_input(
    "Pack2 (%)",
    value=40,
    help="Pourcentage estimé de location en Pack 2 (livraison, montage et démontage)."
) / 100
b_pack3 = st.sidebar.number_input(
    "Pack3 (%)",
    value=20,
    help="Pourcentage estimé de location en Pack 3 (livraison avec bois et cuisinier)."
) / 100

st.sidebar.header("Répartition des Packs (Chiffres lumineux)")
c_pack1 = st.sidebar.number_input(
    "Pack1 (%)",
    value=60,
    help="Pourcentage estimé de location en Pack 1 (1 chiffre lumineux)."
) / 100
c_pack2 = st.sidebar.number_input(
    "Pack2 (%)",
    value=30,
    help="Pourcentage estimé de location en Pack 2 (2 chiffres lumineux, livré, monté et démonté)."
) / 100
c_pack3 = st.sidebar.number_input(
    "Pack3 (%)",
    value=10,
    help="Pourcentage estimé de location en Pack 3 (Pack événementiel complet)."
) / 100

# Sidebar : Tarifs journaliers
st.sidebar.header("Tarifs journaliers (Brasero)")
t_b1 = st.sidebar.number_input(
    "Brasero Pack1 (€/jour)",
    value=150,
    help="Prix de location par jour pour le Pack 1 (location simple)."
)
t_b2 = st.sidebar.number_input(
    "Brasero Pack2 (€/jour)",
    value=300,
    help="Prix de location par jour pour le Pack 2 (livré, monté et démonté)."
)
t_b3 = st.sidebar.number_input(
    "Brasero Pack3 (€/jour)",
    value=400,
    help="Prix de location par jour pour le Pack 3 (livré avec bois et cuisinier)."
)

st.sidebar.header("Tarifs journaliers (Chiffres lumineux)")
t_c1 = st.sidebar.number_input(
    "Chiffres Pack1 (€/jour)",
    value=50,
    help="Prix de location par jour pour 1 chiffre lumineux seul."
)
t_c2 = st.sidebar.number_input(
    "Chiffres Pack2 (€/jour)",
    value=100,
    help="Prix de location par jour pour 2 chiffres lumineux livrés et montés."
)
t_c3 = st.sidebar.number_input(
    "Chiffres Pack3 (€/jour)",
    value=140,
    help="Prix de location par jour pour 2 chiffres lumineux avec décor complet."
)

# Sidebar : Charges & prélèvements obligatoires
st.sidebar.header("Charges & Prélèvements")
social_rate = st.sidebar.number_input(
    "Taux cotisations sociales (%)",
    value=21.2,
    help="Taux URSSAF appliqué au CA (activités de services & location)."
) / 100
lib_rate = st.sidebar.number_input(
    "Taux versement libératoire IR (%)",
    value=1.7,
    help="Taux du prélèvement libératoire sur le CA si option choisie."
) / 100
cpf_rate = st.sidebar.number_input(
    "Taux formation professionnelle (%)",
    value=0.3,
    help="Contribution à la formation professionnelle sur le CA."
) / 100
threshold = st.sidebar.number_input(
    "Seuil CA auto-entreprise (€)",
    value=77700,
    help="Seuil légal de CA annuel pour le régime micro-entreprise (services)."
)

# --- Calculs ---
# CA par segment
brasero_dist = {'Pack1': b_pack1, 'Pack2': b_pack2, 'Pack3': b_pack3}
chiffres_dist = {'Pack1': c_pack1, 'Pack2': c_pack2, 'Pack3': c_pack3}
brasero_days_pack = {k: brasero_days * v for k, v in brasero_dist.items()}
chiffres_days_pack = {k: chiffres_days * v for k, v in chiffres_dist.items()}

ca_brasero = (
    brasero_days_pack['Pack1'] * t_b1
    + brasero_days_pack['Pack2'] * t_b2
    + brasero_days_pack['Pack3'] * t_b3
)
ca_chiffres = (
    chiffres_days_pack['Pack1'] * t_c1
    + chiffres_days_pack['Pack2'] * t_c2
    + chiffres_days_pack['Pack3'] * t_c3
)
total_ca = ca_brasero + ca_chiffres

# Amortissements et resultats avant charges
amort_brasero = brasero_cost / brasero_life
amort_chiffres = chiffres_cost / chiffres_life
result_brasero_before = ca_brasero - amort_brasero
result_chiffres_before = ca_chiffres - amort_chiffres
result_before_total = result_brasero_before + result_chiffres_before

# Charges sociales, formation, impôt libératoire
cotisations = total_ca * social_rate
versement_lib = total_ca * lib_rate
formation = total_ca * cpf_rate
total_charges = cotisations + formation + versement_lib
result_after_all = total_ca - total_charges

# Indicateurs complémentaires
roi_brasero = ca_brasero / brasero_cost * 100 if brasero_cost else 0
roi_chiffres = ca_chiffres / chiffres_cost * 100 if chiffres_cost else 0
roi_total = total_ca / (brasero_cost + chiffres_cost) * 100
threshold_pct = total_ca / threshold * 100 if threshold else 0
charges_pct = total_charges / total_ca * 100 if total_ca else 0
marge_nette_pct = result_after_all / total_ca * 100 if total_ca else 0

# --- Affichage des tables ---
# Hypothèses
st.subheader("Hypothèses de la modélisation")
df_hypotheses = pd.DataFrame({
    'Hypothèse': [
        'Coût initial (€)', "Durée amortissement (ans)", 'Jours loués/an',
        'Taux occ. Chiffres (%)', 'Répartition Pack1 (%)', 'Répartition Pack2 (%)', 'Répartition Pack3 (%)'
    ],
    'Brasero': [
        brasero_cost, brasero_life, brasero_days, '-', b_pack1*100, b_pack2*100, b_pack3*100
    ],
    'Chiffres lumineux': [
        chiffres_cost, chiffres_life, round(chiffres_days,1), chiffres_rate*100,
        c_pack1*100, c_pack2*100, c_pack3*100
    ]
})
st.dataframe(df_hypotheses)

# Résultats avant charges
st.subheader("Résultats avant charges")
df_before = pd.DataFrame({
    'Segment': ['Brasero', 'Chiffres lumineux', 'Total'],
    'CA (€)': [round(ca_brasero,2), round(ca_chiffres,2), round(total_ca,2)],
    'Amortissement annuel (€)': [round(amort_brasero,2), round(amort_chiffres,2), round(amort_brasero+amort_chiffres,2)],
    'Bénéfice net avant charges (€)': [
        round(result_brasero_before,2),
        round(result_chiffres_before,2),
        round(result_before_total,2)
    ]
})
st.dataframe(df_before)

# Charges & prélèvements
st.subheader("Charges & Prélèvements")
df_charges = pd.DataFrame({
    'Poste': [
        'Cotisations sociales', 'Versement libératoire IR',
        'Formation professionnelle', 'Total prélèvements'
    ],
    'Montant (€)': [
        round(cotisations,2), round(versement_lib,2),
        round(formation,2), round(total_charges,2)
    ]
})
st.dataframe(df_charges)

# Résultat après prélèvements
st.subheader("Résultat après prélèvements")
st.metric("Bénéfice net final (€)", f"{round(result_after_all,2)}")
st.metric("Marge nette (%)", f"{round(marge_nette_pct,2)}%")

# Indicateurs clés
st.subheader("Indicateurs clés")
df_indicators = pd.DataFrame({
    'Indicateur': [
        'ROI Brasero (%)', 'ROI Chiffres lumineux (%)', 'ROI Total (%)',
        'CA vs seuil auto-entreprise (%)', 'Taux total de prélèvement (%)'
    ],
    'Valeur (%)': [
        round(roi_brasero,2), round(roi_chiffres,2), round(roi_total,2),
        round(threshold_pct,2), round(charges_pct,2)
    ]
})
st.dataframe(df_indicators)

# Alerte si dépassement de seuil
if total_ca > threshold:
    st.warning(f"⚠️ Votre CA estimé de {total_ca:.2f} € dépasse le seuil de {threshold:.0f} €.")
