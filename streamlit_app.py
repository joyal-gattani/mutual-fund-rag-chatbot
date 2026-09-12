import streamlit as st

from src.app import retrieve_context, generate_answer


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="HDFC Mutual Fund AI Assistant",
    page_icon="📊",
    layout="centered"
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📊 HDFC Mutual Fund AI Assistant")

st.write(
    "Ask questions about selected HDFC Mutual Funds "
    "using source-grounded information from official fund documents."
)

st.info(
    "Answers are generated only from the provided HDFC Mutual Fund documents. "
    "This tool does not provide personalized investment advice."
)


# --------------------------------------------------
# QUESTION INPUT
# --------------------------------------------------

query = st.text_input(
    "Ask your question",
    placeholder="e.g. What is the AUM of HDFC Mid Cap Fund?"
)


# --------------------------------------------------
# ASK BUTTON
# --------------------------------------------------

if st.button("Ask", type="primary"):

    if not query.strip():

        st.warning("Please enter a question.")

    else:

        with st.spinner("Searching documents and generating answer..."):

            # Retrieve only top 3 most relevant sources
            contexts = retrieve_context(query, top_k=8)

            # Generate grounded answer
            answer = generate_answer(query, contexts)


        # --------------------------------------------------
        # ANSWER
        # --------------------------------------------------

        st.subheader("Answer")

        st.markdown(answer)


        # --------------------------------------------------
        # SOURCES
        # --------------------------------------------------

        st.subheader("Sources")

        if not contexts:

            st.write("No relevant sources found.")

        else:

            for i, context in enumerate(contexts):

                metadata = context["metadata"]

                fund = metadata.get(
                    "fund",
                    "Unknown Fund"
                )

                document = metadata.get(
                    "document_name",
                    "Unknown Document"
                )

                page = metadata.get(
                    "page",
                    "Unknown Page"
                )


                with st.expander(
                    f"Source {i + 1}: {fund} — Page {page}"
                ):

                    st.write(
                        f"**Document:** {document}"
                    )

                    st.write(
                        f"**Page:** {page}"
                    )

                    st.write(
                        f"**Fund:** {fund}"
                    )

                    st.write(
                        "**Retrieved content:**"
                    )

                    st.write(
                        context["text"]
                    )