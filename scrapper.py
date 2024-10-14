import json
import os
import markdown
from bs4 import BeautifulSoup
import aiofiles
import asyncio


async def extract_markdown_content(file_path):
    """Extract titles and plain text from a Markdown file asynchronously."""
    result = []

    # Read the file content asynchronously
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
        content = await f.read()

    # Convert Markdown to HTML
    html = markdown.markdown(content)

    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Initialize variables to keep track of the current header
    current_header = None
    current_content = []

    # Loop through all elements in the soup
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li']):
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:  # If the element is a header
            # If we were capturing content, save it under the last header
            result.append({"Heading": current_header, "Content": current_content})
            current_header = element.get_text(strip=True)
            current_content = []
        elif current_header:  # If it's not a header, add to current content
            if element.name in ['p', 'li']:  # Only capture paragraphs and list items
                text = element.get_text(strip=True)
                if text:  # Ensure it's not empty
                    current_content.extend(text.split('\n'))

    return result


async def process_markdown_in_folder(folder_path):
    """Process all Markdown files in the specified folder and its subfolders asynchronously."""
    contents = []

    for root, dirs, files in os.walk(folder_path):
        markdown_tasks = []
        for file in files:
            if file.endswith('.md'):  # Check for Markdown files
                file_path = os.path.join(root, file)
                markdown_tasks.append(extract_markdown_content(file_path))

        # Wait for all the markdown extraction tasks to complete
        markdown_results = await asyncio.gather(*markdown_tasks)

        # Flatten the results list
        for result in markdown_results:
            contents.extend(result)

    return contents


async def main():
    folder_path = 'handbook'  # Path to the handbook folder
    contents = await process_markdown_in_folder(folder_path)
    result = []
    # Output results asynchronously
    async with aiofiles.open('handbook.json', 'w', encoding='utf-8') as output_file:
        for content in contents:
            if content['Content']:
                result.append({"Title": content['Heading'], "Content": content['Content']})
        await output_file.write(json.dumps(result))

    print("Extraction completed. Results saved to 'handbook.json'.")


if __name__ == '__main__':
    asyncio.run(main())

