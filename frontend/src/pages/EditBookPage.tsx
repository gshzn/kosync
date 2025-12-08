import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Loader2, Save } from "lucide-react";
import { toast } from "sonner";

import { useAuth } from "../contexts/AuthContext";
import { AppLayout } from "../layout/AppLayout";
import { API_BASE_URL } from "../lib/config";
import type { Book } from "../types/books";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Badge } from "../components/ui/badge";

export function EditBookPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { session } = useAuth();
  
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Form state
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [description, setDescription] = useState("");

  useEffect(() => {
    const fetchBook = async () => {
      if (!id || !session?.access_token) return;
      
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/books/${id}`, {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });
        
        if (!response.ok) {
          throw new Error("Failed to load book details");
        }
        
        const data = await response.json() as Book;
        setBook(data);
        setTitle(data.title);
        setAuthor(data.author);
        setDescription(data.description || "");
      } catch (err) {
        toast.error("Could not load book details");
        navigate("/");
      } finally {
        setLoading(false);
      }
    };
    
    void fetchBook();
  }, [id, session, navigate]);

  const handleSave = async () => {
    if (!book || !session?.access_token) return;
    
    setSaving(true);
    try {
      const response = await fetch(`${API_BASE_URL}/books/${book.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          title,
          author,
          description: description || null,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to update book");
      }

      toast.success("Book updated successfully");
      navigate("/");
    } catch (err) {
      toast.error("Failed to update book");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex h-64 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </AppLayout>
    );
  }

  if (!book) return null;

  return (
    <AppLayout>
      <div className="mx-auto w-full max-w-2xl space-y-6">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate("/")}
            className="shrink-0"
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-2xl font-bold tracking-tight">Edit Book Details</h1>
        </div>

        <div className="grid gap-6 rounded-lg border bg-card p-6 shadow-sm">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Book title"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="author">Author</Label>
              <Input
                id="author"
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
                placeholder="Author name"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="min-h-[200px] resize-y"
              placeholder="Book description..."
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => navigate("/")}>
              Cancel
            </Button>
            <Button onClick={() => void handleSave()} disabled={saving}>
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
