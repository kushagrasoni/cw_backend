import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai = OpenAI(api_key=os.environ.get("OPENAI_WORK_API_KEY"))


def get_output(prompt):
    completion = openai.chat.completions.create(  # Change the method name
        model='gpt-3.5-turbo',
        messages=[  # Change the prompt parameter to messages parameter
            {'role': 'user', 'content': prompt}
        ],
        temperature=0.9
    )

    output = completion.choices[0].message.content

    return output
