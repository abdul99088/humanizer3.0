import gradio as gr
from transformers import pipeline

# Load the model
generator = pipeline("text2text-generation", model="MBZUAI/LaMini-Flan-T5-783M")

# Define the function
def humanize_text(input_text):
    if not input_text.strip():
        return "Please enter some text to humanize."
    prompt = "Paraphrase this more naturally: " + input_text
    result = generator(prompt, max_length=256, do_sample=True)
    return result[0]["generated_text"]

# Interface to expose /run/predict
gr.Interface(
    fn=humanize_text,
    inputs=gr.Textbox(lines=6, label="Input Text"),
    outputs=gr.Textbox(label="Humanized Text"),
    title="🤖 AI Humanizer",
    description="Enter AI-generated or robotic text and get a more natural, human-sounding version."
).launch()
