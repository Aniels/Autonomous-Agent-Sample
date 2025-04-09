import os  
import re  
from typing import List, Optional  

import requests  
from tqdm import tqdm  
from dotenv import load_dotenv  
from bs4 import BeautifulSoup  
from azure.storage.queue import QueueClient

from autonomous.record import Record
from autonomous.azure_openAI_chat_assistant import AzureOpenAIChatAssistant


class AgendaProcessor:  
    def __init__(self, original_folder_path: str, temp_folder_path: str):  
        """  
        Initializes the AgendaProcessor with necessary paths and Azure Queue configurations.  
        """  
        load_dotenv()  
        self.original_folder_path = original_folder_path  
        self.temp_folder_path = temp_folder_path  
 
        # Initialize Azure Queue Client  
        try:  
            conn_str = os.getenv("CONN_STR")  
            queue_name = os.getenv("QUEUE_NAME")  
            if not conn_str or not queue_name:  
                raise ValueError("Missing Azure configuration in environment variables.")
            self.queue_client = QueueClient.from_connection_string(  
                conn_str=conn_str,  
                queue_name=queue_name  
            )
        except Exception as e:  
            raise  ConnectionError(f"Failed to connect to Azure Queue: {e}")  

        # Initialize Azure OpenAI Assistant and persistent HTTP session
        self.assistant = AzureOpenAIChatAssistant()  
        self.session = requests.Session()  

        # Ensure temp_folder_path and original_folder_path exists  
        try:
            if not os.path.exists(self.original_folder_path): os.makedirs(self.original_folder_path)  
            if not os.path.exists(self.temp_folder_path): os.makedirs(self.temp_folder_path)  
        except OSError as e:  
            print(f"Error: Failed to create directory {self.temp_folder_path}: {e}")  

    @staticmethod  
    def make_legal_file_name(name: str) -> str:  
        return re.sub(r'[<>:"/\\|?*\n]', '_', name)  

    def get_records_from_agenda(self, agenda_path: str) -> List[Record]:  
        """  
        Parses the HTML agenda content and extracts records.  
        """  
        records = []
        with open(agenda_path, mode="r") as f:  
            html_content = f.read()  
            soup = BeautifulSoup(html_content, "html.parser")  

        for a_tag in soup.find_all("a", class_="tree-item"):  
            href = a_tag.get("href")  
            if href:  
                name = self.make_legal_file_name(a_tag.get_text(strip=True))  
                records.append(Record(href=href, name=name))  
            else:  
                print("Warning: Found <a> tag without href attribute.")  

        print(f"Extracted {len(records)} records from agenda.")  
        return records  

    def request_content_and_save(self, records: List[Record], dist_folder_path: str) -> None:  
        """  
            Fetches content for each record and saves it to the folder.  
        """  
        for record in tqdm(records, desc="Processing Records", unit="record"):
            try:  
                response = self.session.get(record.href, timeout=10)  
                response.raise_for_status() 
                content_div = BeautifulSoup(response.text, "html.parser").find("div", class_="content").text
    
                # Save content to a file named after the record's name  
                file_path = os.path.join(dist_folder_path, f"{record.name}.txt")  
                with open(file_path, "w", encoding="utf-8") as file:  
                    file.write(content_div)  

            except Exception as e:  
                print(f"Failed to fetch or save content for {record.href}: {e}")

    def compare_files_and_push_changes(self) -> Optional[List[str]]:  
        """  
        Compares original and temp files, generates change records, and pushes them to the Azure Queue.  
        """  
        changed_records = 0 
        assistant = self.assistant  
        original_files = os.listdir(self.original_folder_path)  

        for file_name in tqdm(original_files, desc="Comparing Files", unit="file"):  
            original_file = os.path.join(self.original_folder_path, file_name)  
            temp_file = os.path.join(self.temp_folder_path, file_name)  

            if not os.path.exists(temp_file):  
                print(f"Warning: Temp file does not exist for {file_name}. Skipping comparison.")  
                continue  

            try:  
                with open(original_file, "r", encoding="utf-8") as orig_f, open(temp_file, "r", encoding="utf-8") as temp_f:  
                    original_content = orig_f.read()  
                    temp_content = temp_f.read()  

                if original_content != temp_content:  
                    response = assistant.generate_completion(new_content=temp_content, ori_content=original_content)  
                    changed_records += 1  
                    self.push_to_queue(response)  

            except IOError as e:  
                print(f"Error: Reading files for {file_name}: {e}")  

        print(f"Detected {changed_records} changed records.")  
        return changed_records  

    def push_to_queue(self, response: str) -> None:  
        try:
            # Serialize Record as a message  
            message = f"{response}"
            self.queue_client.send_message(message) 
        except Exception as e:  
            print(f"Error: Failed to push message to Azure Queue: {e}")
