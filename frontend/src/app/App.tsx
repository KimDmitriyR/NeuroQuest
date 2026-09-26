import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { HomePage } from "../pages/HomePage";
import { QuestPage } from "../pages/QuestPage";
import { ProfilePage } from "../pages/ProfilePage";
import { MissionsPage } from "../pages/MissionsPage";
import { MissionPage } from "../pages/MissionPage";
import { ReviewPage } from "../pages/ReviewPage";
import { FinalePage } from "../pages/FinalePage";

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
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
