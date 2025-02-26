import requests
import db_actions
import ai_generate
import dotenv
import os
import markdown
import sys
import urllib.parse

dotenv.load_dotenv()

WORDPRESS_DOMAIN = os.getenv("WORDPRESS_DOMAIN")
WORDPRESS_USERNAME = os.getenv("WORDPRESS_USERNAME")
WORDPRESS_APPLICATION_PASSWORD = os.getenv("WORDPRESS_APPLICATION_PASSWORD")
CATEGORIES = os.getenv("CATEGORIES").split(",")



POST_URL = f"https://{WORDPRESS_DOMAIN}/wp-json/wp/v2/posts"
MEDIA_UPLOAD_URL = f"https://{WORDPRESS_DOMAIN}/wp-json/wp/v2/media"

# Configure basic auth
WORDPRESS_AUTH = (WORDPRESS_USERNAME, WORDPRESS_APPLICATION_PASSWORD)

def get_unpublished_topic():
    # Check if there are any unpublished topics
    while 1:
        topic_data = db_actions.get_unpublished_topic()
        if topic_data is None:
            print("No unpublished topics found, generating now...")
            # Generate topics
            # ai_generate.generate_topics()
            generated = ai_generate.generate_topics()
            if generated:
                continue
            else:
                print("Unable to generate topics. Exiting...")
                sys.exit(1)
        else:
            return topic_data

def convert_to_html(markdown_content):
    return markdown.markdown(markdown_content, extensions=['fenced_code'])

def create_categories(category):
    data = {
        'name': category,
        'slug': category.lower(),
        'description': f'Category for {category} posts'
    }
    # Check if the category already exists
    response = requests.get(f"https://{WORDPRESS_DOMAIN}/wp-json/wp/v2/categories?name={category.lower()}", auth=WORDPRESS_AUTH)
    if response.status_code == 200 and len(response.json()) > 0:
        print(f"Category {category} already exists.")
        return
    response = requests.post(f"https://{WORDPRESS_DOMAIN}/wp-json/wp/v2/categories", json=data, auth=WORDPRESS_AUTH)
    if response.status_code == 201:
        print(f"Category {category} created successfully.")
    else:
        print(f"Failed to create category {category}. Status code: {response.status_code}")
        print(response.json())
        sys.exit()

def create_post():
    topic_id, category, topic = get_unpublished_topic()
    print("Generating content for topic:", topic)
    # Generate content for the topic
    content = ai_generate.generate_content(topic_id, category, topic)
    if content is None:
        print("Failed to generate content for the topic")
        return
    
    title = content['Title']
    post_content = content['Content']

    # Convert the content to HTML
    post_content = convert_to_html(post_content)

    # Generate a thumbnail for the topic
    thumbnail_url = ai_generate.generate_thumbnail(topic)

    # Create a directory called thumbnails if it doesn't exist
    if not os.path.exists('thumbnails'):
        os.mkdir('thumbnails')
    
    # Download the thumbnail
    thumbnail = requests.get(thumbnail_url).content
    # Save the thumbnail to a file
    with open(f'thumbnails/{topic_id}.jpg', 'wb') as file:
        file.write(thumbnail)

    # Upload the thumbnail to WordPress
    thumbnail_data = {
        'file': open(f'thumbnails/{topic_id}.jpg', 'rb')
    }
    thumbnail_response = requests.post(MEDIA_UPLOAD_URL, files=thumbnail_data, auth=WORDPRESS_AUTH)
    # Check if the thumbnail was uploaded successfully
    if thumbnail_response.status_code != 201:
        print(f"Failed to upload thumbnail: {thumbnail_response.text}")
        return
    
    thumbnail_id = thumbnail_response.json()['id']

    print(f"Thumbnail {thumbnail_id} uploaded successfully.")


    # Create category if it doesn't exist
    create_categories(category)


    # Get the category ID
    category_response = requests.get(f"https://{WORDPRESS_DOMAIN}/wp-json/wp/v2/categories?name={category.lower()}", auth=WORDPRESS_AUTH)
    category_id = category_response.json()[0]['id']

    # Create the post
    print("Creating post...")
    post_data = {
        'title': title,
        'content': post_content,
        'status': 'publish',
        'categories': [category_id],
        'featured_media': thumbnail_id
    }
    post_response = requests.post(POST_URL, json=post_data, auth=WORDPRESS_AUTH)

    # Check if the post was created successfully
    if post_response.status_code == 201:
        print(f"Post created successfully: {post_response.json()['link']}")
        # Set the topic as published
        db_actions.set_topic_published(topic_id)
    else:
        print(f"Failed to create post: {post_response.text}")
    
    # Delete the thumbnail
    os.remove(f'thumbnails/{topic_id}.jpg')
    print("Thumbnail deleted.")

if __name__ == '__main__':
    # Initialize the database
    db_actions.db_init()
    # Create a post
    create_post()