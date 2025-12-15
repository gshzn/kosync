import { useState } from "react";
import { Lock } from "lucide-react";

import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";

export function LoginPage() {
  const { signInWithGoogle } = useAuth();
  const [submitting, setSubmitting] = useState(false);

  const handleGoogleLogin = async () => {
    setSubmitting(true);
    try {
      await signInWithGoogle();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="app-shell flex items-center justify-center px-4">
      <div className="mx-auto flex w-full max-w-md flex-col gap-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome to Kosync Reader
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Sign in with your Google account to manage your EPUB library.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lock className="h-5 w-5 text-primary" />
              Sign in
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Button
              className="w-full"
              onClick={handleGoogleLogin}
              disabled={submitting}
            >
              {submitting ? "Signing in..." : "Sign in with Google"}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
