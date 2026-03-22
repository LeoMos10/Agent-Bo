from core.agent import Agent


def main():
    agent = Agent()

    print("AI Agent Started.")
    print("Type 'exit' to quit.\n")

    while True:
        task = input(">>> ")

        if task.lower() == "exit":
            print("Shutting down...")
            break

        agent.process_task(task)


if __name__ == "__main__":
    main()