# API Key Setup Guide

This guide explains how to obtain the required API keys for BeatLyrics.

## Required Keys

### OpenAI API Key (Required)
1. Visit https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and add to `.env` as `OPENAI_API_KEY`
5. **Cost**: Pay-per-use, approximately $0.01-0.05 per lyric generation

### YouTube Data API Key (Optional)
1. Go to https://console.developers.google.com/
2. Create a new project or select existing
3. Enable "YouTube Data API v3"
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy the key and add to `.env` as `YOUTUBE_API_KEY`
6. **Quota**: 10,000 units/day (free tier)

## Optional Keys

### Spotify API (Metadata Only)
1. Visit https://developer.spotify.com/dashboard
2. Create an app
3. Copy Client ID and Client Secret
4. Add to `.env` as `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`

### Stripe (For Billing)
1. Visit https://dashboard.stripe.com/apikeys
2. Copy publishable and secret keys
3. Add to `.env` as `STRIPE_PUBLISHABLE_KEY` and `STRIPE_SECRET_KEY`

### Auth0 (For Authentication)
1. Visit https://auth0.com/
2. Create an application
3. Copy domain, client ID, and client secret
4. Add to `.env` as `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`, `AUTH0_CLIENT_SECRET`

## Testing Without Keys

You can run the application in limited mode:
- Without YouTube API: URL processing will be disabled
- Without Spotify API: Spotify metadata will be unavailable
- Without Stripe: Billing features will be disabled
- Without Auth0: Authentication will use mock/development mode

The core audio upload and processing functionality only requires the OpenAI API key.
