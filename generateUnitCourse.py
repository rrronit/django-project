import os
import openai
import json
import re


openai.api_key='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'

response = openai.ChatCompletion.create(
          temperature = .5,
          model="gpt-3.5-turbo",
          messages=[
            {"role": "system", "content": "You are AI"},
            {"role": "user", "content": "this is test"}
          ]
        )

res = response['choices'][0]['message']['content'].replace('\'', '"')
        
        
print(res)