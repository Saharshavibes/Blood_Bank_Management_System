import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import axios from "axios";

import { UrgentRoutingMap } from "@/components/maps/UrgentRoutingMap";
import { Button } from "@/components/ui/Button";
import { DegradedStateBanner } from "@/components/ui/DegradedStateBanner";
import { TextField } from "@/components/ui/TextField";
import { fetchNearestBanksForRequest } from "@/services/routing";
import { reportDegradedStateTransition } from "@/services/telemetry";
import type { RoutingRecommendationResponse } from "@/types/routing";

export function HospitalUrgentPage() {
  const [requestId, setRequestId] = useState("");
  const [result, setResult] = useState<RoutingRecommendationResponse | null>(null);
  const [selectedSourceHospitalId, setSelectedSourceHospitalId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDegraded, setIsDegraded] = useState(false);
  const [lastLookupRequestId, setLastLookupRequestId] = useState<string | null>(null);
  const previousDegradedState = useRef(false);

  const selectedCandidate = useMemo(
    () => result?.candidates.find((item) => item.source_hospital_id === selectedSourceHospitalId) ?? null,
    [result?.candidates, selectedSourceHospitalId],
  );

  const runLookup = useCallback(async (lookupRequestId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchNearestBanksForRequest(lookupRequestId);
      setResult(data);
      setSelectedSourceHospitalId(data.candidates[0]?.source_hospital_id ?? null);
      setIsDegraded(false);
      setLastLookupRequestId(lookupRequestId);
    } catch (lookupError) {
      setResult(null);
      setSelectedSourceHospitalId(null);
      setIsDegraded(true);
      setLastLookupRequestId(lookupRequestId);
      if (axios.isAxiosError(lookupError)) {
        setError(lookupError.response?.data?.detail ?? "Unable to fetch nearest banks.");
      } else {
        setError("Unable to fetch nearest banks.");
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleFindNearest = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const normalizedRequestId = requestId.trim();
    if (!normalizedRequestId) {
      setError("Request ID is required.");
      return;
    }

    void runLookup(normalizedRequestId);
  };

  const retryLookup = useCallback(() => {
    if (!lastLookupRequestId) {
      return;
    }
    void runLookup(lastLookupRequestId);
  }, [lastLookupRequestId, runLookup]);

  useEffect(() => {
    if (previousDegradedState.current === isDegraded) {
      return;
    }

    previousDegradedState.current = isDegraded;
    void reportDegradedStateTransition({
      source: "urgent_routing",
      state: isDegraded ? "degraded" : "recovered",
      message: error ?? undefined,
    });
  }, [error, isDegraded]);

  return (
    <div className="space-y-5">
      <section className="glass-card p-6">
        <h2 className="text-xl font-bold">Urgent Demand Routing</h2>
        <p className="mt-2 text-sm text-black/65">
          Enter an urgent request ID to locate the nearest hospitals with available matching stock.
        </p>

        <form className="mt-4 flex flex-col gap-3 sm:flex-row" onSubmit={handleFindNearest}>
          <TextField
            label="Urgent request ID"
            placeholder="e.g. f8f6d880-a3d8-42d8-8d03-042d5e87a497"
            value={requestId}
            onChange={(event) => setRequestId(event.target.value)}
            className="sm:min-w-[420px]"
          />
          <div className="self-end">
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Finding routes..." : "Find nearest blood banks"}
            </Button>
          </div>
        </form>

        {isDegraded ? (
          <div className="mt-3">
            <DegradedStateBanner
              title="Routing recommendations are temporarily degraded"
              message={error ?? "Live nearest-bank recommendations are unavailable."}
              onRetry={lastLookupRequestId ? retryLookup : undefined}
              isRetrying={isLoading}
            />
          </div>
        ) : error ? (
          <p className="mt-3 text-sm text-rose-600">{error}</p>
        ) : null}
      </section>

      {result ? (
        <>
          <section className="glass-card p-5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="pill bg-rose-100 text-rose-700">{result.urgency}</span>
              <span className="pill bg-black/10 text-black/70">Request {result.request_number}</span>
              <span className="pill bg-calm/15 text-calm">Units requested: {result.units_requested}</span>
            </div>
            <p className="mt-3 text-sm text-black/70">
              Requester: {result.requesting_hospital.hospital_name}, {result.requesting_hospital.city}
            </p>
          </section>

          <section className="glass-card overflow-hidden">
            <div className="border-b border-black/10 p-4">
              <h3 className="text-lg font-bold">Nearest Source List</h3>
              <p className="text-sm text-black/65">Click a row to update route preview on the map.</p>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-black/[0.03] text-xs uppercase tracking-wide text-black/60">
                  <tr>
                    <th className="px-4 py-3">Hospital</th>
                    <th className="px-4 py-3">City</th>
                    <th className="px-4 py-3">Distance</th>
                    <th className="px-4 py-3">Available Units</th>
                    <th className="px-4 py-3">Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {result.candidates.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-4 py-6 text-center text-black/60">
                        No matching available stock found.
                      </td>
                    </tr>
                  ) : (
                    result.candidates.map((candidate) => {
                      const isSelected = candidate.source_hospital_id === selectedSourceHospitalId;
                      return (
                        <tr
                          key={candidate.source_hospital_id}
                          className={`cursor-pointer border-t border-black/10 ${isSelected ? "bg-calm/10" : "bg-white"}`}
                          onClick={() => setSelectedSourceHospitalId(candidate.source_hospital_id)}
                        >
                          <td className="px-4 py-3 font-medium">{candidate.source_hospital_name}</td>
                          <td className="px-4 py-3">{candidate.source_city}</td>
                          <td className="px-4 py-3">{candidate.distance_km} km</td>
                          <td className="px-4 py-3">{candidate.available_units}</td>
                          <td className="px-4 py-3">{candidate.available_volume_ml} ml</td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {result.candidates.length > 0 ? (
            <UrgentRoutingMap
              requestingHospital={result.requesting_hospital}
              candidates={result.candidates}
              selectedSourceHospitalId={selectedSourceHospitalId}
            />
          ) : null}

          {selectedCandidate ? (
            <section className="glass-card p-5">
              <h3 className="text-lg font-bold">Selected Route Summary</h3>
              <p className="mt-2 text-sm text-black/70">
                {selectedCandidate.source_hospital_name} ({selectedCandidate.source_city}) is {selectedCandidate.distance_km} km away with {" "}
                {selectedCandidate.available_units} matching units.
              </p>
            </section>
          ) : null}
        </>
      ) : null}
    </div>
  );
}
