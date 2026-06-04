import dotenv
import os

dotenv.load_dotenv()

print(os.getenv("API_KEY"))


def main():
    print("Hello from ai-agent-with-python!")


if __name__ == "__main__":
    main()
