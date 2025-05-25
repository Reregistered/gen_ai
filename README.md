# XLS Gemini Processor

This application processes rows from an XLS/XLSX or CSV file using Google's Gemini Pro API and writes the results back to a new column in an output XLS/XLSX or CSV file.

## Features
- Reads data from `.xls`, `.xlsx`, or `.csv` files.
- Processes each row based on a user-defined prompt template.
- Leverages the Gemini Pro model for text generation.
- Writes results to a new specified column in an output Excel (`.xls`, `.xlsx`) or CSV (`.csv`) file.
- Basic error handling for file operations and API calls.

## Configuration

### Gemini API Key
Before running the application, you need to set your Gemini API key as an environment variable.

On Linux/macOS:
```bash
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

On Windows (Command Prompt):
```bash
set GEMINI_API_KEY=YOUR_API_KEY_HERE
```

On Windows (PowerShell):
```bash
$env:GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

Replace `YOUR_API_KEY_HERE` with your actual API key. The application will read this environment variable to authenticate with the Gemini API.

## Setup

1.  **Clone the repository (if applicable)**:
    ```bash
    git clone <repository_url>
    cd xls_gemini_processor
    ```

2.  **Create a virtual environment**:
    It's recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    ```
    Activate it:
    - On Linux/macOS:
      ```bash
      source venv/bin/activate
      ```
    - On Windows (Command Prompt):
      ```bash
      venv\Scripts\activate.bat
      ```
    - On Windows (PowerShell):
      ```bash
      .\venv\Scripts\Activate.ps1
      ```

3.  **Install dependencies**:
    Ensure your `GEMINI_API_KEY` is set as described in the Configuration section.
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script from the root directory of the project:

```bash
python main.py --input_file examples/sample_input.csv \
               --output_file path/to/your/output.xlsx \
               --prompt_template "For the product {ProductName}, the customer said: '{CustomerFeedback}'. What is the general sentiment and category: {Category}?" \
               --new_column_name "gemini_analysis"
```

### Command-Line Arguments

-   `--input_file` (required): Path to the input file. Can be `.xls`, `.xlsx`, or `.csv`. (e.g., `examples/sample_input.csv`)
-   `--output_file` (required): Path where the output file will be saved. Can be `.xls`, `.xlsx`, or `.csv`.
-   `--prompt_template` (required): The prompt string to be sent to the Gemini API. Use curly braces `{}` to denote column names from your input file that should be inserted into the prompt. For example, if your file has columns `product_name` and `customer_review`, your prompt could be: `"Summarize the following review for {product_name}: {customer_review}"`.
-   `--new_column_name` (required): The name of the new column that will be added to your output file containing the predictions from Gemini.

### Prompt Template Formatting

The `--prompt_template` argument is crucial. It allows you to specify how data from each row is presented to the Gemini model.
-   Enclose column names from your input file in curly braces, e.g., `{column_A}`.
-   The script will replace these placeholders with the actual values from the corresponding columns in each row before sending the prompt to Gemini.
-   Example: If a row has `ProductName: "Laptop X"` and `CustomerFeedback: "long battery life"`, and your template is `Describe {ProductName} focusing on {CustomerFeedback}.`, the actual prompt sent will be `Describe Laptop X focusing on long battery life.`

Make sure the column names in your prompt template exactly match the column headers in your input file (case-sensitive).
