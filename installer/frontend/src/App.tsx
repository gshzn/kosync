import { useEffect, useState } from "react";
import type { User } from "@supabase/supabase-js";
import { EventsOn } from "../wailsjs/runtime/runtime";
import { supabase } from "./lib/supabaseClient";
import { LoginPage } from "./pages/LoginPage";
import { WelcomePage } from "./pages/WelcomePage";

function App() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    EventsOn(
      "auth-complete",
      async (data: { access_token: string; refresh_token: string }) => {
        const { data: sessionData, error } = await supabase.auth.setSession({
          access_token: data.access_token,
          refresh_token: data.refresh_token,
        });
        if (!error && sessionData.user) {
          setUser(sessionData.user);
        }
      }
    );
  }, []);

  if (user) return <WelcomePage user={user} />;
  return <LoginPage />;
}

export default App;
