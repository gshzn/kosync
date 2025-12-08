import { useMemo } from "react";
import { BookMarked, Loader2 } from "lucide-react";

import { AppLayout } from "../layout/AppLayout";
import { useBooks } from "../hooks/useBooks";
import { BookUploadForm } from "../components/BookUploadForm";
import { BookDetailsDialog } from "../components/BookDetailsDialog";
import { Badge } from "../components/ui/badge";
import { Skeleton } from "../components/ui/skeleton";

export function DashboardPage() {
  const { books, loading, error, refresh } = useBooks();

  const sortedBooks = useMemo(
    () =>
      [...books].sort((a, b) => {
        const aDate = a.updated_at ?? a.created_at ?? "";
        const bDate = b.updated_at ?? b.created_at ?? "";
        return bDate.localeCompare(aDate);
      }),
    [books]
  );

  return (
    <AppLayout>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center">
          <div className="space-y-2">
            <h1 className="text-3xl font-bold tracking-tight">
              Your ebooks
            </h1>
            <p className="text-sm text-muted-foreground">
              Upload EPUB files and manage extracted metadata.
            </p>
          </div>
        </div>

        <BookUploadForm onUploaded={refresh} />

        <div className="space-y-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold">Library</h2>
              <p className="text-sm text-muted-foreground">
                {sortedBooks.length > 0
                  ? `${sortedBooks.length} ${
                      sortedBooks.length === 1 ? "book" : "books"
                    } in your library.`
                  : "No books yet. Upload your first EPUB to get started."}
              </p>
            </div>
            {loading && (
              <Badge variant="secondary" className="inline-flex items-center gap-1.5">
                <Loader2 className="h-3 w-3 animate-spin" />
                Loading
              </Badge>
            )}
          </div>

          {error && (
            <div className="rounded-md border border-destructive/50 bg-destructive/10 p-4 text-sm text-destructive">
              <strong>Error loading books:</strong> {error}
            </div>
          )}

          {loading && sortedBooks.length === 0 ? (
            <div className="space-y-3">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-3/4" />
            </div>
          ) : sortedBooks.length === 0 ? (
            <div className="flex flex-col items-center gap-3 rounded-lg border border-dashed py-12 text-center">
              <BookMarked className="h-12 w-12 text-muted-foreground/50" />
              <div>
                <p className="font-medium">No books yet</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Upload your first EPUB to get started.
                </p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
              {sortedBooks.map((book) => {
                const coverSrc = book.cover_image_base64
                  ? `data:image/jpeg;base64,${book.cover_image_base64}`
                  : null;

                return (
                  <BookDetailsDialog key={book.id} book={book}>
                    <div
                      className="flex flex-col overflow-hidden rounded-lg border bg-card text-card-foreground shadow-sm h-full text-left"
                    >
                      <div className="flex h-96 w-full items-center justify-center bg-muted overflow-hidden">
                        {coverSrc ? (
                          <img
                            src={coverSrc}
                            alt={book.title || "Book cover"}
                            className="h-full w-auto object-contain"
                          />
                        ) : (
                          <BookMarked className="h-10 w-10 text-muted-foreground/60" />
                        )}
                      </div>
                      <div className="flex flex-1 flex-col gap-2 p-3">
                        <div className="space-y-1">
                          <p className="line-clamp-2 text-sm font-semibold">
                            {book.title || (
                              <span className="text-muted-foreground">Untitled</span>
                            )}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {book.author || "Unknown author"}
                          </p>
                        </div>
                        <div
                          className="line-clamp-3 text-xs text-muted-foreground"
                          dangerouslySetInnerHTML={{
                            __html: book.description || "No description",
                          }}
                        />
                      </div>
                    </div>
                  </BookDetailsDialog>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
