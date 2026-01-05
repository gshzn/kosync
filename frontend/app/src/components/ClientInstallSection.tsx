import { Download, Info, AlertTriangle, Monitor, Apple, Cable, FolderInput, RefreshCw, Menu, Loader2 } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { API_BASE_URL } from "../lib/config";
import { useAuth } from "../contexts/AuthContext";
import { useState } from "react";
import { toast } from "sonner";

export function ClientInstallSection() {
  const { session } = useAuth();
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    if (!session?.access_token) {
      toast.error("You must be logged in to download the client.");
      return;
    }

    setIsDownloading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/download`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to download file");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "KoboRoot.tgz";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success("Download started!");
    } catch (error) {
      console.error("Download error:", error);
      toast.error("Failed to download KoboRoot.tgz. Please try again.");
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <Card className="relative overflow-hidden transition-all">
      <CardHeader>
        <CardTitle className="text-xl">Install Kosync on your Kobo</CardTitle>
        <CardDescription>
          Follow these steps to install the Kosync client and start synchronising your e-books.
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-8">
          <div className="flex gap-4">
            <div className="flex-none">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary font-bold">1</span>
            </div>
            <div className="space-y-2 pt-1">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <Cable className="h-5 w-5" />
                Connect your device
              </h3>
              <p className="text-muted-foreground">
                Attach your Kobo device to your PC using a USB cable. Make sure to tap "Connect" on the device screen if prompted.
              </p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-none">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary font-bold">2</span>
            </div>
            <div className="space-y-3 pt-1 w-full">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <Download className="h-5 w-5" />
                Download Client
              </h3>
              <p className="text-muted-foreground">
                Download the Kosync client package.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 items-start">
                <Button 
                  onClick={handleDownload} 
                  variant="default" 
                  disabled={isDownloading}
                >
                  {isDownloading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Download className="mr-2 h-4 w-4" />
                  )}
                  Download KoboRoot.tgz
                </Button>
              </div>

              <div className="rounded-md bg-amber-50 p-3 text-sm text-amber-800 dark:bg-amber-900/20 dark:text-amber-200 border border-amber-200 dark:border-amber-900/50 max-w-2xl">
                <p className="font-medium flex items-center gap-1.5 mb-1">
                   <AlertTriangle className="h-4 w-4" /> Safari Users
                </p>
                <p>
                  Safari auto-unzips files. Use Chrome/Firefox or disable "Open safe files" in Safari settings. The file must be named <code>KoboRoot.tgz</code> (not .tar or folder).
                </p>
              </div>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-none">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary font-bold">3</span>
            </div>
            <div className="space-y-3 pt-1 w-full">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <FolderInput className="h-5 w-5" />
                Install Package
              </h3>
              <p className="text-muted-foreground">
                Place the downloaded <code>KoboRoot.tgz</code> file into the <code>.kobo</code> folder on your e-reader's drive.
              </p>

              <div className="rounded-md bg-muted/50 p-4 text-sm max-w-2xl">
                <p className="font-medium flex items-center gap-1.5 mb-2">
                    <Info className="h-4 w-4 text-blue-500" /> Can't see the .kobo folder?
                </p>
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="flex items-start gap-2">
                    <Monitor className="h-4 w-4 mt-0.5 shrink-0 text-muted-foreground" />
                    <div>
                      <span className="font-medium block">Windows</span>
                      <span className="text-muted-foreground text-xs">View &gt; Show &gt; Hidden items</span>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <Apple className="h-4 w-4 mt-0.5 shrink-0 text-muted-foreground" />
                    <div>
                      <span className="font-medium block">macOS</span>
                      <span className="text-muted-foreground text-xs">Press Cmd + Shift + . (dot)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-none">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary font-bold">4</span>
            </div>
            <div className="space-y-2 pt-1">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <RefreshCw className="h-5 w-5" />
                Update
              </h3>
              <p className="text-muted-foreground">
                Eject the ereader safely from your computer and unplug the cable. Wait for the device to reboot and update.
              </p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-none">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary font-bold">5</span>
            </div>
            <div className="space-y-2 pt-1">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <Menu className="h-5 w-5" />
                Synchronise
              </h3>
              <p className="text-muted-foreground">
                Find the <strong>Kosync</strong> menu in the bottom menu bar and click on <strong>Synchronise</strong>!
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
