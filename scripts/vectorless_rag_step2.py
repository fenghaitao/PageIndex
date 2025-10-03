"""
Vectorless RAG Step 2-3: Reasoning-Based Retrieval with LiteLLM

This script implements Steps 2-3 of the PageIndex vectorless RAG workflow:
- Step 2: Use LLM for tree search to identify relevant nodes
- Step 3: Extract context and generate answers

Usage Examples:

    # About templates
    .venv/bin/python3 scripts/vectorless_rag_step2.py \
        --json_path results.4.1/drm_structure.json \
        --model github_copilot/gpt-5-mini \
        --query "What are templates in DML?"

    # About reset mechanisms
    .venv/bin/python3 scripts/vectorless_rag_step2.py \
        --json_path results.4.1/drm_structure.json \
        --model github_copilot/gpt-5-mini \
        --query "How do reset mechanisms work in DML?"

    # About methods and parameters
    .venv/bin/python3 scripts/vectorless_rag_step2.py \
        --json_path results.4.1/drm_structure.json \
        --model github_copilot/gpt-5-mini \
        --query "What are the differences between methods and parameters in DML?"

    # About register modeling
    .venv/bin/python3 scripts/vectorless_rag_step2.py \
        --json_path results.4.1/drm_structure.json \
        --model github_copilot/gpt-5-mini \
        --query "How are registers and fields modeled in DML?"

Requirements:
    - JSON file with PageIndex tree structure (from Step 1)
    - LiteLLM configured for GitHub Copilot (uses OAuth2)
"""

import argparse
import json
import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path to import pageindex utils
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("Warning: litellm not available. Install with: pip install litellm>=1.60.0")

from pageindex import utils


def create_node_mapping(tree):
    """Create a flat mapping of node_id -> node from tree structure."""
    node_map = {}
    
    def traverse(node):
        if isinstance(node, dict):
            if 'node_id' in node:
                node_map[node['node_id']] = node
            if 'nodes' in node:
                traverse(node['nodes'])
        elif isinstance(node, list):
            for item in node:
                traverse(item)
    
    traverse(tree)
    return node_map


def load_tree_structure(json_path: str) -> dict:
    """Load the PageIndex tree structure from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both direct structure and wrapped structure
    if 'structure' in data:
        return data['structure']
    return data


async def call_llm_async(prompt: str, model: str = "gpt-4o", temperature: float = 0, api_key: str = None):
    """Call LLM with LiteLLM, supporting GitHub Copilot models."""
    if not LITELLM_AVAILABLE:
        raise ImportError("litellm is required. Install with: pip install litellm>=1.60.0")
    
    # Prepare extra headers for GitHub Copilot models
    extra_headers = None
    if model.startswith("github_copilot/"):
        extra_headers = {
            "Editor-Version": "vscode/1.85.0",
            "Copilot-Integration-Id": "vscode-chat",
        }
    
    # Use temperature=1 for certain Copilot GPT-5 models
    if model in ("github_copilot/gpt-5-mini", "github_copilot/gpt-5"):
        temperature = 1
    
    try:
        response = await litellm.acompletion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            api_key=api_key,
            extra_headers=extra_headers,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling LLM: {e}")
        raise


async def tree_search(query: str, tree: dict, model: str, api_key: str = None) -> dict:
    """
    Step 2.1: Use LLM for tree search to identify nodes containing relevant context.
    
    Returns:
        dict with 'thinking' and 'node_list' keys
    """
    print("Step 2.1: Performing tree search with LLM...")
    
    # Remove text field to reduce prompt size
    tree_without_text = utils.remove_fields(tree.copy(), fields=['text'])
    
    search_prompt = f"""
You are given a question and a tree structure of a document.
Each node contains a node id, node title, and a corresponding summary.
Your task is to find all nodes that are likely to contain the answer to the question.

Question: {query}

Document tree structure:
{json.dumps(tree_without_text, indent=2)}

Please reply in the following JSON format:
{{
    "thinking": "<Your thinking process on which nodes are relevant to the question>",
    "node_list": ["node_id_1", "node_id_2", ..., "node_id_n"]
}}
Directly return the final JSON structure. Do not output anything else.
"""
    
    tree_search_result = await call_llm_async(search_prompt, model=model, api_key=api_key)
    
    # Parse JSON response
    try:
        result_json = json.loads(tree_search_result)
        return result_json
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse JSON response. Attempting cleanup...")
        # Try to extract JSON from markdown code blocks
        cleaned = tree_search_result.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split('\n')
            cleaned = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned
        try:
            result_json = json.loads(cleaned)
            return result_json
        except:
            print(f"Error: Could not parse LLM response as JSON: {e}")
            return {"thinking": "Failed to parse response", "node_list": []}


def print_retrieved_nodes(node_list: list, node_map: dict):
    """Step 2.2: Print retrieved nodes with details."""
    print("\nStep 2.2: Retrieved Nodes:")
    print("-" * 80)
    for node_id in node_list:
        if node_id not in node_map:
            print(f"Warning: node_id {node_id} not found in tree")
            continue
        node = node_map[node_id]
        page_info = f"Page: {node.get('start_index', 'N/A')}-{node.get('end_index', 'N/A')}"
        print(f"Node ID: {node['node_id']}\t {page_info}\t Title: {node.get('title', 'Untitled')}")
    print("-" * 80)


async def generate_answer(query: str, relevant_content: str, model: str, api_key: str = None) -> str:
    """
    Step 3.2: Generate answer based on retrieved context.
    """
    print("\nStep 3.2: Generating answer with LLM...")
    
    answer_prompt = f"""
