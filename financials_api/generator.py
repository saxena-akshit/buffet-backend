import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration

class T5Generator:
    def __init__(self, model_name='t5-small', max_length=256):
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.max_length = max_length
        print(f"T5 Generator initialized with model: {model_name}") # Keep init message

    def generate(self, prompt: str) -> str:
        input_ids = self.tokenizer.encode(
            prompt,
            return_tensors='pt',
            max_length=512, # Context length limit
            truncation=True
        )

        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_length=self.max_length,
                num_beams=4,
                early_stopping=True,
                length_penalty=1.1
            )

        answer = self.tokenizer.decode(
            output_ids[0],
            skip_special_tokens=True
        )
        return answer