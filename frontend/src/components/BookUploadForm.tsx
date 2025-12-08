import { FormEvent, useState } from "react";
import { Upload } from "lucide-react";
import { toast } from "sonner";

import { useAuth } from "../contexts/AuthContext";
import { API_BASE_URL } from "../lib/config";
import { Button } from "./ui/button";

interface BookUploadFormProps {
  onUploaded?: () => void;
}

export function BookUploadForm({ onUploaded }: BookUploadFormProps) {
  const { session } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!session?.access_token) {
      toast.error("You must be signed in to upload books.");
      return;
    }
    if (!file) {
      toast.error("Please select an EPUB file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/books`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed (${response.status})`);
      }

      toast.success("EPUB uploaded. Metadata will be processed shortly.");
      setFile(null);
      if (onUploaded) {
        onUploaded();
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Unexpected error uploading EPUB";
      toast.error(message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-4 rounded-lg border border-dashed bg-muted/50 p-6 sm:flex-row sm:items-center sm:justify-between"
    >
      <div className="space-y-1">
        <p className="font-semibold">Upload EPUB</p>
        <p className="text-sm text-muted-foreground">
          Select an <span className="font-mono">.epub</span> file. Metadata will
          be extracted by the backend.
        </p>
      </div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <input
          type="file"
          accept=".epub"
          className="block w-full text-sm file:mr-4 file:rounded-md file:border-0 file:bg-primary file:px-4 file:py-2 file:text-sm file:font-semibold file:text-primary-foreground hover:file:bg-primary/90"
          onChange={(event) => {
            const nextFile = event.target.files?.[0];
            setFile(nextFile ?? null);
          }}
        />
        <Button
          type="submit"
          size="sm"
          className="flex items-center gap-2 whitespace-nowrap"
          disabled={uploading || !file}
        >
          <Upload className="h-4 w-4" />
          {uploading ? "Uploading..." : "Upload"}
        </Button>
      </div>
    </form>
  );
}


