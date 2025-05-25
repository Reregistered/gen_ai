import argparse
from app.xls_handler import load_xls, save_xls
from app.gemini_handler import configure_gemini, generate_text_from_row, GeminiAPIError
import pandas as pd
import sys
# import os # Not strictly needed here as configure_gemini handles API key env var directly

def main():
    """Main application flow."""
    parser = argparse.ArgumentParser(description="Process rows from an Excel file using Gemini API and save results.")
    parser.add_argument("input_file", type=str, help="Path to the input Excel file (XLS/XLSX).")
    parser.add_argument("output_file", type=str, help="Path to save the output Excel file (XLS/XLSX).")
    parser.add_argument("prompt_template", type=str, help="Prompt template with placeholders for column names (e.g., 'Summarize: {text_column}').")
    parser.add_argument("new_column_name", type=str, help="Name of the new column to store Gemini predictions.")
    # Optional: Add model_name if you want to make it configurable
    # parser.add_argument("--model_name", type=str, default="gemini-pro", help="Name of the Gemini model to use.")

    args = parser.parse_args()

    # 1. Configure Gemini
    try:
        configure_gemini()
        print("Gemini API configured successfully.")
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except GeminiAPIError as e: # Should configure_gemini raise this? Current impl. does.
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)


    # 2. Load XLS
    try:
        print(f"Loading data from '{args.input_file}'...")
        df = load_xls(args.input_file)
        print(f"Successfully loaded {len(df)} rows.")
    except FileNotFoundError as e:
        print(f"File Loading Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e: # Handles invalid Excel files
        print(f"File Loading Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e: # Catch-all for other unexpected loading errors
        print(f"An unexpected error occurred while loading the file: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Process Rows
    results = []
    total_rows = len(df)
    print(f"\nProcessing {total_rows} rows...")

    for index, row in df.iterrows():
        try:
            generated_text = generate_text_from_row(row, args.prompt_template) #, args.model_name if added
            results.append(generated_text)
            print(f"Processed row {index + 1} of {total_rows}. Result: '{generated_text[:50]}...'")
        except GeminiAPIError as e:
            print(f"Error on row {index + 1}: Gemini API Error - {e}. Using placeholder 'ERROR_API'.", file=sys.stderr)
            results.append("ERROR_API")
        except KeyError as e: # Raised by generate_text_from_row if placeholder is bad
            print(f"Error on row {index + 1}: Key Error - {e}. Check prompt template and column names. Using placeholder 'ERROR_KEY'.", file=sys.stderr)
            results.append("ERROR_KEY")
        except Exception as e: # Catch-all for other unexpected errors during row processing
            print(f"Error on row {index + 1}: Unexpected error - {e}. Using placeholder 'ERROR_UNEXPECTED'.", file=sys.stderr)
            results.append("ERROR_UNEXPECTED")
            
    # 4. Add Results to DataFrame
    if len(results) == len(df):
        df[args.new_column_name] = results
        print(f"\nAdded new column '{args.new_column_name}' with results.")
    else:
        print(f"Error: Number of results ({len(results)}) does not match number of rows ({len(df)}). Cannot add column.", file=sys.stderr)
        sys.exit(1) # Or handle more gracefully, e.g. by not saving or saving partial

    # 5. Save XLS
    try:
        print(f"Saving processed data to '{args.output_file}'...")
        save_xls(df, args.output_file)
        print(f"Processing complete. Output saved to '{args.output_file}'")
    except IOError as e:
        print(f"File Saving Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e: # Catch-all for other unexpected saving errors
        print(f"An unexpected error occurred while saving the file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
