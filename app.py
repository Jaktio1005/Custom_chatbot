from flask import Flask, request, jsonify, render_template
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from data_loader import initialize_vector_store, validate_api_key
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# System prompt for the chatbot
SYSTEM_TEMPLATE = """You are a helpful course assistant for Brainlox's technical courses. When answering questions:

1. For course listings:
   - List relevant courses with their titles
   - Include price per session
   - Mention the number of lessons
   - Add a brief description

2. For specific course inquiries:
   - Provide detailed course information
   - Explain why the course is valuable
   - Mention target audience and prerequisites
   - Include duration and schedule flexibility
   - List key learning outcomes
   - Mention the price and value proposition

3. For comparison questions:
   - Compare courses objectively
   - Highlight unique features of each
   - Suggest the most suitable option based on user's needs

4. For pricing questions:
   - State the price per session clearly
   - Explain what's included
   - Mention any available packages or discounts

Always be enthusiastic and encouraging while maintaining professionalism. If you don't have specific information, be honest and provide the information you do have.

Context: {context}
Question: {question}
"""

# Initialize components with better error handling
try:
    # Validate API key first
    validate_api_key()
    
    # Initialize the vector store
    vector_store = initialize_vector_store()
    
    # Create prompt templates
    system_message_prompt = SystemMessagePromptTemplate.from_template(SYSTEM_TEMPLATE)
    human_template = "{question}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    chat_prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        human_message_prompt,
    ])
    
    # Initialize the language model
    llm = ChatOpenAI(
        temperature=0.7,
        model_name="gpt-3.5-turbo"
    )
    
    # Initialize conversation memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key='answer'
    )
    
    # Create the conversational chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(
            search_kwargs={
                "k": 5,  # Increase number of relevant documents
                "fetch_k": 10  # Fetch more documents for better context
            }
        ),
        memory=memory,
        return_source_documents=True,
        return_generated_question=True,
        combine_docs_chain_kwargs={
            "prompt": chat_prompt
        }
    )
    
    initialization_error = None
except ValueError as ve:
    # Handle API key and initialization errors
    initialization_error = str(ve)
    print(f"Initialization error: {initialization_error}")
except Exception as e:
    initialization_error = f"An unexpected error occurred during initialization: {str(e)}"
    print(f"Unexpected error: {initialization_error}")

@app.route('/')
def index():
    """Serve the chat interface."""
    return render_template('index.html', initialization_error=initialization_error)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests."""
    # Check if system is properly initialized
    if initialization_error:
        return jsonify({
            'error': initialization_error
        }), 503

    try:
        # Validate input
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Missing required field: question'
            }), 400

        question = data['question']

        # Get response from QA chain
        response = qa_chain({
            "question": question
        })

        # Extract chat history for context
        chat_history = []
        if memory.chat_memory.messages:
            for i in range(0, len(memory.chat_memory.messages), 2):
                if i + 1 < len(memory.chat_memory.messages):
                    chat_history.append({
                        'question': memory.chat_memory.messages[i].content,
                        'answer': memory.chat_memory.messages[i + 1].content
                    })

        # Extract source documents
        source_docs = [
            {
                'content': doc.page_content,
                'source': doc.metadata.get('source', 'Unknown'),
                'title': doc.metadata.get('title', 'Unknown')
            }
            for doc in response.get('source_documents', [])
        ]

        # Format the response
        formatted_response = {
            'answer': response['answer'],
            'source_documents': source_docs,
            'chat_history': chat_history,
            'context': {
                'generated_question': response.get('generated_question', question),
                'sources_used': len(source_docs)
            }
        }

        return jsonify(formatted_response)

    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    status = 'healthy' if not initialization_error else 'unhealthy'
    response = {'status': status}
    if initialization_error:
        response['error'] = initialization_error
    return jsonify(response), 200 if status == 'healthy' else 503

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5002, debug=False) 