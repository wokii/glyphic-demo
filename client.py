import streamlit as st
import pandas as pd

from server import (
    load_calls,
    format_duration,
    ask_question,
    get_call_insights,
    STANDARD_QUESTIONS,
)


def main():
    st.set_page_config(page_title="Call Transcript Viewer", layout="wide")

    # Load data
    try:
        calls = load_calls()
    except FileNotFoundError:
        st.error("Could not find calls.json file")
        return
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return

    # Sidebar with call selection and call details
    st.sidebar.title("Call Selection")
    selected_call_title = st.sidebar.selectbox(
        "Select Call",
        options=[call.call_metadata.title for call in calls],
        format_func=lambda x: x,
    )

    # Find selected call
    selected_call = next(
        call for call in calls if call.call_metadata.title == selected_call_title
    )

    # Call details in sidebar

    # Main content area with two columns
    col1, col2 = st.columns([2, 1])

    with col1:

        st.sidebar.title("Call Details")
        metadata = selected_call.call_metadata

        st.sidebar.markdown(
            f"""
        **Duration:** {format_duration(metadata.duration)}  
        **Date:** {metadata.start_time.strftime('%Y-%m-%d %H:%M:%S')}  
        **Participants:** {len(metadata.parties)}
        """
        )

        # Call summary in sidebar
        st.sidebar.subheader("Summary")
        st.sidebar.write(selected_call.inference_results.call_summary)

        # Participants in sidebar
        st.sidebar.subheader("Participants")
        for party in metadata.parties:
            with st.sidebar.expander(party.name):
                if party.profile:
                    st.markdown(
                        f"""
                    **Role:** {party.profile.job_title}  
                    **Location:** {party.profile.location}  
                    **LinkedIn:** [{party.name}]({party.profile.linkedin_url})
                    """
                    )
                if party.email:
                    st.markdown(f"**Email:** {party.email}")

        # Message statistics in sidebar
        st.sidebar.subheader("Message Statistics")
        speaker_counts = (
            pd.DataFrame(
                [
                    {"Speaker": msg.speaker, "Messages": 1}
                    for msg in selected_call.transcript.formatted.messages
                ]
            )
            .groupby("Speaker")
            .sum()
        )

        st.sidebar.bar_chart(speaker_counts)

        st.header("Transcript")
        # Display transcript messages
        messages = selected_call.transcript.formatted.messages
        for msg in messages:
            with st.container():
                st.markdown(f"**{msg.speaker}** - {msg.timestamp}")
                st.text(msg.content)
                st.divider()

    with col2:
        st.header("Call Analysis")

        # Custom Question Section
        st.subheader("Ask a Question")
        custom_question = st.text_area(
            "Enter your question about the call:",
            placeholder="e.g., What were the main pain points discussed?",
        )

        if st.button("Get Answer"):
            if custom_question:
                with st.spinner("Analyzing..."):
                    answer = ask_question(selected_call, custom_question)
                    st.markdown("**Answer:**")
                    st.write(answer)
            else:
                st.warning("Please enter a question.")

        # Predefined Questions Section
        st.subheader("Quick Insights")
        selected_question = st.selectbox(
            "Choose a predefined question:",
            options=STANDARD_QUESTIONS,
            format_func=lambda x: x,
        )

        if st.button("Get Insight"):
            with st.spinner("Analyzing..."):
                answer = ask_question(selected_call, selected_question)
                st.markdown("**Answer:**")
                st.write(answer)

        # Option to get all insights
        if st.button("Get All Insights"):
            with st.spinner("Analyzing all aspects..."):
                insights = get_call_insights(selected_call)
                st.markdown("**Complete Analysis:**")
                st.write(insights)


if __name__ == "__main__":
    main()
