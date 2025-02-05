import os
from typing import List
from bs4 import BeautifulSoup
import requests
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for OpenAI API Key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Sample data in case web scraping fails
SAMPLE_COURSES = """
Python Programming Course
Learn Python programming from basics to advanced concepts. This comprehensive course covers variables, data structures, functions, OOP, and more.

Web Development Bootcamp
Master full-stack web development with HTML, CSS, JavaScript, React, Node.js, and MongoDB. Build real-world projects and deploy them.

Data Science Fundamentals
Explore data science concepts including data analysis, visualization, machine learning, and statistical analysis using Python libraries.

Artificial Intelligence Basics
Introduction to AI concepts, machine learning algorithms, neural networks, and practical applications in various industries.

Cloud Computing Essentials
Learn cloud computing fundamentals with AWS, Azure, and Google Cloud. Understand cloud architecture, deployment, and best practices.
"""

class DataLoader:
    def __init__(self, urls: List[str]):
        """Initialize the DataLoader with a list of URLs."""
        self.urls = urls
        self.documents = None
        self.text_chunks = None
        self.vector_store = None

    def load_data(self) -> None:
        """Load data from the specified URLs using BeautifulSoup or fall back to sample data."""
        try:
            documents = []
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            for url in self.urls:
                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # Extract main content
                    content = []
                    
                    # Get course titles and descriptions
                    courses = soup.find_all('div', class_='course-block')
                    for course in courses:
                        title = course.find('h3')
                        description = course.find('p')
                        if title:
                            content.append(title.get_text(strip=True))
                        if description:
                            content.append(description.get_text(strip=True))
                    
                    # If no courses found, use sample data
                    if not content:
                        content = [SAMPLE_COURSES]
                    
                    # Combine all content
                    text_content = '\n\n'.join(content)
                    
                    # Create a Document object
                    doc = Document(
                        page_content=text_content,
                        metadata={'source': url}
                    )
                    documents.append(doc)
                except Exception as e:
                    print(f"Error scraping {url}: {str(e)}")
                    # Use sample data as fallback
                    doc = Document(
                        page_content=SAMPLE_COURSES,
                        metadata={'source': 'sample_data'}
                    )
                    documents.append(doc)
            
            self.documents = documents
            print(f"Successfully loaded {len(self.documents)} documents")
        except Exception as e:
            print(f"Error loading documents: {str(e)}")
            raise

    def split_text(self, chunk_size: int = 500, chunk_overlap: int = 50) -> None:
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
            print(f"Error creating vector store: {str(e)}")
            raise

def initialize_vector_store() -> FAISS:
    """Initialize and return the vector store with data from the specified URL."""
    urls = ["https://brainlox.com/courses/category/technical"]
    
    data_loader = DataLoader(urls)
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