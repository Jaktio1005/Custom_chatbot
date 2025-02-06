# Custom Chatbot with Langchain and Flask

A production-ready chatbot that uses Langchain to extract and process data from [Brainlox's technical courses](https://brainlox.com/courses/category/technical), creating a knowledge base for answering user questions through a Flask API.

## Features

- Data extraction from web pages using Langchain's URL loaders
- Text processing and chunking for optimal information retrieval
- Vector embeddings using OpenAI's embedding model
- FAISS vector store for efficient similarity search
- RESTful API endpoint for chat interactions
- Comprehensive error handling and logging
- Health check endpoint

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Jaktio1005/Custom-Chatbot.git
cd Custom-Chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment:
```bash
cp .env.example .env
```
Then edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```
⚠️ **IMPORTANT**: Never commit your actual API key to git! The `.env` file is ignored by git for security.

## Project Structure

- `app.py`: Flask application and API endpoints
- `data_loader.py`: Data extraction and processing functionality
- `requirements.txt`: Project dependencies
- `.env.example`: Template for environment variables
- `.env`: Environment variables (not tracked in git)






