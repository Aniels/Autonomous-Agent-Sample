from autonoumous.tool import get_record_from_agenda, request_content_and_save, compare  
  
PROJECT = "partner_conter"
  
def partner_conter(INIT_PROJECT=False):  
    # Read the HTML content from the agenda file  
    with open("data/agenda.html", mode="r") as f:  
        html_content = f.read()  
  
    # Step 1: Extract records from the HTML agenda  
    agenda_records = get_record_from_agenda(html_content)  
  
    if INIT_PROJECT:  
        # Step 2-1: Save original content  
        request_content_and_save(agenda_records, dist_folder_path="data/original")  
    else:  
        # Step 2-2: Save temp content  
        request_content_and_save(agenda_records, dist_folder_path="data/temp")
        
        # Step 3: Compare the original and temporary content in data folder, then push to the queue
        changes = compare("data/original", "data/temp")  
        print(f"Changes detected: {changes}")  
  
  
if __name__ == "__main__":  
    if PROJECT == "partner_conter":  
        partner_conter(INIT_PROJECT=False)
    else:  
        print("No valid project selected.")  