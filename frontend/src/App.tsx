import { useState } from "react";

import { AppLayout, type AppPage } from "./layouts/AppLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { DatasetsPage } from "./pages/DatasetsPage";
import { PlaceholderPage } from "./pages/PlaceholderPage";
import { QueryConsolePage } from "./pages/QueryConsolePage";

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

    return (
      <PlaceholderPage
        title="System Overview"
        description="This section will show health checks, backend configuration, storage mode, and deployment details."
      />
    );
  }

  return (
    <AppLayout activePage={activePage} onNavigate={setActivePage}>
      {renderPage()}
    </AppLayout>
  );
}