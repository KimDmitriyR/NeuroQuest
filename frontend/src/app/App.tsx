import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { HomePage } from "../pages/HomePage";
import { QuestPage } from "../pages/QuestPage";
import { ProfilePage } from "../pages/ProfilePage";
import { MissionsPage } from "../pages/MissionsPage";
import { MissionPage } from "../pages/MissionPage";
import { ReviewPage } from "../pages/ReviewPage";
import { FinalePage } from "../pages/FinalePage";
import { ParentAuthPage } from "../pages/ParentAuthPage";
import { ParentDashboardPage } from "../pages/ParentDashboardPage";
import { TermsPage } from "../pages/TermsPage";
import { PrivacyPage } from "../pages/PrivacyPage";
import { PARENT_TOKEN_KEY } from "../api/client";

const queryClient = new QueryClient();

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/quest/:sessionId" element={<QuestPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/missions" element={<MissionsPage />} />
          <Route path="/mission/:missionId" element={<MissionPage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/finale" element={<FinalePage />} />
          <Route path="/parent" element={<ParentAuthOrDashboard />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

function ParentAuthOrDashboard() {
  const hasToken = !!localStorage.getItem(PARENT_TOKEN_KEY);
  return hasToken ? <ParentDashboardPage /> : <ParentAuthPage />;
}
