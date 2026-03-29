# Implementation Plan
### A Hybrid Memory System for Persistent Developer Context

This plan outlines the creation of **Project Helix**, a CLI-driven tool that extracts architectural patterns and decisions from a codebase and syncs them to a persistent, searchable memory using `memsearch`.

---

## 🎯 Overview
The goal is to move away from "session-based amnesia" in AI agents. **Project Helix** creates a bridge between a local project's specific context and a global "Developer Profile" that carries your coding standards across all your repositories.

---

## 🛠 Phase 1: The Extractor (Repository Mining)
The extractor identifies "High-Signal" data points to avoid token noise and ensure the AI focuses on intent rather than just syntax.

* **Project Topology:** Use `GitPython` to map the folder structure and identify architectural patterns (e.g., MVC, Hexagonal, Microservices).
* **Dependency Audit:** Parse `pyproject.toml`, `requirements.txt`, or `package.json` to identify the stack.
* **Git Intent Mining:** Extract the last 50 commit messages (filtering for `feat:`, `fix:`, and `refactor:`) to understand *why* changes were made.
* **Documentation Conversion:** Use `MarkItDown` to convert local `.pdf`, `.docx`, or `.pptx` internal specs into text for indexing.

---

## 🤖 Phase 2: The Distiller (Synthesis)
Instead of indexing raw files, this phase uses an LLM to synthesize the extracted data into structured Markdown "Memory States."

* **Synthesis Engine:** Powered by `LiteLLM` to allow for local (Ollama) or cloud (Gemini/OpenAI) processing.
* **Structured Output:** Use `Instructor` to ensure the LLM outputs valid Markdown files:
    * `ARCHITECTURE.md`: High-level design choices.
    * `CONVENTIONS.md`: Naming, testing patterns, and error handling.
    * `HISTORY.md`: Critical project pivot points found in Git logs.
* **Target:** These files are saved to the local `./.memsearch/memory/` directory.

---

## 🧠 Phase 3: The Hybrid Brain (Storage & Sync)
This phase addresses the **Global vs. Local** storage strategy by implementing a "Inheritance" model.

* **Global Helix (`~/.dev_brain/`):** Stores your universal preferences (e.g., "I prefer Pydantic for validation," "Always use async for I/O").
* **Local Context (`./.memsearch/`):** Stores project-specific details.
* **Sync Logic:**
    1.  **Initial Hydration:** When running `Helix init`, the tool symlinks or copies the global profile into the local project memory.
    2.  **Indexing:** The `memsearch` library indexes both folders into a single `Milvus Lite` vector database stored locally in the project.
    3.  **Git Hook:** A `post-commit` hook triggers a partial re-index to keep the memory fresh with your latest decisions.

---

## 🔌 Phase 4: The Recall Loop (IDE Integration)
The final step is making this memory accessible to your AI coding assistant (Cursor, VS Code, or Claude Code).

* **MCP Server:** Build a server using `FastMCP` that exposes the `memsearch` index.
* **Tools Provided:**
    * `recall_practice(query)`: Search for how a specific task was handled before.
    * `get_project_context()`: Provides a summary of the current "Helix" of the project.
* **IDE Setup:** Add the MCP server to your IDE configuration (e.g., `cursor-settings.json`).

---

## 💻 Tech Stack & CLI Structure

| Component | Technology |
| :--- | :--- |
| **CLI Framework** | `Typer` |
| **Code/Git Analysis** | `GitPython` + `Tree-sitter` |
| **Document Parsing** | `MarkItDown` |
| **RAG/Memory** | `memsearch` + `Milvus Lite` |
| **IDE Bridge** | `FastMCP` |

### Proposed CLI Commands
* `helix init`: Sets up the local `.memsearch` folder and links the Global Helix.
* `helix snapshot`: Runs the Extractor and Distiller to refresh memory states.
* `helix serve`: Starts the MCP server for IDE integration.
* `helix push-global`: Moves a local pattern (e.g., a great new utility) to your `~/.dev_brain/`.
