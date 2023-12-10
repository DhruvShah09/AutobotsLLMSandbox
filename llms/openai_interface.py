import requests 
import re 
from robots.globals import ai_spec_config

class AISpecInterface:  
    def __init__(self, custom_base_url = None, use_openai = False, openai_api_key = None, custom_headers = None, use_globals=True):
        if use_globals:
            custom_base_url = ai_spec_config["custom_base_url"]
            use_openai = ai_spec_config["use_openai"]
            self.openai_api_key = ai_spec_config["openai_api_key"]
            openai_api_key = self.openai_api_key
            custom_headers = ai_spec_config["custom_headers"]

        if custom_base_url is None and not use_openai: 
            raise Exception("Must specify either a custom base url or use openai")
        elif custom_base_url is not None and use_openai:
            raise Exception("Cannot use both custom base url and openai")
        elif custom_base_url is not None and not use_openai:
            self.base_url = custom_base_url 
            self.use_openai = False
        else:
            self.base_url = "https://api.openai.com"
            self.use_openai = True
            if self.openai_api_key is None:
                raise Exception("Must specify openai api key when using openai endpoints")
            self.openai_api_key = openai_api_key
        if custom_headers:
            #expecting a dictionary of headers
            self.custom_headers = custom_headers
        else:
            self.custom_headers = {
                "Content-Type": "application/json",
                "Authorization" : f"Bearer {self.openai_api_key}"
            }        
        self.custom_url_base = custom_base_url
        self.use_openai = use_openai
        
    #create a text completion based on the prompt
    def create_completion(self, prompt, stop, temperature, engine, max_tokens, is_completion=True):
        completion_headers = self.custom_headers
        if not isinstance(prompt, str):
            raise Exception("please follow openai completion format for prompt [error: prompt must be a string]")
        if is_completion: 
            url =  self.base_url + "/v1/completions"
            payload = { 
                "model": engine,
                "prompt": prompt,
                "max_tokens": max_tokens, 
                "stop": stop
            }
        else: 
            url = self.base_url + "/v1/chat/completions"
            if not isinstance(prompt, list):
                raise Exception("please follow openai chat completions format for prompt [prompt must be a list of dictionary of messages]")
            payload = {
                "model": engine,
                "messages": prompt,
                "max_tokens": max_tokens, 
                "stop": stop
            }  
        response = requests.post(url, headers=completion_headers, json=payload).json()
        print(response)
        pattern = r"```" + "python" + r"\n(.*?)```"
        if is_completion: 
            matches = re.findall(pattern, response["choices"][0]["text"], re.DOTALL)
            try:
                return matches[0] if matches else response["choices"][0]["text"]
            except Exception as e:
                print("error parsing response, the following should give you more hints about the error:")
                print(e)
        else:
            matches = re.findall(pattern, response["choices"][0]["message"]["content"], re.DOTALL)
            try:
                return matches[0] if matches else response["choices"][0]["message"]["content"]
            except Exception as e:
                print("error parsing response, the following should give you more hints about the error:")
                print(e)
        return "Error Generating Completion. See logs for details."

    def create_chat_completion_prompt(self, msg_list, role_list):
        if not isinstance(msg_list, list):
            raise Exception("msg_list must be a list")
        if not isinstance(role_list, list):
            raise Exception("role_list must be a list")
        if len(msg_list) != len(role_list):
            raise Exception("please follow openai chat completions format for prompt [msg_list and role_list must be the same length]")
        if role_list.countOf("system") > 1: 
            raise Exception("please follow openai chat completions format for prompt [role_list must have at most one system prompt]")
        prompt = []
        for i in range(len(msg_list)):
            prompt.append({
                "role": role_list[i],
                "content" : {
                    "type" : "text",
                    "text" : msg_list[i]
                }
            })
        return prompt
        