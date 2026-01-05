export interface Book {
  id: string;
  title: string;
  author: string;
  description?: string | null;
  created_at?: string;
  updated_at?: string;
  cover_image_base64?: string;
}


