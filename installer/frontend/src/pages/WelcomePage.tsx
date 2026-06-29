import type { User } from "@supabase/supabase-js";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface WelcomePageProps {
  user: User;
}

export function WelcomePage({ user }: WelcomePageProps) {
  const name =
    (user.user_metadata?.full_name as string | undefined) ??
    user.email ??
    "there";

  return (
    <div className="app-shell flex items-center justify-center px-4">
      <div className="mx-auto flex w-full max-w-md flex-col gap-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">You're in!</h1>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="text-center">Welcome, {name}</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center gap-2 py-8">
            <p className="text-sm text-muted-foreground">
              The installer is ready to continue.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
