import os
from typing import Optional
from anthropic import Anthropic

import config
from server.types import CallRecord

STANDARD_QUESTIONS = [
    "What are the main pain points mentioned by the buyer?",
    "What next steps or action items were agreed upon?",
    "What objections or concerns were raised?",
    "What is the current state of the deal/opportunity?",
    "Were any specific deadlines or timelines mentioned?",
]


class CallAnalyzer:
    def __init__(self):
        """Initialize the CallAnalyzer with Anthropic API key."""
        self.client = Anthropic(
            api_key=config.settings.claude_api_key.get_secret_value(),
        )

    def analyze_call(self, call: CallRecord, question: str) -> str:
        """Ask a question about a specific call transcript."""
        try:
            # Create the prompt with the question
            prompt = f"""You are a helpful assistant analyzing sales call transcripts. 
            Based on the following call transcript, please answer this question: {question}

            Remember to:
            - Be specific and cite relevant parts of the conversation
            - Stay objective and base answers only on what's in the transcript
            - Say "I cannot determine this from the transcript" if the information isn't present

            Call Title: {call.call_metadata.title}
            Date: {call.call_metadata.start_time.strftime("%Y-%m-%d %H:%M:%S")}
            Duration: {call.call_metadata.duration // 60} minutes

            Transcript:
            {call.transcript.text}"""

            # Get response from Claude
            message = self.client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=1000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )

            return message.content[0].text

        except Exception as e:
            return f"Error analyzing call: {str(e)}"

    def ask_question(self, call: CallRecord, question: str) -> str:
        """Wrapper method for analyze_call."""
        return self.analyze_call(call, question)

    def get_key_insights(self, call: CallRecord) -> str:
        """Get standard key insights from a call."""

        insights = []
        for question in STANDARD_QUESTIONS:
            answer = self.analyze_call(call, question)
            insights.append(f"Q: {question}\nA: {answer}\n")

        return "\n".join(insights)

