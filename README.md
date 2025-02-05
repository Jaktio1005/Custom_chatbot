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

4. Create a `.env` file in the project root and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. The server will run on `http://localhost:5000` with the following endpoints:

### Chat Endpoint

- **URL**: `/chat`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
```json
{
    "question": "Your question here"
}
```
- **Success Response**:
```json
{
    "answer": "The answer to your question",
    "source_documents": [
        {
            "content": "Relevant content from source",
            "source": "Source URL"
        }
    ]
}
```

### Health Check Endpoint

- **URL**: `/health`
- **Method**: `GET`
- **Success Response**:
```json
{
    "status": "healthy"
}
```

## Example Usage with curl

```bash
# Health check
curl http://localhost:5000/health

# Ask a question
curl -X POST http://localhost:5000/chat \
    -H "Content-Type: application/json" \
    -d '{"question": "What technical courses are available?"}'
```

## Project Structure

- `app.py`: Flask application and API endpoints
- `data_loader.py`: Data extraction and processing functionality
- `requirements.txt`: Project dependencies
- `.env`: Environment variables (not tracked in git)

## Error Handling

The API includes comprehensive error handling for:
- Missing or invalid input
- API key configuration issues
- Data loading and processing errors
- Vector store initialization failures

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository. 