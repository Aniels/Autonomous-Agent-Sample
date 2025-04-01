import os  
import re
import requests
from typing import List, Union
from tqdm import tqdm  # Import tqdm for the progress bar  

from dotenv import load_dotenv
from bs4 import BeautifulSoup  
from azure.storage.queue import QueueClient  # Requires Azure Storage Queue SDK  

from autonoumous.data_class import Record 
from autonoumous.AzureOpenAIChatAssistant import AzureOpenAIChatAssistant


def make_legal_file_name(name):  
    # Replace illegal characters with an underscore  
    return re.sub(r'[<>:"/\\|?*\n]', '_', name)  

# Parse the HTML agenda and extract records  
def get_record_from_agenda(html_content: str) -> List[Record]:  
    soup = BeautifulSoup(html_content, "html.parser")  
    records = []  
  
    # Find all <a> elements in the tree structure  
    for a_tag in soup.find_all("a", class_="tree-item"):  
        href = a_tag.get("href")  
        name = make_legal_file_name(a_tag.get_text(strip=True))
        records.append(Record(href=href, name=name))  
  
    return records  
  
  
# Request content from each Record's href and save it to a folder  
def request_content_and_save(records: List[Record], dist_folder_path: str) -> None:  
    if not os.path.exists(dist_folder_path):  
        os.makedirs(dist_folder_path)  
  
    for record in tqdm(records, desc="Processing Records", unit="record"):
        try:  
            response = requests.get(record.href)
            response.raise_for_status()  
            content = BeautifulSoup(response.text, "html.parser").find("div", class_="content").text
  
            # Save content to a file named after the record's name  
            file_path = os.path.join(dist_folder_path, f"{record.name}.txt")  
            with open(file_path, "w", encoding="utf-8") as file:  
                file.write(content)  
              
            record.source_content = content  
        except Exception as e:  
            print(f"Failed to fetch or save content for {record.href}: {e}")  
  

# Compare the original and new HTML content  
def compare(original_folder_path: str, temp_folder_path: str) -> Union[List, None]:  
    changed_records = []  
    assistant = AzureOpenAIChatAssistant()

    # Compare files in both folders  
    for file_name in os.listdir(original_folder_path):  
        original_file = os.path.join(original_folder_path, file_name)  
        temp_file = os.path.join(temp_folder_path, file_name)

        if os.path.exists(temp_file):  
            with open(original_file, "r", encoding="utf-8") as orig_file, open(temp_file, "r", encoding="utf-8") as temp_file:  
                original_content = orig_file.read()  
                temp_content = temp_file.read()  
  
                if original_content != temp_content:
                    response = assistant.generate_completion(new_content=temp_content, ori_content=original_content)
                    changed_records.append(response)
                    push_to_queue(response, "REPLACE_WITH_YOUR_QUEUE_NAME")

    # print("len of changes: " + str(len(changed_records)))

    if len(changed_records) == 0: return None
    return changed_records


# Upload the changes to an Azure queue  
def push_to_queue(record: str, queue_name: str) -> None: 
    
    # Connect to Azure Queue  
    load_dotenv()
    queue_client = QueueClient.from_connection_string(  
        conn_str = os.getenv("CONN_STR"),  
        queue_name = queue_name  
    )  

    try:
        # Serialize Record as a message  
        message = f"{record}"  
        queue_client.send_message(message)  

    except Exception as e:  
        print(f"Failed to upload messages to Azure queue: {e}")  

    