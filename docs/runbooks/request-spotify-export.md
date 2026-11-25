# Runbook: request the Spotify export

The export is a phase 2 input. Phase 1 doesn't need it.

**When to ask:** after the hourly sync has started, and a week or two before phase 2 begins. An export requested after the sync started overlaps the API data, so it fills any gaps the laptop sync left.

1. In a web browser (not the app), go to spotify.com/account/privacy and log in.
2. Under **Download your data**, tick **Extended streaming history**. The other options can stay unticked.
3. Click **Request data**, then confirm using the link in the email Spotify sends.
4. Wait for the second email. Spotify says up to 30 days; it's usually a few days. The download link expires, so download it soon.
5. Unzip it and copy the `Streaming_History_Audio_*.json` files into `data/export/`.
6. Run the export loader (phase 2, week 6). Check that the printed date range starts when you expect and ends after the first sync.

Never commit these files. `data/` is gitignored.
