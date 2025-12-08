import { useCallback, useEffect, useState } from "react";

import { useAuth } from "../contexts/AuthContext";
import { API_BASE_URL } from "../lib/config";
import type { Book } from "../types/books";

interface UseBooksResult {
  books: Book[];
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useBooks(): UseBooksResult {
  const { session } = useAuth();
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  const refresh = useCallback(() => {
    setReloadToken((token) => token + 1);
  }, []);

  useEffect(() => {
    const fetchBooks = async () => {
      if (!session?.access_token) return;
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${API_BASE_URL}/books`, {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });
        if (!response.ok) {
          throw new Error(`Failed to load books (${response.status})`);
        }
        const data = (await response.json()) as Book[];
        setBooks(data);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Unexpected error loading books";
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    void fetchBooks();
  }, [session?.access_token, reloadToken]);

  return { books, loading, error, refresh };
}


