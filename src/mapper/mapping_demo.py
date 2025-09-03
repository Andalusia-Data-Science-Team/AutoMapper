import streamlit as st 
import pandas as pd
import os

# ---- File paths ---- #
DATA_ORIGINAL = "D:/CodingSystem/notebooks/full_mappings.xlsx"
DATA_VALIDATED = "D:/CodingSystem/assets/validated_mappings.csv"

# ---- Expected columns for the validation sheet ---- #
VALIDATION_COLUMNS = [
    "INSURANCE_COMPANY",
    "SERVICE_CODE",
    "SERVICE_DESCRIPTION",
    "PRICE",
    "SERVICE_KEY",
    "SERVICE_CLASSIFICATION",
    "SERVICE_CATEGORY",
    "SBS Code",
    "SBS Code (Hyphenated)",
    "SHORT_DESCRIPTION",
    "Long Description",
    "Definition",
    "Chapter Name",
    "Block Name",
    "Validation (Correct / In Correct)",
    "Correct SBS Code",
    "Correct SBS Short / Long Description",
    "Validated By"
]

# ---- Cache only the original Excel data ---- #
@st.cache_data
def load_original_data():
    return pd.read_excel(DATA_ORIGINAL)

def merge_validated_data(df_original):
    if os.path.exists(DATA_VALIDATED):
        df_validated = pd.read_csv(DATA_VALIDATED)

        merge_cols = [
            'INSURANCE_COMPANY', 'SERVICE_CODE',
            'Validation (Correct / In Correct)',
            'Correct SBS Code',
            'Correct SBS Short / Long Description',
            'Validated By'
        ]

        df_validated = df_validated[[col for col in merge_cols if col in df_validated.columns]]

        merged_df = df_original.merge(
            df_validated,
            on=['INSURANCE_COMPANY', 'SERVICE_CODE'],
            how='left',
            suffixes=('', '_validated')
        )

        for col in ['Validation (Correct / In Correct)', 'Correct SBS Code',
                    'Correct SBS Short / Long Description', 'Validated By']:
            validated_col = f"{col}_validated"
            if validated_col in merged_df.columns:
                merged_df[col] = merged_df[validated_col].where(pd.notna(merged_df[validated_col]), merged_df.get(col))
                merged_df.drop(columns=[validated_col], inplace=True)

        return merged_df
    else:
        return df_original


# ---- Load data ---- #
df_original = load_original_data()
df = merge_validated_data(df_original)

st.title("AHJ Service Mapper 🚀")

# ---- Sidebar filters ---- #
st.sidebar.header("🔎 Filter Options")

insurance_companies = df['INSURANCE_COMPANY'].unique()

# -- Session state for filters -- #
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = insurance_companies[0]

selected_company = st.sidebar.selectbox(
    "🏢 Select Insurance Company",
    insurance_companies,
    index=list(insurance_companies).index(st.session_state.selected_company)
)
st.session_state.selected_company = selected_company

company_df = df[df['INSURANCE_COMPANY'] == selected_company]

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
        st.markdown(f"**🔑 Service Key:** `{record['SERVICE_KEY']}`")
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

    # ---- Feedback ---- #
    st.markdown("---")
    st.subheader("📌 Current Validation Status")

    current_status = record.get('Validation (Correct / In Correct)', 'Not set')
    if pd.isna(current_status):
        current_status = "Not set"

    validated_by = record.get('Validated By', 'Not available')
    if pd.isna(validated_by):
        validated_by = "Not Set"

    st.info(f"**Current Status:** `{current_status}`")
    st.info(f"**Validated By:** `{validated_by}`")

    st.markdown("---")
    st.subheader("📝 Feedback")

    # ✅ Show success message if feedback was saved
    if st.session_state.get("feedback_saved"):
        st.success("✅ Feedback saved successfully!")
        st.session_state.feedback_saved = False  # Reset for next display

    default_idx = 0 if str(current_status).strip().lower() == "correct" else 1
    validation_option = st.radio(
        "Is this mapping correct?",
        ["Correct", "In Correct"],
        index=default_idx,
        key="validation_option_radio"
    )

    with st.form("feedback_form"):
        user_name = st.text_input("👤 Please Enter Your Name", key="user_name_input")

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
            correct_code = record['Correct SBS Code']
            correct_desc = record['Correct SBS Short / Long Description']

        submitted = st.form_submit_button("💾 Save Feedback")

        if submitted:
            updated_row = {
                'INSURANCE_COMPANY': record['INSURANCE_COMPANY'],
                'SERVICE_CODE': record['SERVICE_CODE'],
                'Validation (Correct / In Correct)': validation_option,
                'Correct SBS Code': correct_code,
                'Correct SBS Short / Long Description': correct_desc,
                'Validated By': user_name
            }

            def save_feedback_csv(updated_row, full_record):
                if os.path.exists(DATA_VALIDATED):
                    validated_df = pd.read_csv(DATA_VALIDATED)
                else:
                    validated_df = pd.DataFrame(columns=VALIDATION_COLUMNS)

                idx = validated_df[
                    (validated_df['INSURANCE_COMPANY'] == updated_row['INSURANCE_COMPANY']) &
                    (validated_df['SERVICE_CODE'] == updated_row['SERVICE_CODE'])
                ].index

                new_row = {}
                for col in VALIDATION_COLUMNS:
                    if col in updated_row:
                        new_row[col] = updated_row[col]
                    elif col in full_record:
                        new_row[col] = full_record[col]
                    else:
                        new_row[col] = ""

                if not idx.empty:
                    for col in VALIDATION_COLUMNS:
                        validated_df.loc[idx, col] = new_row[col]
                else:
                    validated_df = pd.concat([validated_df, pd.DataFrame([new_row])], ignore_index=True)

                validated_df.to_csv(DATA_VALIDATED, index=False)

            save_feedback_csv(updated_row, record)

            # ✅ Flag for next render to show message
            st.session_state.feedback_saved = True
            st.cache_data.clear()
            st.rerun()

else:
    st.warning("⚠️ No matching record found. Try a different combination!")