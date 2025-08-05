# SmartSupportBot

A smart hospital-style AI chatbot built using **RASA**, **Twilio WhatsApp**, **Docker**, and **Python**. It handles appointment booking, symptom checking, doctor info lookup, and human handover — all via WhatsApp!

---

## Features

- 🩺 Book appointments
- 🤒 Symptom checker
- 🧑‍⚕️ Doctor info via mock API
- 🙋 Human handover
- 🗂️ CSV + SQLite logging
- 📦 Dockerized setup
- 📱 WhatsApp via Twilio
- 🔐 .env credentials support

---

## Tech Stack

- RASA (NLU & Core)
- Twilio (WhatsApp)
- Docker & Compose
- Python (Custom Actions)
- SQLite & Pandas
- ngrok for tunneling

---

## How to Run Locally

1. **Clone the repo**
   ```bash
   git clone https://github.com/Tenyjose/SmartSupportBot.git
   cd SmartSupportBot
   ```

2. **Create `.env` file**
   ```
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_PHONE_NUMBER=whatsapp:+14155238886
   ```

3. **Start Docker**
   ```bash
   docker compose up --build
   ```

4. **Start ngrok**
   ```bash
   ngrok http 5005
   ```

5. **Set Twilio Webhook**
   - Use the ngrok URL: `https://<your-ngrok-url>/webhooks/twilio/webhook`

6. **Send "hi" from WhatsApp** 

---

## Folder Structure

```
SmartSupportBot/
├── actions/
├── data/
├── domain.yml
├── credentials.yml
├── config.yml
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Author

**Teny Jose**  
MSc Data Analytics | AI Projects | Python & RASA Dev  



