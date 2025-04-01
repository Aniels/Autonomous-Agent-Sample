import os 
from dotenv import load_dotenv  
from openai import AzureOpenAI  
  
  
class AzureOpenAIChatAssistant:  
    def __init__(self):  
        # Load environment variables from the .env file  
        load_dotenv()  
  
        # Initialize Azure OpenAI configuration  
        self.endpoint = os.getenv("ENDPOINT_URL")  
        self.deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o-mini")  
        self.subscription_key = os.getenv("AZURE_OPENAI_API_KEY")  
          
        # Initialize Azure OpenAI client  
        self.client = AzureOpenAI(  
            azure_endpoint=self.endpoint,  
            api_key=self.subscription_key,  
            api_version="2024-03-01-preview",  
        )  
  
    def generate_completion(self, ori_content:str, new_content:str, max_tokens=800, top_p=0.95,  
                            frequency_penalty=0, presence_penalty=0, stop=None, stream=False):  
        """  
        Generate a response using Azure OpenAI's chat completion.  
  
        Args:  
            chat_prompt (list): A list of dictionaries containing the chat prompt.  
            max_tokens (int): The maximum number of tokens to generate.  
            temperature (float): Sampling temperature.  
            top_p (float): Nucleus sampling probability.  
            frequency_penalty (float): Penalize repeated tokens.  
            presence_penalty (float): Penalize new topic introduction.  
            stop (str or None): A stop sequence for the output.  
            stream (bool): Whether to stream the response.  
  
        Returns:  
            dict: The response from Azure OpenAI.  
        """  

        chat_prompt = [  
        {  
            "role": "system",  
            "content": [  
                {  
                    "type": "text",  
                    "text": 
                        "Read the record then compare the different between source_content and new_content in detail. \
                        Give the level of change with one of the level of 'LOW', 'MEDIUM','HIGH'.  \
                        Here is the sample keys in the json output['document name', 'level of change', 'summary of different']."  
                }  
            ]  
        },  
        {  
            "role": "user",  
            "content": [  
                {  
                    "type": "text",  
                    "text": "this is the original content: " + ori_content
                },
                {  
                    "type": "text",  
                    "text": "this is the new content: " + new_content
                }  
            ]  
        }  
    ] 
        try:  
            # Generate the completion  
            completion = self.client.chat.completions.create(  
                model=self.deployment,  
                messages=chat_prompt,  
                max_tokens=max_tokens,  
                temperature=0,  
                top_p=top_p,  
                frequency_penalty=frequency_penalty,  
                presence_penalty=presence_penalty,  
                stop=stop,  
                stream=stream,
                response_format={ "type": "json_object" }, 
            )  
            print("Input tokens: " + str(completion.usage.prompt_tokens) + ", Output tokens: " + str(completion.usage.completion_tokens))
            return completion.choices[0].message.content
        except Exception as e:  
            return {"error": str(e)}  
  
  
# Example usage  
if __name__ == "__main__":  
    # Initialize the assistant  
    assistant = AzureOpenAIChatAssistant()  

    with open("data/original/All.txt", mode="r") as f:
        ori_content = f.read()

    with open("temp/original/All.txt", mode="r") as f:
        new_content = f.read()

    
    response = assistant.generate_completion(new_content, ori_content)
