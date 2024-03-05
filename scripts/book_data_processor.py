import json
import sys

def convert_json_to_text(json_data):
    text_content = ""

    for author, author_data in json_data.items():
        for book in author_data["books"]:
            print(book)
            text_content += f"Author name is {author}, "
            text_content += f"Book Title is {book['title']}, "
            text_content += f"Book Genre is {book['genre']}, "
            text_content += f"Book Target Age Group is {book['target_age_group']}" if 'target_age_group' in book else f"\tTarget Age Group is {book['target_age']}"
            text_content += f", Book Summary is {book['summary']}\n\n"

    return text_content

def save_text_to_file(text_content, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(text_content)

if __name__ == "__main__":
    # Check if the JSON file path is provided
    if len(sys.argv) != 2:
        print("Usage: python book_data_processor.py <path_to_json_file>")
        sys.exit(1)

    json_file_path = sys.argv[1]

    try:
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file_path}")
        sys.exit(1)

    # Convert JSON data to text
    text_content = convert_json_to_text(json_data)

    # Save text to a file
    output_file = "books_summary.txt"
    save_text_to_file(text_content, output_file)

    print(f"Text content saved to {output_file}")