class AnswerParser:
    def parse_llm_answer(self, answer: str):
        best_code = ""
        best_desc = ""
        explanation = ""

        for line in answer.split('\n'):
            if line.startswith("Best SBS Code:"):
                best_code = line.replace("Best SBS Code:", "").strip()
            elif line.startswith("Best SBS Description:"):
                best_desc = line.replace("Best SBS Description:", "").strip()
            elif line.startswith("Explanation:"):
                explanation = line.replace("Explanation:", "").strip()

        return best_code, best_desc, explanation