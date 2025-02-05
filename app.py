from flask import Flask, request, jsonify, render_template
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from data_loader import initialize_vector_store
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API Key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set")

app = Flask(__name__)

# Initialize the vector store
try:
    vector_store = initialize_vector_store()
    # Initialize the language model
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    # Create the QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )
except Exception as e:
    print(f"Error during initialization: {str(e)}")
    raise

@app.route('/')
def index():
    """Serve the chat interface."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests."""
    try:
        # Validate input
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Missing required field: question'
            }), 400

        question = data['question']

        # Get response from QA chain
        response = qa_chain({"query": question})

        # Extract source documents
        source_docs = [
            {
                'content': doc.page_content,
                'source': doc.metadata.get('source', 'Unknown')
            }
            for doc in response.get('source_documents', [])
        ]

        return jsonify({
            'answer': response['result'],
            'source_documents': source_docs
        })

    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5002, debug=False) 