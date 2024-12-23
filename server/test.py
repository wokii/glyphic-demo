from server.anthropic_client import CallAnalyzer

if __name__ == "__main__":
    # Initialize analyzer
    analyzer = CallAnalyzer()

    # Load a call
    from server import load_calls

    calls = load_calls()
    call = calls[0]  # Get first call

    # Ask a specific question
    question = "What's the buyer's main pain point?"
    answer = analyzer.ask_question(call, question)
    print(f"Question: {question}")
    print(f"Answer: {answer}\n")

    # Get key insights
    print("Key Insights:")
    insights = analyzer.get_key_insights(call)
    print(insights)
