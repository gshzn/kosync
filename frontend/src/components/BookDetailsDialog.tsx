import { BookMarked, Pencil } from "lucide-react";
import { useNavigate } from "react-router-dom";

import type { Book } from "../types/books";
import { Button } from "./ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";

interface BookDetailsDialogProps {
  book: Book;
  children: React.ReactNode;
}

export function BookDetailsDialog({ book, children }: BookDetailsDialogProps) {
  const navigate = useNavigate();

  const coverSrc = book.cover_image_base64
    ? `data:image/jpeg;base64,${book.cover_image_base64}`
    : null;

  return (
    <Dialog>
      <DialogTrigger asChild className="cursor-pointer transition-opacity hover:opacity-80">
        {children}
      </DialogTrigger>
      <DialogContent className="max-w-2xl sm:max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>{book.title}</DialogTitle>
          <DialogDescription>
            {book.author || "Unknown author"}
          </DialogDescription>
        </DialogHeader>
        
        <div className="flex flex-col gap-6 py-4 sm:flex-row overflow-y-auto">
          {/* Cover Image Section */}
          <div className="mx-auto shrink-0 sm:mx-0">
            <div className="flex h-64 w-48 items-center justify-center overflow-hidden rounded-md border bg-muted shadow-sm">
              {coverSrc ? (
                <img
                  src={coverSrc}
                  alt={book.title}
                  className="h-full w-full object-contain"
                />
              ) : (
                <BookMarked className="h-16 w-16 text-muted-foreground/50" />
              )}
            </div>
          </div>

          {/* Details Section */}
          <div className="flex flex-1 flex-col gap-4">
            <div className="space-y-1">
              <h3 className="font-semibold leading-none tracking-tight">Description</h3>
              <div className="text-sm text-muted-foreground">
                {book.description ? (
                   <div 
                     className="text-sm text-muted-foreground [&_p]:leading-relaxed [&_p]:mb-4"
                     dangerouslySetInnerHTML={{ __html: book.description }}
                   />
                ) : (
                  <p className="italic text-muted-foreground/60">No description available.</p>
                )}
              </div>
            </div>
            
            {/* Metadata if needed, e.g. dates */}
            <div className="mt-auto pt-4 text-xs text-muted-foreground">
              {book.updated_at && (
                <p>Last updated: {new Date(book.updated_at).toLocaleDateString()}</p>
              )}
            </div>
          </div>
        </div>

        <DialogFooter className="sm:justify-between gap-2">
            <DialogClose asChild>
                <Button variant="secondary">Close</Button>
            </DialogClose>
            <Button onClick={() => navigate(`/book/${book.id}/edit`)}>
              <Pencil className="mr-2 h-4 w-4" />
              Edit Details
            </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
