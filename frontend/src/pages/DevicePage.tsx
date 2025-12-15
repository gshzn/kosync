import { AppLayout } from "../layout/AppLayout";
import { ClientInstallSection } from "../components/ClientInstallSection";

export function DevicePage() {
  return (
    <AppLayout>
      <div className="flex flex-col gap-6">
        <ClientInstallSection />
      </div>
    </AppLayout>
  );
}
