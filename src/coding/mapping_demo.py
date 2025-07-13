import streamlit as st
import pandas as pd
import os

# ---- File paths ---- #
DATA_ORIGINAL = "D:/CodingSystem/notebooks/full_mappings.xlsx"
DATA_UPDATED = "D:/CodingSystem/notebooks/updated_mappings.xlsx"

# ---- Load your data ---- #
@st.cache_data
def load_data():
    if os.path.exists(DATA_UPDATED):
        df = pd.read_excel(DATA_UPDATED)
    else:
        df = pd.read_excel(DATA_ORIGINAL)
    return df

df = load_data()

st.title("AHJ Service Mapper")

# ---- Sidebar filters ---- #
st.sidebar.header("🔎 Filter Options")

# Insurance Company filter
insurance_companies = df['INSURANCE_COMPANY'].unique()
selected_company = st.sidebar.selectbox("🏢 Select Insurance Company", insurance_companies)

# Filter by company
company_df = df[df['INSURANCE_COMPANY'] == selected_company]

# Filter mode
filter_mode = st.sidebar.radio(
    "🎛️ Filter Mode",
    ["Filter by Description", "Filter by Service Code", "Filter by Both"]
)

selected_description, selected_code = None, None

if filter_mode in ["Filter by Description", "Filter by Both"]:
    service_descriptions = company_df['SERVICE_DESCRIPTION'].unique()
    selected_description = st.sidebar.selectbox("📝 Select Service Description", service_descriptions)

if filter_mode in ["Filter by Service Code", "Filter by Both"]:
    service_codes = company_df['SERVICE_CODE'].unique()
    selected_code = st.sidebar.selectbox("💡 Select Service Code", service_codes)

# Apply filters
result_df = company_df
if selected_description:
    result_df = result_df[result_df['SERVICE_DESCRIPTION'] == selected_description]
if selected_code:
    result_df = result_df[result_df['SERVICE_CODE'] == selected_code]

st.subheader("📑 Service Details")

if not result_df.empty:
    record = result_df.iloc[0]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**🏢 Insurance Company:** `{record['INSURANCE_COMPANY']}`")
        st.markdown(f"**💡 AHJ Code:** `{record['SERVICE_CODE']}`")
        st.markdown(f"**📝 AHJ Description:** `{record['SERVICE_DESCRIPTION']}`")
        st.markdown(f"**💰 Service Price:** `{record['PRICE']}`")
        st.markdown(f"**📂 Classification:** `{record['SERVICE_CLASSIFICATION']}`")
        st.markdown(f"**📁 Category:** `{record['SERVICE_CATEGORY']}`")

    with col2:
        st.markdown(f"**🗂️ SBS Code:** `{record['SBS Code']}`")
        st.markdown(f"**📎 SBS Code (Hyphenated):** `{record['SBS Code (Hyphenated)']}`")
        st.markdown(f"**🔖 Short Description:** `{record['SHORT_DESCRIPTION']}`")
        st.markdown(f"**📝 Long Description:** `{record['Long Description']}`")
        st.markdown(f"**📘 Chapter Name:** `{record['Chapter Name']}`")
        st.markdown(f"**📗 Block Name:** `{record['Block Name']}`")

    with st.expander("📚 Additional Details"):
        st.write(record['Definition'])

    # Download button
    csv = result_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download This Record as CSV",
        data=csv,
        file_name='service_details.csv',
        mime='text/csv',
    )

    # ---- Feedback ---- #
    st.markdown("---")
    st.subheader("📌 Current Validation Status")
    current_status = record.get('Validation (Correct / In Correct)', 'Not set')
    st.info(f"**Current Status:** `{current_status}`")

    st.markdown("---")
    st.subheader("📝 Feedback")

    default_idx = 0 if str(current_status).strip().lower() == "correct" else 1
    validation_option = st.radio(
        "Is this mapping correct?",
        ["Correct", "In Correct"],
        index=default_idx,
        key="validation_option_radio"
    )

    with st.form("feedback_form"):
        if validation_option == "In Correct":
            correct_code = st.text_input(
                "💡 Enter the Correct SBS Code",
                value="" if pd.isna(record['Correct SBS Code']) else record['Correct SBS Code'],
                key="correct_code_input_box"
            )
            correct_desc = st.text_area(
                "📝 Enter the Correct SBS Short / Long Description",
                value="" if pd.isna(record['Correct SBS Short / Long Description']) else record['Correct SBS Short / Long Description'],
                key="correct_desc_input_box"
            )
        else:
            # KEEP previous if user selects "Correct"
            correct_code = record['Correct SBS Code']
            correct_desc = record['Correct SBS Short / Long Description']

        submitted = st.form_submit_button("💾 Save Feedback")

        if submitted:
            idx = df[
                (df['INSURANCE_COMPANY'] == selected_company) &
                (df['SERVICE_CODE'] == record['SERVICE_CODE'])
            ].index

            df.loc[idx, 'Validation (Correct / In Correct)'] = validation_option
            df.loc[idx, 'Correct SBS Code'] = correct_code
            df.loc[idx, 'Correct SBS Short / Long Description'] = correct_desc

            df.to_excel(DATA_UPDATED, index=False)

            st.success(f"✅ Feedback saved! File updated: `{os.path.basename(DATA_UPDATED)}`")

else:
    st.warning("⚠️ No matching record found. Try a different combination!")