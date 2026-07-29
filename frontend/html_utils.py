"""
SEABISCUIT - HTML String Helper
Collapses multi-line HTML blobs before they reach st.markdown(unsafe_allow_html=True).
"""


def compact_html(html: str) -> str:
    """Flattens a multi-line HTML string to one line with no leading indentation and no blank
    lines. Streamlit's markdown renderer follows CommonMark: 4+ spaces of leading whitespace on
    a line is an indented code block, and a whitespace-only line ends an HTML block early — both
    of which turn Python-source-indented f-string HTML into literal visible text instead of a
    rendered card/table. Joining on a single space keeps tag boundaries valid."""
    return " ".join(line.strip() for line in html.splitlines() if line.strip())
