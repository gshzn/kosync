## Kosync Reader frontend

React + Vite + TypeScript frontend for Kosync Reader. Uses Supabase for authentication and talks to an existing backend to upload EPUB files and manage ebook metadata.

### Setup

1. Install dependencies:

```bash
pnpm install # or npm install / yarn install
```

2. Create a `.env` file in the project root and configure:

```bash
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_BASE_URL=http://192.168.50.215
```

3. Start the dev server:

```bash
pnpm dev
```

### Behaviour

- Auth via Supabase email/password.
- `GET /books` to list ebooks.
- `POST /books` with `FormData` containing an `.epub` file to upload.
- `PATCH /books/:id` to update metadata (title, author, description).


