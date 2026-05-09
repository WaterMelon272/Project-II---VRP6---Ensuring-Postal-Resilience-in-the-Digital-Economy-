'use client';

import React, { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// 1. Sửa lỗi mất icon marker mặc định của Leaflet
const icon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

const depotIcon = L.divIcon({
  className: 'depot-marker',
  html: '<div style="background:#dc2626;color:white;border-radius:50%;width:18px;height:18px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:bold;">K</div>',
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

const orderIcon = L.divIcon({
  className: 'order-marker',
  html: '<div style="background:#f59e0b;border:2px solid white;border-radius:50%;width:14px;height:14px;"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

interface LocationPoint {
  id: string;
  lat: number;
  lng: number;
  type?: string;
}

interface MapProps {
  routes?: [number, number][][];
  depots?: LocationPoint[];
  orders?: LocationPoint[];
}

function FitBounds({ points }: { points: [number, number][] }) {
  const map = useMap();

  useEffect(() => {
    if (!map || points.length === 0) return;
    map.invalidateSize();
    map.fitBounds(points, { padding: [40, 40], maxZoom: 16 });
  }, [map, points]);

  return null;
}

export default function Map({ routes = [], depots = [], orders = [] }: MapProps) {
  const defaultCenter: [number, number] = [21.0285, 105.8542]; // Hồ Gươm
  const routeColors = ['#2563eb', '#dc2626', '#16a34a', '#ca8a04', '#9333ea', '#0891b2', '#f59e0b'];

  const fitPoints = useMemo(() => {
    const points: [number, number][] = [];
    depots.forEach((depot) => points.push([depot.lat, depot.lng]));
    orders.forEach((order) => points.push([order.lat, order.lng]));
    routes.forEach((route) => route.forEach((point) => points.push(point as [number, number])));
    return points;
  }, [routes, depots, orders]);

  return (
    <MapContainer
      center={defaultCenter}
      zoom={14}
      style={{ height: '100%', width: '100%', zIndex: 0 }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <FitBounds points={fitPoints} />

      {routes.map((route, index) => (
        route.length > 1 && (
          <React.Fragment key={`route-${index}`}>
            <Polyline
              positions={route}
              color={routeColors[index % routeColors.length]}
              weight={6}
              opacity={0.35}
            />
            <Polyline
              positions={route}
              color={routeColors[index % routeColors.length]}
              weight={3}
            />
          </React.Fragment>
        )
      ))}

      {depots.map((depot) => (
        <Marker key={`depot-${depot.id}`} position={[depot.lat, depot.lng]} icon={depotIcon}>
          <Popup>
            Kho: {depot.id} <br /> {depot.type || 'Kho hàng'}
          </Popup>
        </Marker>
      ))}

      {orders.map((order) => (
        <Marker key={`order-${order.id}`} position={[order.lat, order.lng]} icon={orderIcon}>
          <Popup>
            Đơn {order.id} <br /> Khối lượng: {order.type || 'N/A'}
          </Popup>
        </Marker>
      ))}

      {routes.map((route, index) => (
        route.length > 0 && (
          <Marker
            key={`marker-${index}`}
            position={[route[0][0], route[0][1]]}
            icon={icon}
          >
            <Popup>Điểm xuất phát xe {index + 1}</Popup>
          </Marker>
        )
      ))}
    </MapContainer>
  );
}
