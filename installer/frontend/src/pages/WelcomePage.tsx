import { useEffect, useState } from "react";
import type { User } from "@supabase/supabase-js";
import { CheckCircle2, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { InstallKoSync, ListKoboDevices } from "../../wailsjs/go/main/App";
import type { main } from "../../wailsjs/go/models";
import { supabase } from "@/lib/supabaseClient";

type InstallState = "idle" | "installing" | "success" | "error";

interface WelcomePageProps {
  user: User;
  onSignOut: () => void;
}

function SuccessScreen() {
  return (
    <div className="flex flex-col items-center gap-4 text-center">
      <CheckCircle2 className="h-12 w-12 text-green-500" />
      <h2 className="text-xl font-semibold">KoSync installed!</h2>
      <p className="text-sm text-muted-foreground">
        The installation was successful. You can now safely eject your e-reader.
        It will finish the installation by updating.
        </p>
        <p className="text-sm text-muted-foreground">
        After the update,
        you'll find the KoSync app in the bottom-right menu on your Kobo. 
        In the menu, hit Synchronise to download
        the books from your KoSync account!
      </p>
    </div>
  );
}

export function WelcomePage({ user, onSignOut }: WelcomePageProps) {
  const displayName = (user.user_metadata?.full_name as string | undefined) ?? user.email ?? "you";
  const [devices, setDevices] = useState<main.KoboDevice[]>([]);
  const [installState, setInstallState] = useState<InstallState>("idle");
  const [errorMessage, setErrorMessage] = useState<string>("");

  useEffect(() => {
    if (installState === "success") return;
    const poll = async () => {
      const found = await ListKoboDevices();
      setDevices(found ?? []);
    };
    poll();
    const id = setInterval(poll, 1000);
    return () => clearInterval(id);
  }, [installState]);

  const device = devices[0] ?? null;

  async function handleInstall() {
    if (!device) return;
    setInstallState("installing");
    setErrorMessage("");
    try {
      const { data } = await supabase.auth.getSession();
      const token = data.session?.access_token;
      if (!token) throw new Error("Not authenticated");
      await InstallKoSync(device.mountPath, token);
      setInstallState("success");
    } catch (e: unknown) {
      setErrorMessage(e instanceof Error ? e.message : String(e));
      setInstallState("error");
    }
  }

  return (
    <div className="app-shell flex items-center justify-center px-4">
      <div className="mx-auto flex w-full max-w-md flex-col gap-6">
        {installState !== "success" && (
          <div className="text-center">
            <h1 className="text-3xl font-bold tracking-tight">
              {device ? "Kobo detected!" : "Waiting for your Kobo..."}
            </h1>
          </div>
        )}
        <Card>
          <CardHeader>
            {installState !== "success" && (
              <CardTitle className="text-center">
                {device ? device.name : "No device found"}
              </CardTitle>
            )}
          </CardHeader>
          <CardContent className="flex flex-col text-center items-center gap-4">
            {installState === "success" ? (
              <SuccessScreen />
            ) : device ? (
              <>
                <p className="text-sm text-muted-foreground">{device.mountPath}</p>
                {installState === "error" && (
                  <p className="text-sm text-destructive">{errorMessage}</p>
                )}
                <Button
                  onClick={handleInstall}
                  disabled={installState === "installing"}
                >
                  {installState === "installing" ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Installing...
                    </>
                  ) : installState === "error" ? (
                    "Retry"
                  ) : (
                    "Install KoSync"
                  )}
                </Button>
              </>
            ) : (
              <>
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <p className="text-sm text-muted-foreground">
                  Connect your Kobo e-reader to this PC via USB.
                </p>
                <p className="text-sm text-muted-foreground">
                  Make sure to tap <span className="font-semibold">Connect</span> on your Kobo's screen to allow access.
                </p>
              </>
            )}
          </CardContent>
        </Card>
        {installState !== "success" && (
          <p className="text-center text-sm text-muted-foreground">
            Signed in as {displayName}. Not you?{" "}
            <button
              className="pl-1 underline hover:text-foreground"
              onClick={onSignOut}
            >
              Sign in with a different account
            </button>
          </p>
        )}
      </div>
    </div>
  );
}
