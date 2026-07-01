import { useState } from "react";

import { AppLayout, type AppPage } from "./layouts/AppLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { DatasetsPage } from "./pages/DatasetsPage";
import { QueryConsolePage } from "./pages/QueryConsolePage";
import { SystemPage } from "./pages/SystemPage";

export default function App() {
  const [activePage, setActivePage] = useState<AppPage>("dashboard");

  function renderPage() {
    if (activePage === "dashboard") {
      return <DashboardPage />;
    }

    if (activePage === "datasets") {
      return <DatasetsPage />;
    }

    if (activePage === "query") {
      return <QueryConsolePage />;
    }

    return <SystemPage />;
  }

  return (
    <AppLayout activePage={activePage} onNavigate={setActivePage}>
      {renderPage()}
    </AppLayout>
  );
}