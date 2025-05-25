import pandas as pd

def load_xls(file_path: str) -> pd.DataFrame:
    """
    Loads data from an XLS/XLSX or CSV file into a pandas DataFrame.

    Args:
        file_path: The path to the Excel or CSV file.

    Returns:
        A pandas DataFrame containing the data from the file.

    Raises:
        FileNotFoundError: If the file is not found at the given path.
        ValueError: If the file is not a valid Excel/CSV file or is corrupted.
    """
    try:
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            # Let pandas infer engine for .xls/.xlsx
            df = pd.read_excel(file_path, engine=None) 
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File not found at path: {file_path}")
    except pd.errors.EmptyDataError: # Specific error for empty CSV/Excel files
        raise ValueError(f"Error: File is empty: {file_path}")
    except Exception as e:
        # Broad exception for other pandas read_excel/read_csv errors
        if 'Excel file format cannot be determined' in str(e) or 'is not a valid Csv file' in str(e) or isinstance(e, ValueError):
            raise ValueError(f"Error: File is not a valid Excel/CSV file or is corrupted: {file_path}. Details: {e}")
        raise  # Re-raise other unexpected errors


def save_xls(df: pd.DataFrame, file_path: str):
    """
    Saves a pandas DataFrame to an XLS/XLSX or CSV file.

    Args:
        df: The pandas DataFrame to save.
        file_path: The path where the Excel or CSV file will be saved.

    Raises:
        IOError: If there is an issue writing the file to the specified path.
        TypeError: If the input df is not a pandas DataFrame.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")
    
    try:
        if file_path.lower().endswith('.csv'):
            df.to_csv(file_path, index=False)
        elif file_path.lower().endswith('.xlsx'):
            df.to_excel(file_path, index=False, engine='openpyxl')
        elif file_path.lower().endswith('.xls'):
            # For .xls, pandas defaults to xlwt if installed.
            # If xlwt is not installed, pandas will raise an error.
            # Consider adding xlwt to requirements.txt if .xls output is critical.
            df.to_excel(file_path, index=False) # Let pandas handle engine or raise error
        else:
            # Default to .xlsx if no recognized extension, or raise error
            # For safety, let's enforce a known extension or raise an error
            raise ValueError(f"Unsupported file extension: {file_path}. Please use .csv, .xls, or .xlsx.")

    except (IOError, OSError) as e: # Catch both IOError and OSError for broader compatibility
        raise IOError(f"Error: Could not write file to path: {file_path}. Details: {e}")
    except Exception as e: # Catch other potential pandas/engine errors
        raise IOError(f"Error: Failed to save file '{file_path}' due to an unexpected error. Details: {e}")

# Example Usage (optional, for testing)
if __name__ == '__main__':
    # Create a dummy DataFrame
    data = {'col1': [1, 2], 'col2': ['text1', 'text2']}
    dummy_df = pd.DataFrame(data)

    # Test save_xls for different formats
    test_save_path_xlsx = 'test_output.xlsx'
    test_save_path_xls = 'test_output.xls'
    test_save_path_csv = 'test_output.csv'
    
    try:
        save_xls(dummy_df, test_save_path_xlsx)
        print(f"Successfully saved to {test_save_path_xlsx}")
        save_xls(dummy_df, test_save_path_xls) # Requires xlwt to be installed
        print(f"Successfully saved to {test_save_path_xls}")
        save_xls(dummy_df, test_save_path_csv)
        print(f"Successfully saved to {test_save_path_csv}")
    except Exception as e:
        print(f"Error during save_xls test: {e}")

    # Test load_xls for different formats
    try:
        loaded_df_xlsx = load_xls(test_save_path_xlsx)
        print(f"Successfully loaded from {test_save_path_xlsx}:\n{loaded_df_xlsx}")
        loaded_df_xls = load_xls(test_save_path_xls)
        print(f"Successfully loaded from {test_save_path_xls}:\n{loaded_df_xls}")
        loaded_df_csv = load_xls(test_save_path_csv)
        print(f"Successfully loaded from {test_save_path_csv}:\n{loaded_df_csv}")
    except Exception as e:
        print(f"Error during load_xls test: {e}")

    # Test error handling for load_xls
    try:
        load_xls("non_existent_file.xlsx")
    except FileNotFoundError as e:
        print(f"Caught expected error for non_existent_file: {e}")
    
    try:
        with open("not_a_valid_file.txt", "w") as f:
            f.write("This is not an excel or csv file.")
        load_xls("not_a_valid_file.txt")
    except ValueError as e:
        print(f"Caught expected error for invalid file format: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during not_a_valid_file.txt test: {e}")

    # Test error handling for save_xls
    try:
        save_xls("not a dataframe", "error_test.xlsx")
    except TypeError as e:
        print(f"Caught expected error for non-dataframe input: {e}")
    
    try:
        save_xls(dummy_df, "unsupported.ext")
    except ValueError as e:
        print(f"Caught expected error for unsupported extension: {e}")

    # Clean up test files (optional)
    import os
    try:
        if os.path.exists(test_save_path_xlsx): os.remove(test_save_path_xlsx)
        if os.path.exists(test_save_path_xls): os.remove(test_save_path_xls)
        if os.path.exists(test_save_path_csv): os.remove(test_save_path_csv)
        if os.path.exists("not_a_valid_file.txt"): os.remove("not_a_valid_file.txt")
        if os.path.exists("not_an_excel.txt"): # From original test, ensure cleanup
            os.remove("not_an_excel.txt")
    except Exception as e:
        print(f"Error cleaning up test files: {e}")
    # Create a dummy DataFrame
    data = {'col1': [1, 2], 'col2': [3, 4]}
    dummy_df = pd.DataFrame(data)

    # Test save_xls
    test_save_path_xlsx = 'test_output.xlsx'
    test_save_path_xls = 'test_output.xls'
    try:
        save_xls(dummy_df, test_save_path_xlsx)
        print(f"Successfully saved to {test_save_path_xlsx}")
        save_xls(dummy_df, test_save_path_xls)
        print(f"Successfully saved to {test_save_path_xls}")
    except Exception as e:
        print(f"Error during save_xls test: {e}")

    # Test load_xls
    try:
        loaded_df_xlsx = load_xls(test_save_path_xlsx)
        print(f"Successfully loaded from {test_save_path_xlsx}:\n{loaded_df_xlsx}")
        loaded_df_xls = load_xls(test_save_path_xls)
        print(f"Successfully loaded from {test_save_path_xls}:\n{loaded_df_xls}")
    except Exception as e:
        print(f"Error during load_xls test: {e}")

    # Test error handling for load_xls
    try:
        load_xls("non_existent_file.xlsx")
    except FileNotFoundError as e:
        print(f"Caught expected error: {e}")
    
    try:
        # Create a dummy non-excel file
        with open("not_an_excel.txt", "w") as f:
            f.write("This is not an excel file.")
        load_xls("not_an_excel.txt")
    except ValueError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during not_an_excel.txt test: {e}")

    # Test error handling for save_xls
    try:
        save_xls("not a dataframe", "error_test.xlsx")
    except TypeError as e:
        print(f"Caught expected error: {e}")
    
    # Clean up test files (optional)
    import os
    try:
        if os.path.exists(test_save_path_xlsx):
            os.remove(test_save_path_xlsx)
        if os.path.exists(test_save_path_xls):
            os.remove(test_save_path_xls)
        if os.path.exists("not_an_excel.txt"):
            os.remove("not_an_excel.txt")
    except Exception as e:
        print(f"Error cleaning up test files: {e}")
