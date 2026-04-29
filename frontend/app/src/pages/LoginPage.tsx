import { useState } from "react";
import { Lock } from "lucide-react";

import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";

type Mode = "signin" | "signup";

export function LoginPage() {
  const { signIn, signUp, signInWithGoogle } = useAuth();
  const [mode, setMode] = useState<Mode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (mode === "signin") {
        await signIn(email, password);
      } else {
        await signUp(email, password);
      }
    } catch {
      // errors are toasted in AuthContext
    } finally {
      setSubmitting(false);
    }
  };

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
            Log in or sign up to manage your EPUB library and<br/>
            start sending e-books to your Kobo e-Reader!
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lock className="h-5 w-5 text-primary" />
              {mode === "signin" ? "Sign in" : "Create account"}
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete={mode === "signin" ? "current-password" : "new-password"}
                />
              </div>
              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting
                  ? mode === "signin"
                    ? "Signing in..."
                    : "Creating account..."
                  : mode === "signin"
                    ? "Sign in"
                    : "Create account"}
              </Button>
            </form>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-card px-2 text-muted-foreground">or</span>
              </div>
            </div>

            <Button
              variant="outline"
              className="w-full"
              onClick={handleGoogleLogin}
              disabled={submitting}
            >
              Sign in with Google
            </Button>

            <p className="text-center text-sm text-muted-foreground">
              {mode === "signin" ? (
                <>
                  Don't have an account?{" "}
                  <button
                    type="button"
                    className="font-medium text-primary underline-offset-4 hover:underline"
                    onClick={() => setMode("signup")}
                  >
                    Sign up
                  </button>
                </>
              ) : (
                <>
                  Already have an account?{" "}
                  <button
                    type="button"
                    className="font-medium text-primary underline-offset-4 hover:underline"
                    onClick={() => setMode("signin")}
                  >
                    Sign in
                  </button>
                </>
              )}
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
