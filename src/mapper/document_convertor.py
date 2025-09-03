from langchain.schema import Document
import pandas as pd

class DocumentConverter:
    def convert_sbs_to_docs(self, sbs_df: pd.DataFrame):
        docs = []
        for _, row in sbs_df.iterrows():
            service_text = (
                f"**Service Short Description:** {row.get('Short Description', 'Not Mentioned')}\n"
                f"Service Long Description: {row.get('Long Description', 'Not Mentioned')}\n"
                f"Definition: {row.get('Definition', 'Not Mentioned')}\n"
                f"Service Category: {row.get('Block Name', 'Not Mentioned')}\n"
                f"Service Classification: {row.get('Chapter Name', 'Not Mentioned')}\n"
                f"Service Code: {row.get('SBS Code (Hyphenated)', 'Not Mentioned')}"
            )
            docs.append(Document(
                page_content=service_text.strip(),
                metadata={
                    "Service Code": row['SBS Code (Hyphenated)'],
                    "Short Description": row['Short Description']
                }
            ))
        return docs


