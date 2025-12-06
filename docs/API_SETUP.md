# API Setup Guide

Step-by-step instructions for setting up API credentials for LinkedIn and Instagram.

---

## 🔐 LinkedIn API Setup

### Step 1: Create LinkedIn App

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Click **"Create app"**
3. Fill in app details:
   - **App name:** BandaWeb3 Automation
   - **LinkedIn Page:** Your company/personal page
   - **App logo:** Upload BandaWeb3 logo
   - **Legal agreement:** Check the box
4. Click **"Create app"**

### Step 2: Get Client Credentials

1. In your app dashboard, go to **"Auth"** tab
2. Copy **Client ID** and **Client Secret**
3. Add to `.env` file:
   ```bash
   LINKEDIN_CLIENT_ID=your_client_id_here
   LINKEDIN_CLIENT_SECRET=your_client_secret_here
   ```

### Step 3: Configure OAuth Settings

1. In **"Auth"** tab, scroll to **"OAuth 2.0 settings"**
2. Add **Redirect URL:**
   ```
   http://localhost:8000/callback
   ```
3. Click **"Update"**

### Step 4: Request API Access

1. Go to **"Products"** tab
2. Request access to:
   - ✅ **Share on LinkedIn** (required)
   - ✅ **Sign In with LinkedIn** (required)
   - ⚠️ **Marketing Developer Platform** (optional, for analytics)

3. Wait for approval (usually instant for Share on LinkedIn)

### Step 5: Generate Access Token

**Option A: Using OAuth Flow (Recommended)**

1. Create a simple OAuth flow:
   ```python
   # Run this script to get access token
   python3 scripts/linkedin_oauth.py
   ```

2. Follow the prompts:
   - Opens browser to LinkedIn authorization
   - Grant permissions
   - Copy access token from terminal

3. Add to `.env`:
   ```bash
   LINKEDIN_ACCESS_TOKEN=your_access_token_here
   ```

**Option B: Manual OAuth (Advanced)**

1. Build authorization URL:
   ```
   https://www.linkedin.com/oauth/v2/authorization?
   response_type=code&
   client_id=YOUR_CLIENT_ID&
   redirect_uri=http://localhost:8000/callback&
   scope=w_member_social
   ```

2. Visit URL in browser, authorize app
3. Copy `code` from redirect URL
4. Exchange code for access token:
   ```bash
   curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
     -d grant_type=authorization_code \
     -d code=YOUR_CODE \
     -d client_id=YOUR_CLIENT_ID \
     -d client_secret=YOUR_CLIENT_SECRET \
     -d redirect_uri=http://localhost:8000/callback
   ```

### Step 6: Test Connection

```bash
python3 scripts/publish_linkedin.py --test-connection
```

Expected output:
```
✓ Connected to LinkedIn API
User ID: urn:li:person:XXXXXXXX
```

---

## 📸 Instagram Graph API Setup

### Prerequisites

- ✅ Instagram Business or Creator account
- ✅ Facebook Page connected to Instagram account
- ✅ Facebook Developer account

### Step 1: Convert to Business Account

1. Open Instagram app
2. Go to **Settings → Account**
3. Tap **Switch to Professional Account**
4. Choose **Business** or **Creator**
5. Complete setup

### Step 2: Connect to Facebook Page

1. In Instagram settings, go to **Account → Linked accounts**
2. Select **Facebook**
3. Log in and connect to your Facebook Page
4. If you don't have a page, create one first

### Step 3: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **"My Apps" → "Create App"**
3. Choose **"Business"** as app type
4. Fill in details:
   - **App name:** BandaWeb3 Automation
   - **Contact email:** Your email
5. Click **"Create App"**

### Step 4: Add Instagram Product

1. In app dashboard, find **"Instagram"** product
2. Click **"Set Up"**
3. Follow the setup wizard

### Step 5: Get Access Token

**Option A: Using Graph API Explorer (Quick Test)**

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from dropdown
3. Click **"Generate Access Token"**
4. Grant permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
5. Copy **Access Token**

⚠️ **Note:** This token expires in 1-2 hours. For production, use long-lived token.

**Option B: Generate Long-Lived Token (Production)**

1. Get short-lived token from Graph API Explorer (above)

2. Exchange for long-lived token:
   ```bash
   curl -i -X GET "https://graph.facebook.com/v18.0/oauth/access_token?
     grant_type=fb_exchange_token&
     client_id=YOUR_APP_ID&
     client_secret=YOUR_APP_SECRET&
     fb_exchange_token=SHORT_LIVED_TOKEN"
   ```

