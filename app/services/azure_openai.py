import os
from openai import AzureOpenAI

from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_VERSION"),
)

# Constants
OPENAI_MODEL = "cgi_openai_gpt_35_turbo"
OPENAI_MAX_TOKENS = 800
OPENAI_TEMPERATURE = 0.8
OPENAI_N = 1
OPENAI_TOP_P = 0.95
OPENAI_STOP = None


def get_output(prompt):
    message_text = [{"role": "system",
                     "content": prompt
                     }]

    completion = client.chat.completions.create(
        model=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        messages=message_text,
        temperature=OPENAI_TEMPERATURE,
        max_tokens=OPENAI_MAX_TOKENS,
        top_p=OPENAI_TOP_P,
        n=OPENAI_N,
        frequency_penalty=0,
        presence_penalty=0,
        stop=OPENAI_STOP
    )

    output = completion.choices[0].message.content

    return output
