import json

def remove_text(file_path, text_to_remove):
    """
    Removes a specific text from the 'content' field of JSON objects
    within a JSON file.

    Args:
        file_path (str): The path to the JSON file.
        text_to_remove (str): The exact text to be removed.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            if 'content' in item and isinstance(item['content'], str):
                item['content'] = item['content'].replace(text_to_remove, '')

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Successfully removed the specified text from the 'content' field in '{file_path}'.")

    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{file_path}': {e}")
    except UnicodeDecodeError as e:
        print(f"Error decoding file '{file_path}' with UTF-8 encoding: {e}")
        print("Trying again with 'latin-1' encoding...")
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                data = json.load(f)
            for item in data:
                if 'content' in item and isinstance(item['content'], str):
                    item['content'] = item['content'].replace(text_to_remove, '')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Successfully removed the specified text using 'latin-1' encoding.")
        except Exception as e2:
            print(f"Error processing with 'latin-1' encoding: {e2}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    file_path = "articles_5.json"
    text_to_remove = "\n--\nIf you liked this story,sign up for The Essential List newsletter– a handpicked selection of features, videos and can't-miss news, delivered to your inbox twice a week.\nFor more Travel stories from the BBC, follow us onFacebook,XandInstagram.\n"
    remove_text(file_path, text_to_remove)