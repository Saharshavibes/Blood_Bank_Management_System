import { useMemo } from "react";

import L, { type LatLngTuple } from "leaflet";
import { MapContainer, Marker, Polyline, Popup, TileLayer } from "react-leaflet";

import type { RoutingCandidate, RoutingHospitalPoint } from "@/types/routing";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

const defaultMarkerIcon = L.icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41],
});

type UrgentRoutingMapProps = {
  requestingHospital: RoutingHospitalPoint;
  candidates: RoutingCandidate[];
  selectedSourceHospitalId: string | null;
};

export function UrgentRoutingMap({
  requestingHospital,
  candidates,
  selectedSourceHospitalId,
}: UrgentRoutingMapProps) {
  const selectedCandidate = candidates.find((candidate) => candidate.source_hospital_id === selectedSourceHospitalId) ?? null;

  const requestingPosition = useMemo<LatLngTuple>(
    () => [requestingHospital.latitude, requestingHospital.longitude],
    [requestingHospital.latitude, requestingHospital.longitude],
  );

  const center = useMemo<LatLngTuple>(() => {
    if (!selectedCandidate) {
      return requestingPosition;
    }

    return [
      (requestingHospital.latitude + selectedCandidate.latitude) / 2,
      (requestingHospital.longitude + selectedCandidate.longitude) / 2,
    ];
  }, [requestingHospital.latitude, requestingHospital.longitude, requestingPosition, selectedCandidate]);

  return (
    <section className="glass-card overflow-hidden">
      <div className="border-b border-black/10 p-4">
        <h3 className="text-lg font-bold">Nearest Source Routing Map</h3>
        <p className="mt-1 text-sm text-black/65">
          A straight-line emergency path is drawn from requester to selected source hospital.
        </p>
      </div>

      <div className="h-[360px] w-full">
        <MapContainer center={center} zoom={9} scrollWheelZoom className="h-full w-full">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <Marker
            position={requestingPosition}
            icon={defaultMarkerIcon}
          >
            <Popup>
              <strong>Requesting Hospital</strong>
              <br />
              {requestingHospital.hospital_name}
              <br />
              {requestingHospital.city}
            </Popup>
          </Marker>

          {candidates.map((candidate) => (
            <Marker
              key={candidate.source_hospital_id}
              position={[candidate.latitude, candidate.longitude] as LatLngTuple}
              icon={defaultMarkerIcon}
            >
              <Popup>
                <strong>{candidate.source_hospital_name}</strong>
                <br />
                {candidate.source_city}
                <br />
                {candidate.distance_km} km away
              </Popup>
            </Marker>
          ))}

          {selectedCandidate ? (
            <Polyline
              positions={[
                requestingPosition,
                [selectedCandidate.latitude, selectedCandidate.longitude] as LatLngTuple,
              ]}
              pathOptions={{ color: "#ef4444", weight: 4 }}
            />
          ) : null}
        </MapContainer>
      </div>
    </section>
  );
}
