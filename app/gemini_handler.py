import google.generativeai as genai
import os
import pandas as pd # Required for pd.Series type hint
from google.api_core import exceptions as google_exceptions

class GeminiAPIError(Exception):
    """Custom exception for Gemini API related errors."""
    pass

def configure_gemini():
    """
    Configures the Google Generative AI SDK with an API key from environment variables.

    Raises:
        ValueError: If the GEMINI_API_KEY environment variable is not set.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not set. "
            "Please set it to your Google Generative AI API key."
        )
    try:
        genai.configure(api_key=api_key)
        print("Gemini API configured successfully.") # Optional: for confirmation
    except Exception as e:
        # This might catch errors if genai.configure itself has issues, though typically it's straightforward.
        raise GeminiAPIError(f"Failed to configure Gemini API: {e}")


def generate_text_from_row(row: pd.Series, prompt_template: str, model_name: str = "gemini-pro") -> str:
    """
    Generates text for a given row of data using a prompt template and the Gemini API.

    Args:
        row: A pandas Series representing a row from the DataFrame.
        prompt_template: A string template with placeholders like {column_name}.
        model_name: The name of the Gemini model to use (default: "gemini-pro").

    Returns:
        The generated text as a string.

    Raises:
        GeminiAPIError: If there's an issue with the API call or processing the response.
        KeyError: If a placeholder in the prompt_template is not found in the row's columns.
    """
    try:
        # Format the prompt using data from the row
        # This uses f-string like capabilities if prompt_template is "Summarize: {text}"
        # and row is a Series. We can iterate through row.items() to fill the template.
        # A more robust way is to use .format(**row.to_dict()) after ensuring all keys exist.
        
        # Check if all placeholders in prompt_template are in row.keys()
        required_keys = [col.strip('{}') for col in prompt_template.split() if '{' in col and '}' in col]
        for key in required_keys:
            if key not in row:
                raise KeyError(f"Placeholder '{{{key}}}' in prompt_template not found in the provided row's columns: {list(row.keys())}")

        formatted_prompt = prompt_template.format(**row.to_dict())
    except KeyError as e:
        raise KeyError(f"Error formatting prompt: {e}. Ensure all placeholders in the template exist as columns in the DataFrame row.")
    except Exception as e: # Catch any other formatting errors
        raise ValueError(f"Error formatting prompt: {e}. Template: '{prompt_template}', Row: {row.to_dict()}")

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(formatted_prompt)

        if not response.parts:
             # This case handles scenarios where the response might be empty or blocked.
             # response.prompt_feedback could be checked for block reasons.
            block_reason = ""
            if response.prompt_feedback:
                block_reason = f" (Reason: {response.prompt_feedback.block_reason})" if response.prompt_feedback.block_reason else ""
            
            # Check if candidates exist and have content
            candidate_text = None
            if response.candidates:
                candidate_text = response.candidates[0].content.parts[0].text if response.candidates[0].content and response.candidates[0].content.parts else None

            if candidate_text:
                return candidate_text # Return text even if parts is empty but candidate text exists
            
            raise GeminiAPIError(f"Gemini API returned an empty response or content was blocked{block_reason}. No text generated for prompt: '{formatted_prompt}'")

        # Accessing text, preferring response.text if available and robust
        # Gemini API typically returns text in response.text or response.candidates[0].content.parts[0].text
        generated_text = ""
        if hasattr(response, 'text') and response.text:
            generated_text = response.text
        elif response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            generated_text = response.candidates[0].content.parts[0].text
        
        if not generated_text.strip():
            # This handles cases where the text might be present but effectively empty (e.g. only whitespace)
            # or if the API indicates an issue with generation itself.
            block_reason = ""
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                block_reason = f" (Reason: {response.prompt_feedback.block_reason})"
            raise GeminiAPIError(f"Gemini API returned empty or whitespace text{block_reason} for prompt: '{formatted_prompt}'")
        
        return generated_text

    except (google_exceptions.GoogleAPIError, google_exceptions.RetryError) as e:
        # Catch specific Google API errors (includes auth, quota, server errors, etc.)
        raise GeminiAPIError(f"Gemini API call failed: {e}. Prompt: '{formatted_prompt}'")
    except KeyError as e: # This could happen if response structure is unexpected
        raise GeminiAPIError(f"Error accessing generated text from Gemini API response: {e}. Response structure might be unexpected. Response: {response}")
    except Exception as e: # Catch-all for other unexpected errors during generation
        raise GeminiAPIError(f"An unexpected error occurred during text generation with Gemini API: {e}. Prompt: '{formatted_prompt}'")

if __name__ == '__main__':
    # This block is for basic testing and assumes GEMINI_API_KEY is set.
    # To run, you would need to set the GEMINI_API_KEY environment variable.
    # Example: export GEMINI_API_KEY="your_actual_api_key"
    
    print("Running gemini_handler.py tests...")

    # 1. Test API Key Configuration
    try:
        print("\nAttempting to configure Gemini API...")
        # Unset key for testing failure (DO NOT do this in production tests without care)
        # original_key = os.environ.pop("GEMINI_API_KEY", None) 
        # if not original_key:
        #     print("GEMINI_API_KEY was not set. Skipping ValueError test for configure_gemini.")
        # else:
        #     try:
        #         configure_gemini() # Should fail if key is removed
        #     except ValueError as e:
        #         print(f"SUCCESS: Caught expected ValueError for missing API key: {e}")
        #     finally:
        #         os.environ["GEMINI_API_KEY"] = original_key # Restore key

        # Test with key set (assuming it's set in the environment for this manual test)
        if os.getenv("GEMINI_API_KEY"):
            configure_gemini()
            print("SUCCESS: configure_gemini() ran if API key was present.")
        else:
            print("SKIPPED: configure_gemini() test because GEMINI_API_KEY is not set.")
            print("Please set the GEMINI_API_KEY environment variable to test fully.")

    except GeminiAPIError as e:
        print(f"ERROR during configure_gemini test: {e}")
    except ValueError as e:
         print(f"CAUGHT during configure_gemini test (expected if key missing): {e}")


    # 2. Test Text Generation (if API key is configured)
    if os.getenv("GEMINI_API_KEY"):
        print("\nAttempting text generation...")
        try:
            configure_gemini() # Ensure it's configured for this part
            sample_data = {'product_name': 'Eco-friendly Water Bottle', 'description': 'Made from 100% recycled plastic, holds 500ml.'}
            sample_row = pd.Series(sample_data)
            prompt = "Write a short advertisement for a product named '{product_name}' which is '{description}'"
            
            print(f"Test Prompt: {prompt.format(**sample_row.to_dict())}")
            generated_ad = generate_text_from_row(sample_row, prompt)
            print(f"SUCCESS: Generated text: '{generated_ad}'")

            # Test with a non-existent column in prompt
            try:
                prompt_bad_key = "Summarize: {non_existent_column}"
                generate_text_from_row(sample_row, prompt_bad_key)
            except KeyError as e:
                print(f"SUCCESS: Caught expected KeyError for bad placeholder: {e}")

        except GeminiAPIError as e:
            print(f"ERROR during generate_text_from_row test: {e}")
        except KeyError as e:
            print(f"ERROR (KeyError) during generate_text_from_row test setup: {e}")
        except Exception as e:
            print(f"UNEXPECTED ERROR during generate_text_from_row test: {e}")
    else:
        print("\nSKIPPED: generate_text_from_row tests because GEMINI_API_KEY is not set.")
        print("Please set the GEMINI_API_KEY environment variable to test fully.")

    print("\n gemini_handler.py tests finished.")
