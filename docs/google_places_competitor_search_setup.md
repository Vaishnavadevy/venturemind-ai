# Google Places competitor search setup

VentureMind uses **Places API (New) Text Search** on the backend to retrieve public Google Places listings for a founder's business category and location. The key never reaches the browser.

## One-time Google Cloud configuration

1. Open the Google Cloud Console and select the project used for VentureMind.
2. Attach an active billing account. Google Places requests are billable, so configure a small budget alert before testing.
3. Open **APIs & Services > Library** and enable **Places API (New)**.
4. Open **APIs & Services > Credentials** and create a new API key.
5. Restrict the key to **Places API (New)**. Do not use the same browser-exposed key for this backend service.
6. Add the key to `backend/.env` only:

```env
GOOGLE_PLACES_API_KEY=replace_with_your_server_key
```

7. Restart the FastAPI server.

## Test procedure

1. Sign in to VentureMind and open **Workspace**.
2. Save a Founder Profile with a business category, country, and city or district.
3. In **Nearby competitor analysis**, click **Analyse nearby competitors**.
4. Confirm that result cards show a name, address, public rating (when available), and Google Maps link.

If direct results do not load, the **Open Google Maps** link remains available as a no-key fallback. No competitor names or ratings are fabricated by VentureMind.

## Data and usage note

Google Places data is subject to Google Maps Platform terms and availability. VentureMind stores no provider key in the frontend and requests only the fields required for the competitor cards.
