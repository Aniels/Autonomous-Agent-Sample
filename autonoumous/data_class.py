import json
from typing import Union  
from dataclasses import dataclass, asdict

# Define the Record class  
@dataclass  
class Record:  
    href: str  
    name: str  
    
    # Method to convert the Record instance to JSON  
    def to_json(self, indent: int = 4) -> str:  
        # Convert the dataclass to a dictionary and then to a JSON string
        return json.dumps(asdict(self), indent=indent)

