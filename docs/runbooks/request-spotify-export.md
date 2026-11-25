# Runbook: request the Spotify export

1. In a web browser (not the app), go to spotify.com/account/privacy and log in.
2. Under **Download your data**, tick **Extended streaming history**. The other options can stay unticked.
3. Click **Request data**, then confirm using the link in the email Spotify sends.
4. Wait for the second email. Spotify says up to 30 days; it's usually a few days. The download link expires, so download it soon.
5. Unzip it and copy the `Streaming_History_Audio_*.json` files into `data/export/`.
6. Run `make all`. Check that the printed date range starts when you expect.

**Before switching on the phase 2 sync,** request a fresh export and reload it, so there's no gap between the export and the API.

Never commit these files. `data/` is gitignored.
