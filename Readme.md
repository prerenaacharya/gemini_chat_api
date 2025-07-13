Gemini Chatroom Backend - FastAPI

This is a Gemini-style chatroom backend service built with FastAPI, integrated with Google Gemini API, Stripe for subscriptions, Redis Queue (RQ) for background tasks, and JWT-based authentication. It is designed to support real-time chatrooms with scalable message generation and subscription control.

📁 Project Setup and Run Instructions

✅ Prerequisites

Python 3.10+

Redis Server (local or cloud)

Stripe account (test keys)

Google Gemini API key

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

Installation

# Clone the repo
https://github.com/prerenaacharya/gemini_chat_api
cd <project-directory>

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Redis server (if not already)
redis-server or if using windows use docker

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 for deploying on railway
uvicorn app.main:app --reload to run in local system and use 
localhost:8000/docs to check the endpoints from swagger ui

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

API ENDPOINTS

POST /auth/signup
Registers a new user using a mobile number,user name,password. No authentication is required.

POST /auth/send-otp
Sends an OTP to the mobile number provided. This is mocked in development and the OTP is returned in the response.

POST /auth/verify-otp
Verifies the OTP entered by the user and returns a JWT token for the session.

POST /auth/forgot-password
Sends a new OTP for password reset purposes. This is unauthenticated.

POST /auth/change-password
Allows a logged-in user to change their password. Requires a valid JWT token.

👤 User APIs

GET /user/me
Returns the current authenticated user’s profile details using the JWT token.

💬 Chatroom APIs

POST /chatroom
Creates a new chatroom tied to the authenticated user.

GET /chatroom
Returns a list of all chatrooms created by the user. This list is cached in Redis for 5–10 minutes to reduce DB load.

GET /chatroom/{id}
Retrieves full information about a specific chatroom belonging to the user.

POST /chatroom/{id}/message
Sends a message to the chatroom. The response from Gemini is generated asynchronously using Redis Queue.

💳 Subscription and Payments APIs

POST /payments/subscribe/pro
Initiates a Stripe Checkout session for upgrading to a Pro subscription. Returns a checkout URL.

POST /payments/webhook/stripe
Stripe sends event notifications (e.g., payment completed) to this endpoint. It updates the user’s subscription type. This is an unauthenticated route but signature-verified.

GET /payments/subscription/status
Returns the current user’s subscription level: Basic or Pro. Requires a valid JWT token.