Answer the question based on the context:

Question: {query}
Context: {relevant_content}

Provide a clear, concise answer based only on the context provided.
"""
    
    answer = await call_llm_async(answer_prompt, model=model, api_key=api_key)
    return answer


async def main_async(args):
    """Main async workflow for Steps 2-3."""
    
    # Load tree structure
    print(f"Loading tree structure from: {args.json_path}")
    tree = load_tree_structure(args.json_path)
    
    if isinstance(tree, list):
        print(f"Loaded tree with {len(tree)} root nodes")
    else:
        print(f"Loaded tree: {type(tree)}")
    
    # Step 2.1: Tree search
    search_result = await tree_search(args.query, tree, args.model, args.api_key)
    
    # Print reasoning process
    print("\n" + "=" * 80)
    print("REASONING PROCESS:")
    print("=" * 80)
    thinking = search_result.get('thinking', 'No reasoning provided')
    # Wrap text for better readability
    import textwrap
    wrapped = textwrap.fill(thinking, width=80)
    print(wrapped)
    print("=" * 80)
    
    # Step 2.2: Print retrieved nodes
    node_map = create_node_mapping(tree)
    node_list = search_result.get('node_list', [])
    print_retrieved_nodes(node_list, node_map)
    
    # Step 3.1: Extract relevant context
    print("\nStep 3.1: Extracting relevant context from retrieved nodes...")
    relevant_texts = []
    for node_id in node_list:
        if node_id in node_map:
            node = node_map[node_id]
            # Use 'text' if available, otherwise use 'summary'
            if 'text' in node:
                relevant_texts.append(node['text'])
            elif 'summary' in node:
                # Format with title for better context
                title = node.get('title', 'Section')
                summary = node['summary']
                relevant_texts.append(f"[{title}]\n{summary}")
            else:
                print(f"Warning: Node {node_id} has no 'text' or 'summary' field")
        else:
            print(f"Warning: Node {node_id} not found in tree")
    
    if not relevant_texts:
        print("Error: No relevant context found. Cannot generate answer.")
        return
    
    relevant_content = "\n\n".join(relevant_texts)
    
    # Show preview of retrieved context
    print("\nRetrieved Context Preview:")
    print("-" * 80)
    preview = relevant_content[:500] + ('...' if len(relevant_content) > 500 else '')
    print(preview)
    print("-" * 80)
    print(f"Total context length: {len(relevant_content)} characters")
    
    # Step 3.2: Generate answer
    answer = await generate_answer(args.query, relevant_content, args.model, args.api_key)
    
    # Print final answer
    print("\n" + "=" * 80)
    print("GENERATED ANSWER:")
    print("=" * 80)
    wrapped_answer = textwrap.fill(answer, width=80)
    print(wrapped_answer)
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Vectorless RAG Step 2-3: Reasoning-Based Retrieval with LiteLLM"
    )
    parser.add_argument(
        "--json_path",
        required=True,
        help="Path to JSON file with PageIndex tree structure"
    )
    parser.add_argument(
        "--model",
        default="github_copilot/gpt-5-mini",
        help="Model to use (e.g., github_copilot/gpt-5-mini, gpt-4o)"
    )
    parser.add_argument(
        "--query",
        required=True,
        help="Query/question to answer"
    )
    parser.add_argument(
        "--api_key",
        default=None,
        help="Optional API key (LiteLLM uses OAuth2 for GitHub Copilot by default)"
    )
    
    args = parser.parse_args()
    
    # Check if JSON file exists
    if not os.path.isfile(args.json_path):
        print(f"Error: JSON file not found: {args.json_path}")
        sys.exit(1)
    
    # Check LiteLLM availability
    if not LITELLM_AVAILABLE:
        print("Error: litellm is required but not installed.")
        print("Install with: pip install litellm>=1.60.0")
        sys.exit(1)
    
    # Run async main
    asyncio.run(main_async(args))


if __name__ == '__main__':
    main()
