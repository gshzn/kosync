import { useEffect, useState } from "react";
import type { User } from "@supabase/supabase-js";
import { Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ListKoboDevices } from "../../wailsjs/go/main/App";
import { BrowserOpenURL } from "../../wailsjs/runtime/runtime";
import type { main } from "../../wailsjs/go/models";

interface WelcomePageProps {
  user: User;
}

export function WelcomePage({ user }: WelcomePageProps) {
  const displayName = (user.user_metadata?.full_name as string | undefined) ?? user.email ?? "you";
  const [devices, setDevices] = useState<main.KoboDevice[]>([]);

  useEffect(() => {
    const poll = async () => {
      const found = await ListKoboDevices();
      setDevices(found ?? []);
    };
    poll();
    const id = setInterval(poll, 1000);
    return () => clearInterval(id);
  }, []);

  const device = devices[0] ?? null;

  return (
    <div className="app-shell flex items-center justify-center px-4">
      <div className="mx-auto flex w-full max-w-md flex-col gap-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">
            {device ? "Kobo detected!" : "Waiting for your Kobo..."}
          </h1>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="text-center">
              {device ? device.name : "No device found"}
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center gap-4 py-8">
            {device ? (
              <>
                <p className="text-sm text-muted-foreground">{device.mountPath}</p>
                <Button
                  onClick={() => console.log("Install KoSync on", device.mountPath)}
                >
                  Install KoSync
                </Button>
              </>
            ) : (
              <>
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <p className="text-sm text-muted-foreground">
                  Connect your Kobo e-reader to this PC via USB.
                </p>
              </>
            )}
          </CardContent>
        </Card>
        <p className="text-center text-sm text-muted-foreground">
          Signed in as {displayName}.{" "}
          <button
            className="underline hover:text-foreground"
            onClick={() => BrowserOpenURL(`${import.meta.env.VITE_KOSYNC_APP_URL}/login?desktop_redirect=true`)}
          >
            Not you? Sign in with a different account
          </button>
        </p>
      </div>
    </div>
  );
}
