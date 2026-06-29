import { useEffect } from "react";
import { Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { openBrowser } from "@/lib/wailsBindings";

export function LoginPage() {
  useEffect(() => {
    openBrowser("https://app.kosync.app/login?desktop_redirect=true");
  }, []);

  return (
    <div className="app-shell flex items-center justify-center px-4">
      <div className="mx-auto flex w-full max-w-md flex-col gap-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome to Kosync
          </h1>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="text-center">Logging in</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center gap-4 py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">
              Logging in in the browser...
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
