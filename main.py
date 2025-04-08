from autonomous.agendaProcesser import AgendaProcessor

PROJECT = "partner_conter"
AGENDA_PATH = "data/agenda.html"
ORIGINAL_FOLDER= "data/original"
TEMP_FOLDER= "data/temp"
  
def partner_center(INIT_PROJECT=False):  
    agenda_processer = AgendaProcessor(
    original_folder_path = ORIGINAL_FOLDER,
    temp_folder_path = TEMP_FOLDER
    )

    agenda_records = agenda_processer.get_records_from_agenda(agenda_path=AGENDA_PATH)

    if INIT_PROJECT:
        # Step 2-1: Save original content
        agenda_processer.request_content_and_save(records=agenda_records, dist_folder_path=ORIGINAL_FOLDER)
    else:  
        # Step 2-2: Save temp content
        agenda_processer.request_content_and_save(records=agenda_records, dist_folder_path=TEMP_FOLDER)
        
        # Step 3: Compare the original and temporary content in data folder, then push to the queue
        agenda_processer.compare_files_and_push_changes()
  
  
if __name__ == "__main__":  
    if PROJECT == "partner_conter":  
        partner_center(INIT_PROJECT=True) # need to do it with False in second times to compare different
    else:  
        print("No valid project selected.")
