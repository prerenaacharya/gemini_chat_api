# Gemini Chat API

A scalable, multi-user chat backend with OTP login, Stripe subscription, Redis-based queues, and Gemini 2.0 streaming integration. Built using **FastAPI**, it supports chatrooms, background task handling, and real-time AI responses.

---

## 🔧 Setup Instructions

Configure Runtime Environment

Create a `.env` file in the root of your project and define the following variables:

```env
DATABASE_URL=your_postgres_or_mysql_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
GEMINI_API_KEY=your_gemini_api_key
STRIPE_PRO_PRICE_ID=your_stripe_price_id


### 2. Download Requirement
  pip install -r requirements.txt

### 3. Run Application
  uvicorn main:app --reload 

⚙️  Queue System Explanation
Two Redis-based queues are used for efficient task handling:

1. Chatroom List Caching
Applied to GET /chatroom

Chatroom data is cached in Redis to reduce database load and improve response speed.

2. Message Processing Queue
Used in POST /chatroom/{id}/message

Messages are pushed into a queue and processed asynchronously to support multiple chatrooms concurrently.


🤖 Gemini API Integration
This app uses Google Gemini 2.0 Flash with streaming (stream=True) to provide real-time AI responses:

The Gemini API is integrated into the message queue processor.

Token-by-token streaming gives an instant typing feel.

Background processing avoids blocking the main server thread.

🧠 Design Decisions & Inspiration
OTP-based Auth inspired by common apps like WhatsApp and Swiggy for frictionless login.

Redis-backed Queues enable background task execution, improving scalability.

Stripe handles subscription-based access (Free vs. Pro).

Streaming Gemini ensures fast and interactive AI responses in chat.