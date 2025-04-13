from deepseek import DeepSeekClient
import os

# Set the new API key in the environment (you can do this in the terminal or directly in the code)
os.environ["DEEPSEEK_API_KEY"] = "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"

# Initialize the DeepSeek client with your API key
client = DeepSeekClient(api_key=os.getenv("DEEPSEEK_API_KEY"))

# Example query to the model
query = "Can you tell me a fact about Paris?"

# Call DeepSeek API to get response for the query
try:
    response = client.ask(query)
    print("Response:", response["answer"])
except Exception as e:
    print(f"An error occurred: {e}")
