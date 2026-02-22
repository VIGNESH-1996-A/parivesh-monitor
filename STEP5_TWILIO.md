# Step 5: Where to find your Twilio values

Your **.env** file is already created with your phone number. You only need to add the three Twilio values.

---

## 1. Open Twilio Console

Go to: **https://console.twilio.com**  
Log in with the account you created using 9940944929.

---

## 2. Account SID and Auth Token

On the **main dashboard** (home page after login) you will see:

| Label | What to copy |
|-------|----------------|
| **Account SID** | A string that starts with **`AC`** (e.g. `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`) |
| **Auth Token** | Click **Show** next to it, then copy the token |

**Note:** The ID you mentioned (`US0663c98a68ac0277beefa5a21a6cbd56`) starts with **US** — that is not the Account SID. Use the one that starts with **AC** on the dashboard.

- Paste **Account SID** into `.env` as: `TWILIO_ACCOUNT_SID=ACxxxxxxxx...`
- Paste **Auth Token** into `.env` as: `TWILIO_AUTH_TOKEN=your_token_here`

---

## 3. Twilio “From” phone number

To send SMS, Twilio needs a number that **sends** the message (your 9940944929 is the number that **receives** it).

- In the left menu click **Phone Numbers** → **Manage** → **Active numbers**.
- If you see a number there (trial or bought), copy it in full, e.g. **+15551234567**.
- If you have **no number yet**: click **Buy a number**, choose a number (trial accounts often get one free in supported countries). Copy that number.

In `.env` set (with the `+` sign):

```env
TWILIO_FROM_NUMBER=+15551234567
```

Use your actual Twilio number instead of `+15551234567`.

---

## 4. Edit the .env file

1. In Cursor (or Notepad), open **v:\PARIVESH\.env**.
2. Replace the empty values as below (no quotes, no spaces around `=`):

```env
PHONE_NUMBER=919940944929
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=paste_your_auth_token_here
TWILIO_FROM_NUMBER=+15551234567
```

3. Save the file.

---

## 5. Test

In terminal (in `v:\PARIVESH`):

```powershell
python parivesh_monitor.py
```

If Twilio is set correctly, when there is a new update you’ll get an SMS on 9940944929. If you see **“SMS skipped”**, check that all three Twilio values in `.env` are correct and saved.
