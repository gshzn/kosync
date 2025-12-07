import { ReactNode } from "react";
import { LogOut, Menu, BookOpen } from "lucide-react";

import { useAuth } from "../contexts/AuthContext";
import { Avatar, AvatarFallback } from "../components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../components/ui/dropdown-menu";
import { Button } from "../components/ui/button";

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const { user, signOut } = useAuth();

  const initials =
    user?.email?.[0]?.toUpperCase() ??
    user?.user_metadata?.name?.[0]?.toUpperCase() ??
    "?";

  return (
    <div className="app-shell">
      <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
        <div className="container flex h-16 items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
              <BookOpen className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold tracking-tight text-foreground">
                Kosync Reader
              </span>
              <span className="text-xs text-muted-foreground">
                Your EPUBs, synced and searchable
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden text-right sm:flex sm:flex-col">
              <span className="text-xs font-medium text-foreground">
                {user?.email ?? "Signed in"}
              </span>
              <span className="text-[11px] text-muted-foreground">
                Authenticated
              </span>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="flex items-center gap-2 rounded-full px-2"
                >
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="text-xs font-medium">
                      {initials}
                    </AvatarFallback>
                  </Avatar>
                  <Menu className="hidden h-4 w-4 sm:inline-block" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuLabel>My Account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  className="cursor-pointer text-destructive focus:text-destructive"
                  onSelect={(event) => {
                    event.preventDefault();
                    void signOut();
                  }}
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Sign out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      <main className="container flex min-h-[calc(100vh-4rem)] flex-col gap-8 py-8">
        {children}
      </main>
    </div>
  );
}


