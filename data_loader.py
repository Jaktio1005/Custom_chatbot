import os
from typing import List, Dict
from bs4 import BeautifulSoup
import requests
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import time
import re

# Load environment variables
load_dotenv()

def validate_api_key():
    """Validate OpenAI API key and provide clear instructions if missing."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "\n\nOpenAI API key is not properly configured!"
            "\n1. Create an account at https://platform.openai.com/signup"
            "\n2. Get your API key at https://platform.openai.com/account/api-keys"
            "\n3. Add your API key to the .env file:"
            "\n   OPENAI_API_KEY=your-actual-api-key-here"
            "\n\nNever commit your actual API key to git!"
        )
    return api_key

# Validate API key on module load
validate_api_key()

class DataLoader:
    def __init__(self, base_url: str):
        """Initialize the DataLoader with the base URL."""
        self.base_url = base_url
        self.documents = None
        self.text_chunks = None
        self.vector_store = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_course_links(self) -> List[str]:
        """Extract links to individual course pages from the main page."""
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            course_links = []
            # Find all course cards
            course_cards = soup.find_all('div', class_='card')
            
            for card in course_cards:
                # Find the View Details link
                view_details = card.find('a', string='View Details')
                if view_details and 'href' in view_details.attrs:
                    course_url = view_details['href']
                    if not course_url.startswith('http'):
                        course_url = f"https://brainlox.com{course_url}"
                    course_links.append(course_url)
            
            print(f"Found {len(course_links)} course links")
            return course_links
        except Exception as e:
            print(f"Error getting course links: {str(e)}")
            return []

    def scrape_course_page(self, url: str) -> Dict[str, str]:
        """Scrape detailed information from a course page."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            course_data = {
                'title': '',
                'description': '',
                'curriculum': '',
                'requirements': '',
                'outcomes': '',
                'url': url
            }
            
            # Extract course title and description from the card
            card = soup.find('div', class_='card')
            if card:
                # Get title
                title = card.find('h3')
                if title:
                    course_data['title'] = title.get_text(strip=True)
                
                # Get description
                description = card.find('p')
                if description:
                    course_data['description'] = description.get_text(strip=True)
                
                # Get lessons count
                lessons = card.find('div', class_='lessons')
                if lessons:
                    course_data['curriculum'] = f"Total Lessons: {lessons.get_text(strip=True)}"
            
            return course_data
        except Exception as e:
            print(f"Error scraping course page {url}: {str(e)}")
            return None

    def load_data(self) -> None:
        """Load data from the main page and individual course pages."""
        try:
            documents = []
            
            # Get the main page content
            print(f"Fetching content from {self.base_url}")
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            
            print(f"Response status code: {response.status_code}")
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Try different selectors to find course information
            course_titles = soup.find_all('h3')
            print(f"Found {len(course_titles)} course titles")
            
            for title in course_titles:
                try:
                    title_text = title.get_text(strip=True)
                    if not title_text or title_text in ['Explore', 'Resources', 'Address']:
                        continue
                        
                    print(f"Processing course: {title_text}")
                    
                    # Get the parent container
                    parent = title.parent
                    if not parent:
                        continue
                    
                    # Find description - it's usually text or a paragraph after the title
                    description = ""
                    next_elem = title.find_next_sibling()
                    if next_elem and next_elem.name == 'p':
                        description = next_elem.get_text(strip=True)
                    elif title.next_sibling:
                        description = title.next_sibling.strip()
                    
                    # Find lessons count - usually near the title
                    lessons_text = ""
                    lessons_elem = parent.find(text=lambda t: t and 'Lessons' in t)
                    if lessons_elem:
                        lessons_text = lessons_elem.strip()
                        # Extract just the number
                        if match := re.search(r'(\d+)\s*Lessons', lessons_text):
                            num_lessons = match.group(1)
                            duration_weeks = (int(num_lessons) + 1) // 2  # Assuming 2 lessons per week
                            lessons_text = f"{lessons_text} (Approximately {duration_weeks} weeks)"
                    
                    # Find price - usually contains "per session"
                    price_text = ""
                    price_elem = parent.find(text=lambda t: t and 'per session' in t.lower())
                    if price_elem:
                        price_text = price_elem.strip()
                        
                    # Extract additional details
                    details = {
                        'target_audience': 'This course is suitable for ' + ('kids' if 'kids' in title_text.lower() or 'young' in title_text.lower() else 'all skill levels'),
                        'prerequisites': 'No prior experience needed' if 'beginner' in title_text.lower() or 'introduction' in title_text.lower() else 'Basic programming knowledge recommended',
                        'schedule': 'Flexible scheduling available',
                        'format': 'Interactive online sessions with hands-on projects and exercises'
                    }
                    
                    # Create content with enhanced structure
                    content = [
                        f"Course: {title_text}",
                        f"Description: {description}",
                        f"Duration: {lessons_text}",
                        f"Price: {price_text}",
                        f"Target Audience: {details['target_audience']}",
                        f"Prerequisites: {details['prerequisites']}",
                        f"Schedule: {details['schedule']}",
                        f"Format: {details['format']}"
                    ]
                    
                    # Add topic tags
                    topics = []
                    if any(keyword in title_text.lower() for keyword in ['python', 'java', 'javascript', 'web', 'ai', 'scratch', 'robotics']):
                        if 'python' in title_text.lower():
                            topics.append('Python Programming')
                        if 'java' in title_text.lower():
                            topics.append('Java Development')
                        if 'javascript' in title_text.lower() or 'js' in title_text.lower():
                            topics.append('JavaScript')
                        if 'web' in title_text.lower():
                            topics.append('Web Development')
                        if 'ai' in title_text.lower() or 'artificial intelligence' in title_text.lower():
                            topics.append('Artificial Intelligence')
                        if 'scratch' in title_text.lower():
                            topics.append('Scratch Programming')
                        if 'robotics' in title_text.lower():
                            topics.append('Robotics')
                    
                    if topics:
                        content.append(f"Topics: {', '.join(topics)}")
                    
                    # Create a Document object with enhanced metadata
                    doc = Document(
                        page_content='\n\n'.join(filter(None, content)),
                        metadata={
                            'source': self.base_url,
                            'title': title_text,
                            'topics': topics,
                            'lessons': lessons_text,
                            'price': price_text,
                            'target_audience': details['target_audience']
                        }
                    )
                    documents.append(doc)
                    print(f"Added document for: {title_text}")
                
                except Exception as e:
                    print(f"Error processing course title '{title_text if 'title_text' in locals() else 'unknown'}': {str(e)}")
            
            self.documents = documents
            print(f"Successfully loaded {len(self.documents)} course documents")
            
            if not self.documents:
                raise ValueError("No courses found on the page. Please check the website structure.")
                
        except Exception as e:
            print(f"Error loading documents: {str(e)}")
            raise

    def split_text(self, chunk_size: int = 1000, chunk_overlap: int = 100) -> None:
        """Split the loaded documents into chunks."""
        if not self.documents:
            raise ValueError("No documents loaded. Call load_data() first.")

        text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )

        self.text_chunks = text_splitter.split_documents(self.documents)
        print(f"Created {len(self.text_chunks)} text chunks")

    def create_vector_store(self) -> FAISS:
        """Create and return a FAISS vector store from the text chunks."""
        if not self.text_chunks:
            raise ValueError("No text chunks available. Call split_text() first.")

        try:
            embeddings = OpenAIEmbeddings()
            self.vector_store = FAISS.from_documents(
                documents=self.text_chunks,
                embedding=embeddings
            )
            print("Vector store created successfully")
            return self.vector_store
        except Exception as e:
            if "invalid_api_key" in str(e):
                raise ValueError(
                    "\n\nInvalid OpenAI API key! Please check your .env file and ensure you've added a valid API key."
                    "\nGet your API key at: https://platform.openai.com/account/api-keys"
                ) from e
            print(f"Error creating vector store: {str(e)}")
            raise

def initialize_vector_store() -> FAISS:
    """Initialize and return the vector store with data from Brainlox."""
    base_url = "https://brainlox.com/courses/category/technical"
    
    data_loader = DataLoader(base_url)
    data_loader.load_data()
    data_loader.split_text()
    vector_store = data_loader.create_vector_store()
    
    return vector_store

if __name__ == "__main__":
    # Test the data loading and vector store creation
    try:
        vector_store = initialize_vector_store()
        print("Vector store initialization successful")
    except Exception as e:
        print(f"Error initializing vector store: {str(e)}") 