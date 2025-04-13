from transformers import pipeline

# Load the summarization pipeline from HuggingFace
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(input_text: str) -> str:
    # Generate summary
    summary = summarizer(input_text, max_length=50, min_length=25, do_sample=False)
    return summary[0]['summary_text']
