import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AppLayout } from "./AppLayout";
import { SessionProvider } from "../features/session/SessionProvider";
import { RequireSignedIn } from "../features/session/RequireSignedIn";
import { useSession } from "../features/session/useSession";
import { HomePage } from "../pages/HomePage";
import { QuestPage } from "../pages/QuestPage";
import { ProfilePage } from "../pages/ProfilePage";
import { MissionsPage } from "../pages/MissionsPage";
import { MissionPage } from "../pages/MissionPage";
import { ReviewPage } from "../pages/ReviewPage";
import { FinalePage } from "../pages/FinalePage";
import { ParentAuthPage } from "../pages/ParentAuthPage";
import { ParentDashboardPage } from "../pages/ParentDashboardPage";
import { SettingsPage } from "../pages/SettingsPage";
import { TermsPage } from "../pages/TermsPage";
import { PrivacyPage } from "../pages/PrivacyPage";

const queryClient = new QueryClient();

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SessionProvider>
        <BrowserRouter>
          <Routes>
            {/* the grand finale is a full-screen show: no header/footer */}
            <Route element={<RequireSignedIn />}>
              <Route path="/finale" element={<FinalePage />} />
            </Route>

            <Route element={<AppLayout />}>
              {/* open to everyone: landing page, sign-in, settings, legal texts */}
              <Route path="/" element={<HomePage />} />
              <Route path="/parent" element={<ParentAuthOrDashboard />} />

              {/* cards, missions and progress: signed-in users only */}
              <Route element={<RequireSignedIn />}>
                <Route path="/quest/:sessionId" element={<QuestPage />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/missions" element={<MissionsPage />} />
                <Route path="/mission/:missionId" element={<MissionPage />} />
              </Route>
              <Route element={<RequireSignedIn parentOnly />}>
                <Route path="/review" element={<ReviewPage />} />
              </Route>

              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/terms" element={<TermsPage />} />
              <Route path="/privacy" element={<PrivacyPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </SessionProvider>
    </QueryClientProvider>
  );
}

function ParentAuthOrDashboard() {
  const { parent, parentLoading } = useSession();
  return parent || parentLoading ? <ParentDashboardPage /> : <ParentAuthPage />;
}
