# Mail Manager

Mail Manager is a privacy-first, stateless web application that helps users analyze, organize, and clean their email inbox by identifying bulky and unnecessary emails.

## Features

- **Secure OAuth Connection**: Connect to Gmail and Outlook without sharing your password.
- **Privacy First**: Stateless architecture. We don't store your emails or tokens in a database.
- **AI Recommendation Engine**: Smart heuristics to identify newsletters, bulk senders, and large emails.
- **Bulk Cleanup**: Easily move unwanted emails to trash.
- **PWA Support**: Installable on mobile and desktop devices.
- **Dark & Light Mode**: Modern, responsive interface.

## Tech Stack

- **Frontend**: React (Vite), Tailwind CSS, Lucide Icons, Framer Motion.
- **Backend**: Flask, Flask-SocketIO, Flask-Session.
- **APIs**: Gmail API, Microsoft Graph API.

---

## Development Guide (Step-by-Step)

To run this project locally, you need to have **two terminal windows** open simultaneously: one for the backend (Flask) and one for the frontend (React).

### Step 1: Set up the Backend

1. **Open Terminal #1** and navigate to the backend folder:
   ```bash
   cd backend
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables**:
   - Create a file named `.env` in the `backend/` directory.
   - Copy the contents from `.env.example` into `.env`.
   - Fill in your `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, etc. (See the OAuth Configuration section below).
4. **Run the Backend Server**:
   ```bash
   python run.py
   ```
   *The backend will start at `http://localhost:5000`.*

### Step 2: Set up the Frontend

1. **Open Terminal #2** and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Run the Frontend Development Server**:
   ```bash
   npm run dev
   ```
   *The frontend will start at `http://localhost:5173`.*

### Step 3: Access the App

- Open your browser and go to **`http://localhost:5173`**.
- The frontend is configured to automatically proxy requests to the backend at port 5000.
- You can now click "Connect Gmail" or "Connect Outlook" to begin the analysis.

---

## OAuth Configuration Guide

### Google (Gmail API)

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the **Gmail API**.
4. Go to **APIs & Services > OAuth consent screen**. Configure it for "External" use.
5. Add the following scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.modify`
6. Go to **Credentials > Create Credentials > OAuth client ID**.
7. Choose **Web application**.
8. Add Redirect URIs: `http://localhost:5000/api/auth/gmail/callback` (and your production URL).
9. Copy the Client ID and Client Secret to your `.env` file.

### Microsoft (Outlook / Graph API)

1. Go to the [Microsoft Entra admin center](https://entra.microsoft.com/) (Azure AD).
2. Go to **App registrations > New registration**.
3. Choose **Accounts in any organizational directory and personal Microsoft accounts**.
4. Add Redirect URI: `http://localhost:5000/api/auth/outlook/callback` (Web).
5. Go to **Certificates & secrets > New client secret**.
6. Copy the Client ID and Secret to your `.env` file.
7. Under **API permissions**, add:
   - `Mail.Read`
   - `Mail.ReadWrite`

---

## AI Recommendation Logic

The application uses a heuristic-based AI engine to label emails:

- **Safe to Delete**: High-frequency senders (>50 emails), common bulk keywords (newsletter, marketing), or large attachments (>5MB).
- **Review**: Moderate frequency or partial matches with bulk patterns.
- **Keep**: Personal communication or low-frequency senders.

---

## Deployment Guide

### Render (Unified Deployment)

1. Create a new Web Service on [Render](https://render.com).
2. Connect your GitHub repository.
3. Set **Build Command**: `cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt`
4. Set **Start Command**: `cd backend && python run.py` (Or use Gunicorn/Eventlet in production).
5. Add Environment Variables from your `.env` file.

### Vercel (Frontend only)

1. Connect your repo to Vercel.
2. Set the root directory to `frontend`.
3. Configure the backend API URL as an environment variable.

---

## MetLife / Enterprise Deployment (Docker)

For deployment on internal platforms like MetLife, it is recommended to use Docker to ensure environment consistency.

### 1. Build the Docker Image
```bash
docker build -t mail-manager .
```

### 2. Run the Container
```bash
docker run -p 5000:5000 \
  -e GMAIL_CLIENT_ID=your_id \
  -e GMAIL_CLIENT_SECRET=your_secret \
  -e SECRET_KEY=your_secret_key \
  mail-manager
```

*Note: In an enterprise environment, ensure that your OAuth redirect URIs are registered for the specific internal domain used by the platform.*

---

## Security Note

This application is **stateless**. It uses server-side filesystem sessions to temporarily store tokens and metadata for the duration of the scan. All data is cleared when the session expires or the user logs out.
