import dotenv
import os

dotenv.load_dotenv()

print(os.getenv("API_KEY"))


def main():
    print("Hello from ai-agent-with-python!")
    print("TEst")
    print("updated")
    react_prompt = "You are awasome tool Question: {{question}}"
    prompt = react_prompt.format(question="Waht is the price of laptop")
    print(prompt)


if __name__ == "__main__":
    main()
