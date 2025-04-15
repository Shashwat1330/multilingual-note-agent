from deepseek import DeepSeekClient
import os

os.environ["DEEPSEEK_API_KEY"] = "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"

client = DeepSeekClient(api_key=os.getenv("DEEPSEEK_API_KEY"))

query = "Can you tell me a fact about Paris?"

try:
    response = client.ask(query)
    print("Response:", response["answer"])
except Exception as e:
    print(f"An error occurred: {e}")
