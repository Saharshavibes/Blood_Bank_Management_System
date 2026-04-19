import { InventoryTable } from "@/components/inventory/InventoryTable";

export function AdminInventoryPage() {
  return (
    <div className="space-y-4">
      <section className="glass-card p-5">
        <h2 className="text-xl font-bold">Inventory Operations</h2>
        <p className="mt-1 text-sm text-black/65">
          Base inventory table with live API integration and scan-ready bag view.
        </p>
      </section>
      <InventoryTable />
    </div>
  );
}
