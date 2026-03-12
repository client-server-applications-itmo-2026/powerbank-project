import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, Tooltip, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useGeolocation } from '../shared/hooks/useGeolocation';
import { useStations } from '../shared/hooks/useStations';
import { StartRentalDrawer } from '../features/StartRentalDrawer';
import { CompleteRentalFlow } from '../features/CompleteRentalFlow';
import { AppLayout } from '../shared/ui/AppLayout';
import { ROUTES } from '../shared/constants/routes';
import type { RetrieveNearestStantionsResponseItem, RentalSchema } from '../shared/types/api';
import styles from './MapPage.module.css';

// Fix default Leaflet icon paths broken by bundlers
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom icons
const userIcon = L.divIcon({
  className: '',
  html: `<div class="user-marker"></div>`,
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

function stationIcon(available: boolean) {
  return L.divIcon({
    className: '',
    html: `<div class="station-marker ${available ? 'station-available' : 'station-empty'}">
             <span>${available ? '⚡' : '○'}</span>
           </div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -20],
  });
}

interface RentalSuccessBannerProps {
  rental: RentalSchema;
  onDismiss: () => void;
}

function RentalSuccessBanner({ rental, onDismiss }: RentalSuccessBannerProps) {
  return (
    <div className={styles.rentalBanner}>
      <div className={styles.rentalBannerContent}>
        <span>✅ Аренда #{rental.id} началась! Батарея: {rental.battery_id}</span>
        <button className={styles.bannerClose} onClick={onDismiss}>✕</button>
      </div>
    </div>
  );
}

export function MapPage() {
  const location = useLocation();
  const navigate = useNavigate();
  // Set when user navigates here from RentalsPage to return a battery
  const completingRental = (location.state as { completingRental?: RentalSchema } | null)?.completingRental ?? null;

  const { lat, lon, error: geoError, loading: geoLoading } = useGeolocation();
  const { stations, loading: stationsLoading, error: stationsError, refetch } = useStations({
    lat,
    lon,
    radius_meters: 5000,
    enabled: lat != null && lon != null,
  });

  const [selectedStation, setSelectedStation] = useState<RetrieveNearestStantionsResponseItem | null>(null);
  const [completingStation, setCompletingStation] = useState<RetrieveNearestStantionsResponseItem | null>(null);
  const [activeRental, setActiveRental] = useState<RentalSchema | null>(null);
  const [didRecenter, setDidRecenter] = useState(false);

  const mapCenter: [number, number] = lat != null && lon != null ? [lat, lon] : [55.7558, 37.6176];

  function handleStationClick(station: RetrieveNearestStantionsResponseItem) {
    if (completingRental) {
      setCompletingStation(station);
    } else {
      setSelectedStation(station);
    }
  }

  function handleRentalSuccess(rental: RentalSchema) {
    setActiveRental(rental);
    setSelectedStation(null);
    refetch();
  }

  return (
    <AppLayout>
      <div className={styles.page}>
        {/* Return mode banner */}
        {completingRental && (
          <div className={styles.returnBanner}>
            <span>📍 Выберите станцию для возврата батарейки</span>
            <button className={styles.returnBannerCancel} onClick={() => navigate(ROUTES.RENTALS)}>
              Отмена
            </button>
          </div>
        )}

        {activeRental && (
          <RentalSuccessBanner rental={activeRental} onDismiss={() => setActiveRental(null)} />
        )}

        {/* Status bar */}
        <div className={styles.statusBar}>
          {geoLoading && <span className={styles.statusChip}>📍 Определяем местоположение…</span>}
          {geoError && <span className={styles.statusChipWarn}>⚠️ {geoError}</span>}
          {stationsLoading && <span className={styles.statusChip}>Загрузка станций…</span>}
          {stationsError && <span className={styles.statusChipWarn}>{stationsError}</span>}
          {!stationsLoading && !stationsError && (
            <span className={styles.statusChip}>
              {stations.length} станций в радиусе 5 км
            </span>
          )}
          <button className={styles.refreshBtn} onClick={refetch} title="Обновить">
            ↻
          </button>
        </div>

        <MapContainer
          center={mapCenter}
          zoom={14}
          className={styles.map}
          zoomControl={true}
        >
          {/* Recenter once when geolocation resolves */}
          {lat != null && lon != null && !didRecenter && (
            <RecenterOnce lat={lat} lon={lon} onDone={() => setDidRecenter(true)} />
          )}

          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            subdomains="abcd"
            maxZoom={20}
          />

          {/* User location */}
          {lat != null && lon != null && (
            <Marker position={[lat, lon]} icon={userIcon}>
              <Popup>Вы здесь</Popup>
            </Marker>
          )}

          {/* Stations */}
          {stations.map((station) => (
            <Marker
              key={station.hardware_id}
              position={[station.location.lat, station.location.lon]}
              icon={stationIcon(station.available_batteries > 0)}
              eventHandlers={{
                click: () => handleStationClick(station),
              }}
            >
              <Tooltip direction="top" offset={[0, -20]} opacity={1}>
                <div className={styles.popupContent}>
                  <strong>{station.hardware_id}</strong>
                  <br />
                  ⚡ {station.available_batteries} батарей · 🔌 {station.free_slots} слотов
                  {completingRental ? (
                    <span className={styles.tooltipHint}>Нажмите, чтобы вернуть сюда</span>
                  ) : station.available_batteries > 0 ? (
                    <span className={styles.tooltipHint}>Нажмите, чтобы арендовать</span>
                  ) : null}
                </div>
              </Tooltip>
            </Marker>
          ))}
        </MapContainer>

        <StartRentalDrawer
          station={selectedStation}
          onClose={() => setSelectedStation(null)}
          onSuccess={handleRentalSuccess}
        />

        {completingRental && completingStation && (
          <CompleteRentalFlow
            rental={completingRental}
            preselectedStantionId={completingStation.hardware_id}
            onClose={() => setCompletingStation(null)}
            onCompleted={() => navigate(ROUTES.RENTALS)}
          />
        )}
      </div>
    </AppLayout>
  );
}

// Recenter map once, then call onDone to prevent infinite re-renders
function RecenterOnce({ lat, lon, onDone }: { lat: number; lon: number; onDone: () => void }) {
  const map = useMap();
  map.setView([lat, lon], 15);
  // call onDone via microtask to avoid state update during render
  Promise.resolve().then(onDone);
  return null;
}


