from transformers import AutoTokenizer, AutoModelForImageTextToText, BitsAndBytesConfig
import torch

class LLMManager:

    LLM_IN_USE = "Qwen/Qwen3.5-4B-Base"
    context = "context.txt"

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(self.LLM_IN_USE)
        config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
        self.model = AutoModelForImageTextToText.from_pretrained(
            self.LLM_IN_USE,
            quantization_config=config,
            device_map="auto"
        )
        with open (self.context, "r") as f:
            self.template = f.read().replace("\n", "", 3)

    def prepare_input(self, email_text, sender):
        ai_input = self.template
        ai_input = ai_input.replace("<sender>", sender)
        ai_input = ai_input.replace("<email>", email_text)
        ai_input = ai_input.replace("<eos>", self.tokenizer.decode(self.tokenizer.eos_token_id))
        return ai_input

    def forward(self, email_text, sender, ai_text): 

        # Prepare AI input
        with torch.no_grad():
            ai_input = self.prepare_input(email_text, sender)
            ai_input = ai_input + ai_text
            ai_input = self.tokenizer(ai_input, return_tensors="pt").to(self.device)
            
            # Get singular text token from AI model
            output = self.model(ai_input["input_ids"], attention_mask=None)
            output = output.logits[:, -1, :]
            output = torch.argmax(output, dim=-1).type(torch.int64)
            generated_text = self.tokenizer.decode(output.item())

            # Clear Tensors from GPU memory
            del ai_input
            del output
            torch.cuda.empty_cache()

            # Return single token text output (duh)
            return generated_text
    
    def stop_generating(self, token_text, ai_text):

        if token_text == self.tokenizer.decode(self.tokenizer.eos_token_id):
            return True
        elif "Sincerely, Dylan Beskar" in ai_text:
            return True
        else:
            return False
