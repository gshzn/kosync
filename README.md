# KoSync

KoSync is an e-book synchronization tool for Kobo eReaders. It allows you to manage your ebook library through a web interface and automatically sync them to your device over the internet.

A live version of the project is available at [https://kosync.app](https://kosync.app).

## Why

I was on holiday and I didn't want to bring books, therefore I bought a Kobo e-reader. I shortly after found out I wasn't able to send books to the e-reader without attaching the e-reader to a PC via a cable. 

## Architecture

The KoSync project consists of a few components:

- Backend: A Python 3.12 API built with FastAPI, handling library management, file storage, and client binary generation.
- Client: A lightweight Go application which runs on Kobo devices. It relies on for the interface [NickelMenu](https://github.com/pgaskin/NickelMenu) and [NickelDBus](https://github.com/shermp/NickelDBus) for extending the default Kobo interface. 
  - Huge thanks to the two projects and their maintainers.
- Frontend (Web app): A React application with Shadcn components for managing your e-books on the web.
    - Thanks Cursor + Gemini for assisting me on this.
- Landing Page: A simple landing page built with Astro.
- Authentication: Managed through Supabase.

Finally, for the live version I have running, I set up a NGINX reverse proxy to route all requests to right server/static assets.

## Setup Instructions

### 1. Build the Go Client
The client must be compiled for the Kobo's ARM architecture and placed where the backend can find it for distribution.

```bash
cd client
GOOS=linux GOARCH=arm go build -o ../backend/kosync_client .
```

### 2. Configure the Backend
The backend runs in a Docker container. You need to provide environment variables for Supabase and general configuration.

1. Navigate to the backend directory: `cd backend`
2. Create a `.env` file with the following contents:
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_service_role_key
   DATABASE_URL=sqlite:////app/db/kosync.db
   BASE_URL=https://api-endpoint
   ALLOWED_ORIGINS=https://frontend-url
   ```
3. Start the service:
   ```bash
   docker-compose up -d
   ```

### 3. Build the Frontends

#### Web App
1. Navigate to the app directory: `cd frontend/app`
2. Install dependencies: `npm install`
3. Create a `.env` file:
   ```env
   VITE_SUPABASE_URL=your_supabase_project_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   VITE_API_BASE_URL=https://api-endpoint/api/v1
   ```
4. Build the project: `npm run build`

#### Landing Page
1. Navigate to the landing page directory: `cd frontend/landing-page`
2. Install dependencies: `npm install`
3. Build the project: `npm run build`

#### Reverse proxy

Set up a reverse proxy of your choice (e.g. NGINX/Caddy) to route requests to the correct place depending on the host.

## How to Use

1. **Sign Up**: Log in with Google on the 
2. **Upload Books**: Drag and drop your EPUB files into the web interface.
3. **Install Client**: 
   - Download the generated `KoboRoot.tgz` from the "Devices" section of the dashboard.
   - Place the `KoboRoot.tgz` update file on your device in the `.kobo` and wait for the KoSync client to be installed.
4. **Sync**: Use the new KoSync menu entry on your Kobo to synchronise your library. Your new books will be downloaded and automatically added to your Kobo library.
