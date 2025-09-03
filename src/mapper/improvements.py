import pandas as pd

class ServiceMappingsProcessor:
    def __init__(self, mappings_path: str, feedback_path: str):
        self.mappings_path = mappings_path
        self.feedback_path = feedback_path

    def load_data(self):
        """Load mappings and feedback Excel files."""
        self.mappings = pd.read_excel(self.mappings_path)
        self.feedback = pd.read_excel(self.feedback_path)

    def process_feedback(self):
        """Extract and clean correct mappings from feedback."""
        correct = self.feedback[self.feedback['Comment'] == 'Correct'].copy()
        correct['SBS Code'] = correct['SBS Code'].astype(int)

        self.correct_mappings = correct[
            ['SERVICE_CODE', 'SERVICE_DESCRIPTION', 'SERVICE_KEY', 'SERVICE_CLASSIFICATION',
             'SERVICE_CATEGORY', 'SBS Code', 'SBS Code (Hyphenated)', 'SHORT_DESCRIPTION',
             'Long Description', 'Definition', 'Chapter Name', 'Block Name']
        ].drop_duplicates()

        self.correct_services = list(self.correct_mappings['SERVICE_CODE'].unique())

    def process_mappings(self):
        """Split mappings into unrevised and revised, then merge with feedback."""
        self.unrevised_mappings = self.mappings[~self.mappings['SERVICE_CODE'].isin(self.correct_services)]

        self.revised_codes = self.mappings[
            self.mappings['SERVICE_CODE'].isin(self.correct_services)
        ][['INSURANCE_COMPANY', 'SERVICE_CODE', 'PRICE']]

        self.match_services = self.revised_codes.merge(
            self.correct_mappings, how='left', on='SERVICE_CODE'
        )[
            ['INSURANCE_COMPANY', 'SERVICE_CODE', 'SERVICE_DESCRIPTION', 'PRICE',
             'SERVICE_KEY', 'SERVICE_CLASSIFICATION', 'SERVICE_CATEGORY', 'SBS Code',
             'SBS Code (Hyphenated)', 'SHORT_DESCRIPTION', 'Long Description',
             'Definition', 'Chapter Name', 'Block Name']
        ]

        self.mappings_after_edits = pd.concat([self.unrevised_mappings, self.revised_codes], axis=0)

    def run(self):
        """Run the full pipeline (no return, just prepare data)."""
        self.load_data()
        self.process_feedback()
        self.process_mappings()

    def save_to_excel(self, output_path: str):
        """Save the final dataframe to an Excel file."""
        if self.mappings_after_edits is None:
            raise ValueError("You must run the pipeline before saving.")
        self.mappings_after_edits.to_excel(output_path, index=False)
    

processor = ServiceMappingsProcessor(
    mappings_path="D:\\CodingSystem\\assets\\ahj_sbs_mappings.xlsx",
    feedback_path="D:\\CodingSystem\\assets\\feedback\\AI-Revision (TCS-ART-MEDVISA-PUPA).xlsx"
)

processor.run()
processor.save_to_excel("D:\\CodingSystem\\assets\\feedback\\mappings_after_edits.xlsx")

