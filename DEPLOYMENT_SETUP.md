# Deployment Setup Guide

## Issue: API Connection Error on Cloudflare Pages

If you're seeing "Unable to connect to the API" errors in your Cloudflare Pages deployment, it's because the frontend doesn't know about your Render backend URL.

## Solution

### Option 1: Manual Configuration in Cloudflare Pages Dashboard (Quickest)

1. Go to [Cloudflare Pages Dashboard](https://dash.cloudflare.com)
2. Select your **nexusrag** project
3. Go to **Settings** → **Environment variables**
4. Click **Add environment variable**
5. Add the following variables:

   **For Production:**
   - Key: `NEXT_PUBLIC_API_BASE_URL`
   - Value: `https://your-render-service-name.onrender.com`
   - Select **Production** environment
   
   **Example values:**
   ```
   NEXT_PUBLIC_API_BASE_URL=https://nexusrag-api.onrender.com
   ```

6. After adding, trigger a new deployment:
   - Go to **Deployments**
   - Click on the latest deployment
   - Click **Retry deployment**

### Option 2: Automated Deployment with GitHub Actions (Recommended)

To automatically deploy with the correct backend URL on every push:

1. Add GitHub Secrets to your repository:
   - Go to **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Add these secrets:
     ```
     CLOUDFLARE_API_TOKEN=<your-cloudflare-api-token>
     CLOUDFLARE_ACCOUNT_ID=<your-cloudflare-account-id>
     CLOUDFLARE_API_BASE_URL=https://your-render-backend-url.onrender.com
     ```

2. The GitHub Actions workflow will automatically:
   - Build the frontend with the correct API base URL
   - Deploy to Cloudflare Pages on every push to main branch

### Finding Your Values

**Render Backend URL:**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your **rag-api** service
3. Copy the URL from the top of the page (looks like `https://rag-api-xxxx.onrender.com`)

**Cloudflare Credentials:**
1. API Token: Go to [Cloudflare Dashboard](https://dash.cloudflare.com/profile/api-tokens)
   - Look for "API Tokens" section
   - Create a token with "Cloudflare Pages" permission
2. Account ID: Go to your Cloudflare account overview page
   - It's shown in the right sidebar under "Account ID"

## Verification

After setting the environment variables, verify the deployment works:

1. Go to your Cloudflare Pages site
2. Open the browser DevTools (F12)
3. Go to the **Network** tab
4. Submit a query
5. Look for the `/answer` API request
6. It should hit `https://your-render-backend-url.onrender.com/answer` (not localhost)

## Why This Happens

The frontend is a static site built with Next.js and exported as static HTML/CSS/JS. The API URL is embedded at **build time** using environment variables. Therefore:

- `NEXT_PUBLIC_API_BASE_URL` must be set **before** the build
- It defaults to `http://localhost:8000` if not provided
- This works on your local machine but fails in production because `localhost` resolves to the user's computer, not your backend

## Troubleshooting

**Still getting "Unable to connect" errors?**

1. Check the Render backend is running:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click your rag-api service
   - Check the logs for errors
   - Verify "Health" shows green checkmark

2. Verify CORS is configured:
   - Your backend should accept requests from `https://your-cloudflare-domain.pages.dev`
   - Check the `RAG__SECURITY__CORS_ORIGINS` environment variable in Render

3. Test the API directly:
   - Open browser console (F12)
   - Run: `fetch('https://your-render-url.onrender.com/health').then(r => r.json()).then(console.log)`
   - Should return `{"status":"ok"}` or similar

**Port 8000 in error message?**
This means the API URL is still pointing to localhost. Re-check that you set `NEXT_PUBLIC_API_BASE_URL` and re-deployed.
