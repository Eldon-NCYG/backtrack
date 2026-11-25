# Runbook: set up Spotify API access

Needed once before the phase 1 sync can run, then again every 6 months.

`make auth` and `make sync` are phase 1 deliverables (weeks 1 and 2). Steps 1 to 3 can be done before they exist.

## First time

1. Check the account has Spotify Premium. Development mode apps stop working without it.
2. Go to developer.spotify.com/dashboard and create an app. The name doesn't matter. Tick **Web API**. Set the redirect URI to `http://127.0.0.1:8888/callback`. Spotify rejects `localhost`.
3. Copy `.env.example` to `.env`. Paste the app's client ID and client secret into `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`.
4. Run `make auth`. It opens Spotify's consent page asking for one permission, `user-read-recently-played`. Approve it. Paste the refresh token it gives you into `SPOTIFY_REFRESH_TOKEN` in `.env`.
5. Run `make sync`. Check that the printed row count is up to 50 and the date range ends today.

## Every 6 months

The refresh token expires 6 months after step 4, and using it doesn't extend it. Set a calendar reminder for 5 months.

1. Run `make auth` again and replace `SPOTIFY_REFRESH_TOKEN` in `.env`.
2. Run `make sync` and check the date range.

If the hourly sync starts failing with `invalid_grant`, the token has expired or been revoked. Re-authorise the same day: every hour it's down risks plays falling out of the 50-play window.

## Rules

- Never commit `.env`. It's gitignored.
- Never paste the client secret or refresh token into an issue, a commit message, a log or a chat.
- If the client secret leaks, reset it from the app's settings on the dashboard, then repeat steps 3 to 5.
