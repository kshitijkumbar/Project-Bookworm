import pandas as pd
import sys

def convert_csv_to_text(csv_file_path, output_file):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file_path)

    # Create a text string to store the natural language content
    text_content = ""

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        if index % 10 != 0:  # Skip every third row (0-based index)
            continue
        text_content += f"Movie Release Year: {row['Release Year'] if 'Release Year' in df.columns else 'NA'}\n"
        text_content += f"Movie Title: {row['Title'] if 'Title' in df.columns else 'NA'}\n"
        text_content += f"Movie Origin/Ethnicity: {row['Origin/Ethnicity'] if 'Origin/Ethnicity' in df.columns else 'NA'}\n"
        text_content += f"Movie Director: {row['Director'] if 'Director' in df.columns else 'NA'}\n"
        text_content += f"Movie Cast: {row['Cast'] if 'Cast' in df.columns else 'NA'}\n"
        text_content += f"Movie Genre: {row['Genre'] if 'Genre' in df.columns else 'NA'}\n"
        text_content += f"Movie Wiki Page: {row['Wiki Page'] if 'Wiki Page' in df.columns else 'NA'}\n"
        text_content += f"Movie Plot: {row['Plot'] if 'Plot' in df.columns else 'NA'}\n\n"

    # Save the text content to a file
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(text_content)

if __name__ == "__main__":
    
    # Check if the CSV file path is provided
    if len(sys.argv) != 2:
        print("Usage: python movie_data_processor.py <path_to_csv_file>")
        sys.exit(1)

    # Specify the path to the CSV file
    csv_file_path = sys.argv[1]
    

    # Specify the output file name
    output_file = "movie_data_summary.txt"

    # Convert CSV to text
    convert_csv_to_text(csv_file_path, output_file)

    print(f"Text content saved to {output_file}")