3. Response will contain `access_token` (valid for 60 days)

4. Add to `.env`:
   ```bash
   INSTAGRAM_ACCESS_TOKEN=your_long_lived_token_here
   FACEBOOK_APP_ID=your_app_id_here
   FACEBOOK_APP_SECRET=your_app_secret_here
   ```

### Step 6: Get Instagram Business Account ID

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Use your access token
3. Make request:
   ```
   GET /me/accounts
   ```
4. Find your Facebook Page ID
5. Make another request:
   ```
   GET /{page_id}?fields=instagram_business_account
   ```
6. Copy `instagram_business_account.id`
7. Add to `.env`:
   ```bash
   INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id_here
   ```

### Step 7: Test Connection

```bash
python3 scripts/publish_instagram.py --test-connection
```

Expected output:
```
✓ Connected to Instagram API
Account: @bandaweb3
Name: BandaWeb3
```

---

## 🔄 Token Refresh

### LinkedIn Tokens

LinkedIn access tokens expire after **60 days**.

**To refresh:**
1. Re-run OAuth flow (Step 5 above)
2. Update `.env` with new token
3. Test connection

**Automation (Optional):**
- Set up token refresh script
- Run monthly via cron

### Instagram Tokens

Instagram access tokens expire after **60 days**.

**To refresh:**
1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Generate new token
3. Exchange for long-lived token
4. Update `.env`

**Automation (Optional):**
- Use refresh token endpoint
- Set up monthly cron job

---

## 🔒 Security Best Practices

### 1. Never Commit Credentials

```bash
# Ensure .env is in .gitignore
echo "config/.env" >> .gitignore

# Verify
git status  # .env should not appear
```

### 2. Use Environment Variables

```bash
# Never hardcode credentials
# ❌ Bad
api_key = "sk-1234567890"

# ✅ Good
api_key = os.getenv("API_KEY")
```

### 3. Rotate Tokens Regularly

- LinkedIn: Every 60 days (automatic expiration)
- Instagram: Every 60 days (automatic expiration)
- Set calendar reminders

### 4. Limit Permissions

- Only request necessary scopes
- LinkedIn: `w_member_social` (minimum)
- Instagram: `instagram_basic`, `instagram_content_publish`

### 5. Monitor API Usage

- Check LinkedIn/Facebook developer dashboards
- Set up usage alerts
- Stay within rate limits

---

## 📊 Rate Limits

### LinkedIn API

- **Posts:** 100 per day per user
- **Reads:** 500 per day per app
- **Burst:** 10 requests per second

**Best Practices:**
- Space out posts (1-2 per day)
- Cache read data
- Implement exponential backoff

### Instagram Graph API

- **Posts:** 25 per day per user
- **Reads:** 200 per hour per user
- **Burst:** 5 requests per second

**Best Practices:**
- Limit to 1-2 posts per day
- Use scheduling for optimal times
- Batch read requests

---

## 🆘 Troubleshooting

### LinkedIn: "Invalid client credentials"

**Solution:**
1. Verify Client ID and Secret in `.env`
2. Check for extra spaces or quotes
3. Regenerate credentials if needed

### LinkedIn: "Insufficient permissions"

**Solution:**
1. Go to app **"Products"** tab
2. Ensure **"Share on LinkedIn"** is approved
3. Re-request if needed

### Instagram: "Invalid access token"

**Solution:**
1. Token may have expired (60 days)
2. Generate new long-lived token
3. Update `.env`

### Instagram: "Instagram account not found"

**Solution:**
1. Verify account is Business/Creator
2. Check Facebook Page connection
3. Verify Business Account ID is correct

### Instagram: "Permissions error"

**Solution:**
1. Re-generate token with correct permissions
2. Ensure all required scopes are granted
3. Check app is in "Live" mode (not Development)

---

## ✅ Verification Checklist

Before using the publishing scripts, verify:

- [ ] LinkedIn app created and approved
- [ ] LinkedIn Client ID and Secret in `.env`
- [ ] LinkedIn access token generated and in `.env`
- [ ] LinkedIn connection test passes
- [ ] Instagram Business account set up
- [ ] Facebook Page connected to Instagram
- [ ] Facebook app created with Instagram product
- [ ] Instagram access token (long-lived) in `.env`
- [ ] Instagram Business Account ID in `.env`
- [ ] Instagram connection test passes
- [ ] `.env` file in `.gitignore`
- [ ] All tokens have 30+ days until expiration

---

**Last Updated:** December 2024  
**Version:** 1.0
