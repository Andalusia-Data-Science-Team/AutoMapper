import pandas as pd

class ServiceMatcher:
    def __init__(self, ahj_path, sbs_path):
        self.ahj_path = ahj_path
        self.sbs_path = sbs_path
        self.ahj = None
        self.sbs = None

    def load_data(self):
        """Load Excel files and apply basic cleaning."""
        self.ahj = pd.read_excel(self.ahj_path)
        self.ahj = self.ahj[~self.ahj['INSURANCE_COMPANY']
                            .isin([0, 'Cash', 'Item Cash', 'OUTSIDE DOCTOR (CASH)'])]

        self.sbs = pd.read_excel(self.sbs_path)
        self.sbs['Short Description'] = self.sbs['Short Description'].str.strip().str.upper()
        self.sbs['Long Description'] = self.sbs['Long Description'].str.strip().str.upper()

        return self.ahj, self.sbs

    def preprocess_ahj(self):
        """Remove PK- prefix from service description."""
        if self.ahj is None:
            raise ValueError("Load AHJ data first using load_data().")

        self.ahj['NEW_SERVICE_DESCRIPTION'] = self.ahj['SERVICE_DESCRIPTION']\
            .str.replace(r'^(PK-)+', '', regex=True)

        return self.ahj

    def match_services(self):
        """Match AHJ services with SBS services using short and long descriptions."""
        if self.ahj is None or self.sbs is None:
            raise ValueError("Load data first using load_data().")

        merge_long = self.ahj.merge(
            self.sbs,
            how='left',
            left_on='NEW_SERVICE_DESCRIPTION',
            right_on='Long Description'
        )

        merge_short = self.ahj.merge(
            self.sbs,
            how='left',
            left_on='NEW_SERVICE_DESCRIPTION',
            right_on='Short Description'
        )

        # Combine matches
        exact_services = pd.concat([merge_long, merge_short])
        exact_services = exact_services[
            exact_services['Long Description'].notnull() |
            exact_services['Short Description'].notnull()
        ]
        exact_services.drop_duplicates(inplace=True)

        return exact_services

    def find_unique_ahj_services(self, exact_services):
        """Find AHJ services not matched in SBS."""
        if self.ahj is None:
            raise ValueError("Load AHJ data first using load_data().")

        different_ahj = self.ahj[
            ~self.ahj['SERVICE_DESCRIPTION']
            .isin(exact_services['SERVICE_DESCRIPTION'].unique())
        ]

        unique_ahj_services = different_ahj[
            ['SERVICE_CODE', 'SERVICE_DESCRIPTION', 'SERVICE_CLASSIFICATION', 'SERVICE_CATEGORY']
        ].drop_duplicates().reset_index(drop=True)

        return unique_ahj_services


# Example usage:
# if __name__ == "__main__":
#     matcher = ServiceMatcher(
#         ahj_path="D:\\CodingSystem\\assets\\AHJ_PriceList.xlsx",
#         sbs_path="D:\\CodingSystem\\assets\\SBS_Services.xlsx"
#     )

#     ahj, sbs = matcher.load_data()
#     ahj = matcher.preprocess_ahj()
#     exact = matcher.match_services()
#     unique = matcher.find_unique_ahj_services(exact)

#     print("Matched services:", exact.shape)
#     print("Unique AHJ services:", unique.shape)
#     print(unique.columns)