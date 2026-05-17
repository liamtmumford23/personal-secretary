# Personal Secretary

A CLI agent that manages Gmail and Google Calendar using Claude as the brain.

## Setup

1. **Create a Google Cloud project**
   - Go to https://console.cloud.google.com and create a new project.
   - Enable the **Gmail API** and **Google Calendar API**.
   - Under *APIs & Services → Credentials*, create an **OAuth 2.0 Client ID** (Desktop app).
   - Download the JSON file and save it as `credentials.json` in this directory.

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your Anthropic API key**
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```

4. **Run**
   ```bash
   python main.py
   ```
   The first run opens a browser for Google OAuth. The token is cached in `token.json` so subsequent runs skip that step.

## Usage examples

```
> Show my last 5 emails from my boss
> Do I have anything scheduled this Friday?
> Schedule a dentist appointment on May 10 from 9am to 10am
> Send Alice an email saying I'll be late to the meeting
```

Claude confirms before sending emails or creating events.