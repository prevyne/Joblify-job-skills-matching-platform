import os
import sys

def generate_directory_tree(start_path):
    """
    Generates and prints a tree-like structure for a given directory.

    Args:
        start_path (str): The absolute or relative path to the directory
                          to be mapped.
    """
    # --- Configuration ---
    # Add directories or files you want to ignore to this list.
    # This is useful for ignoring clutter like __pycache__ or .git.
    ignore_list = {'.git', '__pycache__', '.vscode', 'node_modules', 'venv'}
    
    # --- Validation ---
    if not os.path.isdir(start_path):
        print(f"Error: The specified path '{start_path}' is not a valid directory.")
        return

    print(f"Directory map for: {os.path.abspath(start_path)}\n")

    # --- Core Recursive Function ---
    def walk_directory(directory, prefix=""):
        """
        Recursively walks through the directory to build the tree.

        Args:
            directory (str): The path of the directory to walk through.
            prefix (str): The prefix string for formatting the tree structure,
                          which grows with recursion depth.
        """
        # Get all items in the directory and filter out ignored ones
        try:
            items = [item for item in os.listdir(directory) if item not in ignore_list]
            # Sort items to ensure consistent order
            items.sort()
        except PermissionError:
            print(f"{prefix}├── [Permission Denied]")
            return
            
        # Pointer to keep track of the last item in the list
        pointer = "├── "
        
        for index, item in enumerate(items):
            # Check if it's the last item to use a different connector
            if index == len(items) - 1:
                pointer = "└── "

            # Get the full path of the item
            path = os.path.join(directory, item)

            # Print the item with its corresponding prefix
            print(f"{prefix}{pointer}{item}")

            # If the item is a directory, recurse into it
            if os.path.isdir(path):
                # Determine the prefix for the next level of recursion
                extension = "│   " if index < len(items) - 1 else "    "
                walk_directory(path, prefix + extension)

    # --- Initial Call ---
    # Start the recursive walk from the root of the specified path
    walk_directory(start_path)


# --- Script Execution ---
if __name__ == "__main__":
    # The script can be run with an optional command-line argument
    # to specify the directory.
    # If no argument is given, it defaults to the current directory.
    if len(sys.argv) > 1:
        # Use the directory provided by the user
        root_directory = sys.argv[1]
    else:
        # Default to the current working directory
        root_directory = "."
        
    generate_directory_tree(root_directory)

