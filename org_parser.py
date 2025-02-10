import re
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()
# Database connection settings
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

class OrgNode:
    """A simple Org mode node representation."""
    def __init__(self, heading, body="", todo=None, children=None):
        self.heading = heading
        self.body = body
        self.todo = todo
        self.children = children if children is not None else []


def extract_clean_description_and_subtree(node_body):
    """Extracts the task description and returns the remaining subtree separately."""
    if not node_body:
        return "", ""  # No description or subtree available

    lines = node_body.split("\n")  # Split into lines
    description_lines = []
    subtree_lines = []

    found_subtask = False  # Flag to check when we hit a subtask

    for line in lines:
        stripped_line = line.strip()

        # Detect Org headings (*, **) as subtasks
        if re.match(r"^\s*\*{1,3} ", line):
            found_subtask = True  # Start of a new subtask detected

        if found_subtask:
            subtree_lines.append(line)  # Store everything after the first subtask
        else:
            description_lines.append(stripped_line)  # Store description

    description = "\n".join(description_lines).strip()
    subtree = "\n".join(subtree_lines).strip()

    return description, subtree

def parse_org_subtasks(subtree_text):
    """Parses an Org-mode subtree string into structured nodes, handling deep nesting."""
    if not subtree_text.strip():
        return []

    nodes = []
    current_node = None
    body_lines = []
    stack = []  # Track nested levels of subtasks

    for line in subtree_text.split("\n"):
        stripped_line = line.strip()

        # Detect a new task header (subtask)
        match = re.match(r"^(\s*)(\*+)\s+(TODO|DONE)?\s*(.+)", line)
        if match:
            indent, stars, todo, title = match.groups()
            depth = len(stars)  # Determine task depth from the number of stars (*, **, ***)

            # Store previous node before switching to a new one
            if current_node:
                current_node.body = "\n".join(body_lines).strip()
                body_lines = []  # Reset body lines

                # Handle proper nesting using stack
                while stack and stack[-1][0] >= depth:
                    stack.pop()  # Remove nodes until we reach the correct level

                if stack:
                    stack[-1][1].children.append(current_node)  # Add to the parent node
                else:
                    nodes.append(current_node)  # Top-level node

            # Create a new subtask node
            current_node = OrgNode(heading=title, todo=todo, body="")
            stack.append((depth, current_node))  # Store depth and node reference
        else:
            # Add to body if no new task header is found
            body_lines.append(stripped_line)

    # Store the last node
    if current_node:
        current_node.body = "\n".join(body_lines).strip()
        while stack and stack[-1][0] >= depth:
            stack.pop()
        if stack:
            stack[-1][1].children.append(current_node)
        else:
            nodes.append(current_node)

    return nodes
