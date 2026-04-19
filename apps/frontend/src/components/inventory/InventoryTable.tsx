import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";

import apiClient from "@/lib/api";
import { DegradedStateBanner } from "@/components/ui/DegradedStateBanner";
import { reportDegradedStateTransition } from "@/services/telemetry";
import type { BloodBag, BloodBagStatus } from "@/types/inventory";
import { BLOOD_BAG_STATUSES, BLOOD_TYPES, type BloodType } from "@/types/domain";

const SAMPLE_BAGS: BloodBag[] = [
  {
    id: "sample-1",
    bag_number: "BB-20260411-0001",
    donor_id: "donor-1",
    storage_hospital_id: "central-bank",
    blood_request_id: null,
    blood_type: "O+",
    component: "packed_red_cells",
    volume_ml: 450,
    collection_date: "2026-04-10T08:00:00Z",
    expiration_date: "2026-05-22T08:00:00Z",
    status: "available",
    created_at: "2026-04-10T08:00:00Z",
    updated_at: "2026-04-10T08:00:00Z",
  },
  {
    id: "sample-2",
    bag_number: "BB-20260411-0002",
    donor_id: "donor-2",
    storage_hospital_id: "city-medical",
    blood_request_id: null,
    blood_type: "A-",
    component: "platelets",
    volume_ml: 320,
    collection_date: "2026-04-09T11:20:00Z",
    expiration_date: "2026-04-16T11:20:00Z",
    status: "reserved",
    created_at: "2026-04-09T11:20:00Z",
    updated_at: "2026-04-11T09:30:00Z",
  },
  {
    id: "sample-3",
    bag_number: "BB-20260411-0003",
    donor_id: "donor-3",
    storage_hospital_id: "central-bank",
    blood_request_id: null,
    blood_type: "B+",
    component: "plasma",
    volume_ml: 250,
    collection_date: "2026-04-08T16:45:00Z",
    expiration_date: "2026-06-01T16:45:00Z",
    status: "tested",
    created_at: "2026-04-08T16:45:00Z",
    updated_at: "2026-04-10T10:15:00Z",
  },
];

const statusClassMap: Record<BloodBagStatus, string> = {
  collected: "bg-slate-100 text-slate-700",
  tested: "bg-blue-100 text-blue-700",
  available: "bg-emerald-100 text-emerald-700",
  reserved: "bg-amber-100 text-amber-700",
  issued: "bg-orange-100 text-orange-700",
  transfused: "bg-cyan-100 text-cyan-700",
  discarded: "bg-neutral-200 text-neutral-700",
  expired: "bg-rose-100 text-rose-700",
};

export function InventoryTable() {
  const [bags, setBags] = useState<BloodBag[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<BloodBagStatus | "">("");
  const [bloodTypeFilter, setBloodTypeFilter] = useState<BloodType | "">("");
  const [sourceLabel, setSourceLabel] = useState("live");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isDegraded, setIsDegraded] = useState(false);
  const [reloadNonce, setReloadNonce] = useState(0);
  const previousDegradedState = useRef(false);

  useEffect(() => {
    const fetchBags = async () => {
      setIsLoading(true);
      setErrorMessage(null);

      try {
        const { data } = await apiClient.get<BloodBag[]>("/inventory/bags", {
          params: {
            status: statusFilter || undefined,
            blood_type: bloodTypeFilter || undefined,
          },
        });
        setBags(data);
        setSourceLabel("live");
        setIsDegraded(false);
      } catch (error) {
        const filtered = SAMPLE_BAGS.filter((item) => {
          const matchesStatus = !statusFilter || item.status === statusFilter;
          const matchesType = !bloodTypeFilter || item.blood_type === bloodTypeFilter;
          return matchesStatus && matchesType;
        });

        setBags(filtered);
        setSourceLabel("sample");
        setIsDegraded(true);
        if (axios.isAxiosError(error)) {
          setErrorMessage(error.response?.data?.detail ?? "Live inventory endpoint is unavailable.");
        } else {
          setErrorMessage("Live inventory endpoint is unavailable.");
        }
      } finally {
        setIsLoading(false);
      }
    };

    void fetchBags();
  }, [bloodTypeFilter, reloadNonce, statusFilter]);

  const retryLiveData = useCallback(() => {
    setReloadNonce((value) => value + 1);
  }, []);

  useEffect(() => {
    if (previousDegradedState.current === isDegraded) {
      return;
    }

    previousDegradedState.current = isDegraded;
    void reportDegradedStateTransition({
      source: "inventory",
      state: isDegraded ? "degraded" : "recovered",
      message: errorMessage ?? undefined,
    });
  }, [errorMessage, isDegraded]);

  const totalVolume = useMemo(() => bags.reduce((sum, bag) => sum + bag.volume_ml, 0), [bags]);

  return (
    <section className="glass-card overflow-hidden">
      <div className="flex flex-col gap-4 border-b border-black/10 p-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-mono uppercase tracking-[0.18em] text-black/50">Inventory</p>
          <h3 className="text-lg font-bold">Blood Bag Stock</h3>
          <p className="text-sm text-black/65">
            {bags.length} records • {totalVolume.toLocaleString()} ml total • source: {sourceLabel}
          </p>
        </div>

        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <select
            className="rounded-lg border border-black/15 bg-white px-3 py-2 text-sm"
            value={bloodTypeFilter}
            onChange={(event) => setBloodTypeFilter(event.target.value as BloodType | "")}
          >
            <option value="">All blood groups</option>
            {BLOOD_TYPES.map((group) => (
              <option key={group} value={group}>
                {group}
              </option>
            ))}
          </select>

          <select
            className="rounded-lg border border-black/15 bg-white px-3 py-2 text-sm"
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value as BloodBagStatus | "")}
          >
            <option value="">All statuses</option>
            {BLOOD_BAG_STATUSES.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>
      </div>

      {isDegraded ? (
        <div className="px-4 pt-4">
          <DegradedStateBanner
            title="Live inventory feed is unavailable"
            message={errorMessage ?? "Showing sample stock records until the API recovers."}
            onRetry={retryLiveData}
            isRetrying={isLoading}
          />
        </div>
      ) : null}

      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-black/[0.03] text-xs uppercase tracking-wide text-black/60">
            <tr>
              <th className="px-4 py-3">Bag</th>
              <th className="px-4 py-3">Group</th>
              <th className="px-4 py-3">Component</th>
              <th className="px-4 py-3">Volume</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Expires</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-black/60">
                  Loading inventory...
                </td>
              </tr>
            ) : bags.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-black/60">
                  No blood bags found for the selected filters.
                </td>
              </tr>
            ) : (
              bags.map((bag) => (
                <tr key={bag.id} className="border-t border-black/10">
                  <td className="px-4 py-3 font-medium">{bag.bag_number}</td>
                  <td className="px-4 py-3">{bag.blood_type}</td>
                  <td className="px-4 py-3 capitalize">{bag.component.split("_").join(" ")}</td>
                  <td className="px-4 py-3">{bag.volume_ml} ml</td>
                  <td className="px-4 py-3">
                    <span className={`pill ${statusClassMap[bag.status]}`}>{bag.status}</span>
                  </td>
                  <td className="px-4 py-3">{new Date(bag.expiration_date).toLocaleDateString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
