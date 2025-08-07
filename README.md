# 🏢 GlitchPunchAI - Cynical AI Shitposter on Twitter

[![Twitter Bot](https://img.shields.io/badge/Twitter-@GlitchPunchAI-1DA1F2?logo=twitter)](https://twitter.com/GlitchPunchAI)
[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-FFD21F.svg)](https://huggingface.co/spaces/KennyOry/GlitchPunchAI)

An AI bot that generates absurd tech humor tweets in the style of a "cynical troll." Uses Zephyr-7B model to create tweets with dark humor and unexpected tech memes.

## 🔥 Features
- Automated tweet generation every 2-4 hours
- Custom prompt engineering with tech metaphors
- Automatic content filtering
- Health-check endpoint for monitoring
- Retry logic for Twitter API failures
- Docker container support
- FULL FREE (free base twitter api + free space in HF)

## 🚀 Deployment on Hugging Face Spaces

1. **Fork the repository**:  
   [https://huggingface.co/spaces/KennyOry/GlitchPunchAI](https://huggingface.co/spaces/KennyOry/GlitchPunchAI)

2. **Add secrets** in Space settings:
   ```env
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
   BEARER_TOKEN=your_bearer_token
   ```

3. **Configure resources** (minimum requirements):
   Free space hardware
   - CPU basic
   - 2 VCPU
   - 16 GB
   - FREE

4. **Launch the Space** - bot activates automatically

> **Note**: Initial model download may take 1-2 minutes on first launch

## 💻 Local Installation

### Requirements
- Python 3.9+
- Docker (optional)
- Twitter Developer Account

### Steps:
1. Clone repository:
   ```bash
   git clone https://github.com/cloverfield11/GlitchPunchAI.git
   cd GlitchPunchAI
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file with Twitter credentials:
   ```env
   TWITTER_API_KEY=your_key
   TWITTER_API_SECRET=your_secret
   TWITTER_ACCESS_TOKEN=your_token
   TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
   BEARER_TOKEN=your_bearer_token
   ```

4. Run with Python:
   ```bash
   python app.py
   ```

### Using Docker:
```bash
docker build -t glitchpunch .
docker run -d --name glitch_bot \
  --env-file .env \
  -p 7860:7860 \
  glitchpunch
```

## ⚙️ Configuration
Key parameters in `app.py`:
```python
MODEL_REPO = "KennyOry/GlitchPunchAI"
MODEL_FILE = "zephyr-7b-beta.Q5_K_M.gguf"
N_CTX = 2048
INTERVAL_HOURS = (2.0, 4.0)
```

## 📂 Project Structure
```
├── app.py             - Main bot script
├── Dockerfile         - Docker configuration
├── requirements.txt   - Python dependencies
├── README.md          - This file
└── .env.example       - Environment template
```

## ⚠️ Limitations & Notes
- Requires significant CPU/RAM resources
- Tweet generation may take 20-30 seconds
- Content generation uses uncensored humor - review prompts carefully

## 📜 License
Apache 2.0 - [LICENSE](https://github.com/cloverfield11/GlitchPunchAI/blob/main/LICENSE)

> **Disclaimer**: Bot generates provocative humor. Maintainer not responsible for content violating platform policies.