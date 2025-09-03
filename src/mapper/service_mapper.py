import os
import traceback
import pandas as pd
from typing import List
from data_preprocessing import ServiceMatcher
from document_convertor import DocumentConverter
from prompt import prompt_template
from vector_store import VectorstoreBuilder
from rag_chain_factory import RAGChainFactory
from answer_parser import AnswerParser

class ServiceMapper:
    def __init__(
        self,
        vectorstore,
        prompt_template,
        answer_parser: AnswerParser,
        results_file: str = "mapping_results.csv",
        failures_file: str = "mapping_failures.csv"
    ):
        self.vectorstore = vectorstore
        self.prompt_template = prompt_template
        self.answer_parser = answer_parser
        self.results_file = results_file
        self.failures_file = failures_file

    def _load_done_codes(self) -> List[str]:
        """Load already processed service codes from results file."""
        if os.path.exists(self.results_file):
            done_codes = pd.read_csv(self.results_file)["Internal_Service_Code"].unique().tolist()
            print(f"🔄 Found {len(done_codes)} completed rows. Skipping them.")
            return done_codes
        else:
            return []

    def _init_output_files(self, results_cols: List[str], failures_cols: List[str]) -> None:
        """Ensure result and failure files exist with headers."""
        if not os.path.exists(self.results_file):
            pd.DataFrame(columns=results_cols).to_csv(self.results_file, index=False)
        if not os.path.exists(self.failures_file):
            pd.DataFrame(columns=failures_cols).to_csv(self.failures_file, index=False)

    def _append_to_csv(self, file_path: str, row_data: dict) -> None:
        """Append a single row to a CSV file."""
        pd.DataFrame([row_data]).to_csv(file_path, mode='a', header=False, index=False)

    def map_service_codes(self, ahj_services_df: pd.DataFrame) -> None:
        """Map AHJ service codes to SBS codes using RAG."""
        rag_chain = RAGChainFactory(self.vectorstore, self.prompt_template).create_rag_chain()

        results_cols = [
            "Internal_Service_Code",
            "Internal_Description",
            "Matched_SBS_Code",
            "Matched_SBS_Short_Description",
            "LLM_Explanation"
        ]
        failures_cols = ahj_services_df.columns.tolist() + ["Error", "Traceback"]

        done_codes = self._load_done_codes()
        self._init_output_files(results_cols, failures_cols)

        to_process = ahj_services_df[~ahj_services_df["SERVICE_CODE"].isin(done_codes)]
        print(f"🚀 Processing {len(to_process)} rows...")

        for idx, (_, row) in enumerate(to_process.iterrows(), start=1):
            query = (
                f"Service Code: {row['SERVICE_CODE']}\n"
                f"Description: {row['SERVICE_DESCRIPTION']}\n"
                f"Classification: {row['SERVICE_CLASSIFICATION']}\n"
                f"Category: {row['SERVICE_CATEGORY']}"
            )
            try:
                response = rag_chain({"query": query})
                answer = response['result']
                best_code, best_desc, explanation = self.answer_parser.parse_llm_answer(answer)

                self._append_to_csv(self.results_file, {
                    "Internal_Service_Code": row['SERVICE_CODE'],
                    "Internal_Description": row['SERVICE_DESCRIPTION'],
                    "Matched_SBS_Code": best_code,
                    "Matched_SBS_Short_Description": best_desc,
                    "LLM_Explanation": explanation
                })

                print(f"✅ Row {idx}/{len(to_process)} — {row['SERVICE_CODE']} mapped.")

            except Exception as e:
                tb = traceback.format_exc()
                print(f"❌ Error at row {idx}/{len(to_process)}: {e}")

                failed_row = row.to_dict()
                failed_row["Error"] = str(e)
                failed_row["Traceback"] = tb

                self._append_to_csv(self.failures_file, failed_row)

        print(f"🎉 Done! Results in {self.results_file}, failures in {self.failures_file}")

# === STEP 1: Load and prepare AHJ & SBS data ===
matcher = ServiceMatcher(
    ahj_path=r"D:\CodingSystem\assets\AHJ_PriceList.xlsx",
    sbs_path=r"D:\CodingSystem\assets\SBS_Services.xlsx"
)

ahj_df, sbs_df = matcher.load_data()
ahj_df = matcher.preprocess_ahj()
exact_matches = matcher.match_services()
unique_ahj_services = matcher.find_unique_ahj_services(exact_matches)

print(f"Matched services: {exact_matches.shape}")
print(f"Unique AHJ services: {unique_ahj_services.shape}")

# === STEP 2: Convert SBS services to documents ===
# You can combine Short & Long descriptions if needed for better retrieval
sbs_docs = DocumentConverter().convert_sbs_to_docs(sbs_df)

# === STEP 3: Build Vectorstore ===
vectorstore_builder = VectorstoreBuilder("BAAI/bge-small-en-v1.5")
vectorstore = vectorstore_builder.create_faiss_index(sbs_docs)

# === STEP 4: Initialize ServiceMapper ===
mapper = ServiceMapper(
    vectorstore=vectorstore,
    prompt_template=prompt_template,
    answer_parser=AnswerParser(),  # ✅ Instantiate here
    results_file="mapping_results.csv",
    failures_file="mapping_failures.csv"
)

# === STEP 5: Map services ===
mapper.map_service_codes(unique_ahj_services)

print("✅ Service mapping process completed.")