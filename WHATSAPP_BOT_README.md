# RSI WhatsApp Bot - Otoño 2026

WhatsApp chatbot assistant for the "Responsabilidad Social en la Industria" course (Fall 2026).

## Features

- ✅ **WhatsApp Business API Integration** - Handles incoming messages and sends responses
- ✅ **AI-Powered Responses** - Optional OpenAI integration for intelligent conversations
- ✅ **Fallback Logic** - Smart keyword-based responses when AI is not available
- ✅ **Robust Error Handling** - Comprehensive logging and error management
- ✅ **Environment Configuration** - Secure credential management via environment variables
- ✅ **Health Monitoring** - Built-in health check endpoint
- ✅ **Message Status Tracking** - Marks messages as read automatically

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the environment template and fill in your credentials:

```bash
cp .env.whatsapp .env
```

Edit `.env` with your actual values:

```env
PHONE_NUMBER_ID=your_phone_number_id
WABA_ID=your_waba_id
WHATSAPP_TOKEN=your_permanent_token
VERIFY_TOKEN=rsi_otono_2026
OPENAI_API_KEY=your_openai_key  # Optional
```

### 3. Run the Application

**Development:**
```bash
python app.py
```

**Production (with Gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Configuration

### Required Environment Variables

| Variable | Description | Where to Find |
|----------|-------------|---------------|
| `PHONE_NUMBER_ID` | Your WhatsApp phone number ID | Meta Developer Dashboard → WhatsApp → API Setup |
| `WABA_ID` | WhatsApp Business Account ID | Meta Developer Dashboard → WhatsApp → Settings |
| `WHATSAPP_TOKEN` | Permanent access token | Meta Developer Dashboard → WhatsApp → API Setup |
| `VERIFY_TOKEN` | Webhook verification token | You choose this (must match Meta webhook config) |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI responses | None (uses fallback logic) |
| `FLASK_ENV` | Flask environment | `development` |
| `PORT` | Server port | `5000` |

## Webhook Setup

1. **Deploy your application** to a public server (e.g., Railway, Render, Heroku)

2. **Configure Meta webhook**:
   - Go to Meta Developer Dashboard → Your App → WhatsApp → Configuration
   - Callback URL: `https://your-domain.com/webhook`
   - Verify Token: Your `VERIFY_TOKEN` value
   - Webhook Fields: Select `messages`

3. **Test the webhook**:
   ```bash
   curl "http://localhost:5000/webhook?hub.mode=subscribe&hub.verify_token=rsi_otono_2026&hub.challenge=test123"
   # Should return: test123
   ```

## API Endpoints

### `GET /`
Home endpoint with service information.

**Response:**
```json
{
  "service": "RSI WhatsApp Bot - Otoño 2026",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "webhook": "/webhook (GET, POST)",
    "health": "/health (GET)"
  }
}
```

### `GET /webhook`
Webhook verification endpoint (used by Meta).

**Query Parameters:**
- `hub.mode` - Should be "subscribe"
- `hub.verify_token` - Your verify token
- `hub.challenge` - Challenge string to return

### `POST /webhook`
Receives incoming WhatsApp messages.

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "configuration": {
    "phone_number_id_set": true,
    "waba_id_set": true,
    "token_set": true,
    "verify_token_set": true,
    "openai_key_set": false
  }
}
```

## AI Assistant Behavior

The bot responds as a teaching assistant for the RSI course with expertise in:
- Circular economy (economía circular)
- Industrial sustainability (sostenibilidad industrial)
- Corporate Social Responsibility (RSC)

**Response style:**
- Warm, professional, and direct
- Maximum 3 lines per response
- Asks for name and student ID when discussing assignments

### Example Interactions

**User:** "¿Qué es economía circular?"  
**Bot:** "♻️ La economía circular busca minimizar residuos y maximizar el valor de los recursos. ¿Qué aspecto te interesa profundizar?"

**User:** "Tengo dudas sobre la tarea"  
**Bot:** "📚 Para consultas sobre tareas, por favor proporciona tu nombre completo y matrícula. ¿En qué tarea necesitas ayuda?"

## Architecture

```
app.py
├── WhatsAppClient
│   ├── send_message()
│   └── mark_as_read()
├── AIAssistant
│   ├── generate_response()
│   └── _fallback_response()
└── Flask Routes
    ├── GET  /
    ├── GET  /health
    ├── GET  /webhook (verify)
    └── POST /webhook (receive messages)
```

## Error Handling

The application includes comprehensive error handling:
- Network timeouts (10s for WhatsApp API, 30s for OpenAI)
- Invalid message formats
- Missing configuration
- API failures with graceful fallbacks
- Detailed logging for debugging

## Logging

Logs are written to stdout with the following format:
```
2026-09-06 11:42:00 - __main__ - INFO - Processing message from 1234567890: ¿Qué es RSC?
```

Log levels:
- `INFO` - Normal operations
- `WARNING` - Configuration issues
- `ERROR` - Operation failures
- `CRITICAL` - System failures

## Security Considerations

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Use HTTPS in production** - Required by Meta
3. **Verify webhook signatures** - Consider adding signature verification
4. **Rate limiting** - Implement rate limiting for production
5. **Token rotation** - Regularly rotate your access tokens

## Deployment

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Render

1. Create a new Web Service
2. Connect your Git repository
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
5. Add environment variables in dashboard

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV PORT=5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Troubleshooting

### Webhook not receiving messages
- Check Meta webhook configuration
- Verify HTTPS is enabled (required by Meta)
- Check firewall/network settings
- Review application logs

### AI responses not working
- Verify `OPENAI_API_KEY` is set correctly
- Check OpenAI account has credits
- Fallback responses should still work

### Health check fails
- Review missing configuration items
- Check environment variables are loaded
- Ensure `.env` file exists and is readable

## Development

### Testing Locally with ngrok

```bash
# Start ngrok
ngrok http 5000

# Use the ngrok URL in Meta webhook configuration
# Example: https://abc123.ngrok.io/webhook
```

### Running Tests

```bash
# Test webhook verification
curl "http://localhost:5000/webhook?hub.mode=subscribe&hub.verify_token=rsi_otono_2026&hub.challenge=test123"

# Test health endpoint
curl http://localhost:5000/health

# Test home endpoint
curl http://localhost:5000/
```

## Contributing

Improvements welcome! Focus areas:
- Message persistence/database integration
- Student data management
- Assignment tracking
- Analytics and reporting
- Multi-language support

## License

MIT License - See LICENSE file for details

## Support

For course-related questions, contact the RSI professor.  
For technical issues, check the logs or create an issue in the repository.
