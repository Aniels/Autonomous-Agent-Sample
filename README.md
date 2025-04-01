# Autonomous Agent Sample
  
## Overview  
  
The Partner Counter Project is designed to extract records from an HTML agenda, fetch content from the records' links, and compare original content with updated content. The differences are then processed and uploaded to an Azure Storage Queue for further handling.  
  
## Setup
 
1. Clone the repository:
```bash  
gh repo clone Aniels/Autonomous-Agent-Sample
```

2. You can install the required packages using pip:  
  
```bash
pip install -r requirements.txt  
```

3. Environment Variables:
Create a .env file in the root directory and define the following variables:

> CONN_STR=<your_azure_queue_connection_string>  
> ENDPOINT_URL=<your_azure_openai_endpoint_url>  
> DEPLOYMENT_NAME=<your_azure_openai_deployment_name>  
> AZURE_OPENAI_API_KEY=<your_azure_openai_api_key>  

4. Data Directory:
- Ensure you have a data directory with agenda.html file structured appropriately.

## Usage
 
- To run the project, execute the following command:

```
python main.py
```

The script will perform the following steps:  
  
1. Read the HTML content from `data/agenda.html`.  
2. Extract records from the HTML agenda.  
3. Depending on the `INIT_PROJECT` flag:  
   - If `INIT_PROJECT=True`, it saves the original content to `data/original`.  
   - Otherwise, it saves the temporary content to `data/temp`.  
4. Compare the original and temporary content in their respective folders and print detected changes.  
5. Upload the changes to the specified Azure Storage Queue.  

## Features  
  
- **HTML Parsing**: Extracts records from an HTML agenda file.  
- **Content Retrieval**: Fetches content from each record's URL.  
- **Content Comparison**: Compares original content with new content to detect changes.  
- **Azure Integration**: Uploads detected changes to an Azure Storage Queue.  
- **Progress Tracking**: Uses `tqdm` for progress indication during content processing.  
  
## Requirements  
  
- Python 3.11.9
- Required Python packages:  
  - `beautifulsoup4`  
  - `requests`  
  - `tqdm`  
  - `python-dotenv`  
  - `azure-storage-queue`  
  - `openai`  

## Contributing
- Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
- This project is licensed under the MIT License. See the LICENSE file for details.
