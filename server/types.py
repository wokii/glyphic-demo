import json
import re

from pydantic import BaseModel, Field, computed_field
from typing import List, Optional
from datetime import datetime


class Profile(BaseModel):
    """Profile information for a call participant"""

    job_title: str
    location: str
    photo_url: str
    linkedin_url: str


class Party(BaseModel):
    """Represents a participant in a call"""

    name: str
    email: Optional[str] = None
    profile: Optional[Profile] = None


class CallMetadata(BaseModel):
    """Metadata about the call"""

    title: str
    duration: int
    start_time: datetime
    parties: List[Party]


class Message(BaseModel):
    """Represents a single message in the conversation"""

    timestamp: str
    speaker: str
    content: str
    speaker_role: Optional[str] = None


class FormattedTranscript(BaseModel):
    """A structured version of the transcript"""

    messages: List[Message]

    @classmethod
    def from_raw_text(cls, text: str) -> "FormattedTranscript":
        """Parse raw transcript text into structured format"""
        # Regular expression to match transcript lines
        pattern = r"<(\d+:\d+)> (.*?) \((.*?)\):\n(.*?)(?=\n<|$)"
        matches = re.finditer(pattern, text, re.DOTALL)

        messages = []
        for match in matches:
            timestamp, speaker_role, speaker, content = match.groups()
            # Clean up the content by removing extra newlines
            content = content.strip()

            messages.append(
                Message(
                    timestamp=timestamp,
                    speaker=speaker,
                    speaker_role=speaker_role,  # e.g., "Buyer 0" or "Seller 1"
                    content=content,
                )
            )

        return cls(messages=messages)

    def to_text(self) -> str:
        """Convert structured format back to text"""
        return "\n\n".join(
            [f"[{msg.timestamp}] {msg.speaker}: {msg.content}" for msg in self.messages]
        )

    def to_markdown(self) -> str:
        """Convert to markdown format"""
        return "\n\n".join(
            [
                f"**{msg.speaker}** ({msg.timestamp})  \n{msg.content}"
                for msg in self.messages
            ]
        )

    def get_speaker_messages(self, speaker: str) -> List[Message]:
        """Get all messages from a specific speaker"""
        return [msg for msg in self.messages if msg.speaker == speaker]


class Transcript(BaseModel):
    """Contains both raw and formatted transcript"""

    text: str

    @computed_field
    @property
    def formatted(self) -> FormattedTranscript:
        """Parse and return formatted version of transcript"""
        return FormattedTranscript.from_raw_text(self.text)


class InferenceResults(BaseModel):
    """Results from AI inference on the call"""

    call_summary: str
    # Add other inference fields as needed


class CallRecord(BaseModel):
    """Main class representing a single call record"""

    id: str = Field(..., description="Unique identifier for the call record")
    created_at_utc: datetime = Field(..., description="When the record was created")
    call_metadata: CallMetadata = Field(..., description="Metadata about the call")
    transcript: Transcript = Field(..., description="Call transcript")
    inference_results: InferenceResults = Field(..., description="AI inference results")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# Example usage:
if __name__ == "__main__":
    # Load the JSON file
    with open("../calls.json", "r") as f:
        data = json.load(f)

    # Parse all call records
    calls = [CallRecord.model_validate(record) for record in data]

    # Print some basic info about each call
    for call in calls:
        print(f"\nCall: {call.call_metadata.title}")
        print(f"Duration: {call.call_metadata.duration} seconds")
        print(f"Participants: {len(call.call_metadata.parties)}")
        print(f"Summary: {call.inference_results.call_summary}")
        print(f"Formatted: {call.transcript.formatted}")
        print("-" * 80)
