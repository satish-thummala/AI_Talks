import torch
from transformers import AutoTokenizer, AutoModel

model_name = "bert-base-uncased"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(
    model_name,
    output_attentions=True
)

text = "The cat sat on the mat because it was tired."

inputs = tokenizer(
    text,
    return_tensors="pt"
)

tokens = tokenizer.convert_ids_to_tokens(
    inputs["input_ids"][0]
)

print(tokens)

with torch.no_grad():
    outputs = model(**inputs)

attention = outputs.attentions