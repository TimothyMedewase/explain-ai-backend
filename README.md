# Explain AI Backend

A FastAPI-based Retrieval Augmented Generation (RAG) system that processes document uploads and answers questions about them using LLMs.

## Features

- Document upload and text extraction
- RAG using LangChain and OpenAI GPT-4
- Conversation history for multi-turn interactions
- Content-specific formatting (math, letters, general content)
- API for frontend integration

## Deployment to Railway.app

### Step 1: Create a Railway account

Sign up at [Railway.app](https://railway.app) if you don't already have an account.

### Step 2: Connect your GitHub repository

1. Push this project to your GitHub account
2. In Railway dashboard, choose "New Project"
3. Select "Deploy from GitHub repo"
4. Find and select this repository

### Step 3: Configure environment variables

In the Railway dashboard, add these environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `FRONTEND_URL`: The URL of your frontend application (e.g., your Vercel deployment URL)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins (e.g., https://yourdomain.com,https://www.yourdomain.com)
- `MAX_CONVERSATIONS`: (Optional) Maximum number of conversations to store in memory (default: 100)
- `CONVERSATION_EXPIRY`: (Optional) Conversation expiry time in seconds (default: 3600)

### Step 4: Deploy

Railway will automatically deploy your application when you push changes to your repository.

## Local Development

1. Clone the repository
2. Create and activate a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your environment variables
   ```
   OPENAI_API_KEY=your-api-key-here
   ```
5. Run the application
   ```
   uvicorn app.main:app --reload
   ```

## API Usage

### POST /process

Upload files and get AI-generated answers about their content.

**Request:**

- Method: POST
- Content-Type: multipart/form-data
- Parameters:
  - `files`: One or more files (max 5)
  - `query`: Your question about the documents
  - `conversation_id`: (Optional) ID for continuing a conversation

**Response:**

```json
{
  "response": "AI-generated answer",
  "conversation_id": "unique-conversation-id",
  "content_type": "general|math|letter"
}
```

## Frontend Integration

See the [Frontend Repository](https://github.com/yourusername/explain-ai-frontend) for how to connect your UI to this API.
