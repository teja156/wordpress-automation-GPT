import dotenv
import os
import random
import openai
import requests
from io import BytesIO
from PIL import Image
import db_actions

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4-turbo"


CATEGORIES = os.getenv("CATEGORIES").split(",")

PROMPT_IDEAS_V1 = """
Generate 5 unique and highly engaging blog post ideas related to {category}

Avoid repeating these topics: {existing_topics}.

Each idea should be:
- Relevant for 2024 and beyond
- Easy to write without requiring real-time news updates
- Useful for programmers, cybersecurity experts, computer geeks, or DevOps professionals
- Search engine optimized (SEO-friendly)
- Response should contain only ascii readable characters, no other special characters are allowed
- Category names are case-sensitive and should be an exact match

Return the response as a JSON object formatted like this:
{{
  "category": "{category}",
  "ideas": [
    "Blog Idea 1",
    "Blog Idea 2",
    "Blog Idea 3",
    ...
  ]
}}
"""

PROMPT_CONTENT_V1 = """
Write a structured blog post on the topic: {topic}

## Format:
- Use **Markdown** for headings and formatting.
- Title: `# Blog Post Title`
- Headings: `## Heading`
- Subheadings: `### Subheading`
- Include code snippets inside triple backticks (` ``` `) for syntax highlighting.
- Use bullet points for lists.
- End with a conclusion.
- Make sure the response only contains ascii readable text, no other characters allowed.

## Return Format:
Return the response as a JSON object with the following structure:
```json
## Return Format:
    Return the response as a JSON object with the following structure:
    {{
      "Title": "{topic}",
      "Content": "Full blog post in Markdown format"
    }}
"""

PROMPT_THUMBNAIL_V1 = """
Generate an AI-generated image representing the topic: '{topic}'.
    The image should be visually appealing and relevant to the subject. Don't try to insert text into the image. The image should be 1280x720 pixels in size. Return the image as a base64 encoded string.
"""


def send_prompt(prompt):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    print (f"Sending prompt to {MODEL}: {prompt}")
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(e)
        return None


def generate_topics():
  for category in CATEGORIES:
      # get all existing topics
      existing_topics = db_actions.get_all_topics()
      # concat all topics into a string separated by commas
      existing_topics = ', '.join([topic[2] for topic in existing_topics])
      ideas = send_prompt(PROMPT_IDEAS_V1.format(category=category, existing_topics=existing_topics))
      print(ideas)
      # ideas is a json object, convert it to a python object
      ideas = eval(ideas)

      # Add the ideas to the database
      category = ideas['category']
      for idea in ideas['ideas']:
          db_actions.add_topic(category, idea)


def generate_content(topic_id, category, topic):
    # Generate content for the topic
    content = send_prompt(PROMPT_CONTENT_V1.format(topic=topic))
    print(f"Content generated for topic {topic}: {content}")
    # content is a json object, convert it to a python object
    content = eval(content)
    return content


def generate_thumbnail(topic):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    # Generate a thumbnail for the topic
    response = client.images.generate(
        model="dall-e-3",
        prompt=PROMPT_THUMBNAIL_V1.format(topic=topic),
        n=1,
        size="1792x1024"
    )
    image_url = response.data[0].url
    return image_url