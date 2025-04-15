# rag_pipeline/generator.py

import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration

class T5Generator:
    def __init__(self, model_name='t5-small', max_length=128):
        """
        model_name: e.g. 't5-small', 'flan-t5-small', etc.
        """
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.max_length = max_length

    def generate(self, prompt: str) -> str:
        """
        Takes a prompt string and returns a generated answer.
        """
        input_ids = self.tokenizer.encode(
            prompt,
            return_tensors='pt'
        )

        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_length=self.max_length,
                num_beams=2,
                early_stopping=True
            )

        answer = self.tokenizer.decode(
            output_ids[0],
            skip_special_tokens=True
        )
        return answer
