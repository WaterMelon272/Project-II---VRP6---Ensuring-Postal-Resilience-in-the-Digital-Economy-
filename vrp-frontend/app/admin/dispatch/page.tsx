'use client';

import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Package, 
  Car, 
  CheckCircle2, 
  Loader2, 
  Settings2, 
  MapPin, 
  Navigation 
} from 'lucide-react';
import dynamic from 'next/dynamic';

// Import động component Map để tránh lỗi SSR (Server-Side Rendering)
const MapComponent = dynamic(() => import('@/components/Map'), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center bg-gray-100 text-gray-500">
      <Loader2 className="animate-spin mr-2" /> Đang tải bản đồ...
    </div>
  )
});

const VEHICLE_TYPES = [
  { type: 'Xe lớn', max_load: 20 },
  { type: 'Xe vừa', max_load: 12 },
  { type: 'Xe nhỏ', max_load: 6 },
];

interface Warehouse {
  id: string;
  lat: number;
  lng: number;
}

interface Vehicle {
  id: string;
  lat: number;
  lng: number;
  type: string;
  max_load: number;
  warehouse_id: string;
}

interface Order {
  id: string;
  lat: number;
  lng: number;
  demand: number;
}

interface Assignment {
  vehicle_id: string;
  vehicle_type?: string;
  max_load?: number;
  orders: string[];
  route: [number, number][];
}

interface OrderEtaMap {
  [orderId: string]: number;
}

const generateWarehouses = (): Warehouse[] => {
  const baseLat = 21.0285;
  const baseLng = 105.8542;
  return Array.from({ length: 3 }).map((_, index) => ({
    id: `KH-${index + 1}`,
    lat: baseLat + (Math.random() - 0.5) * 0.015,
    lng: baseLng + (Math.random() - 0.5) * 0.015,
  }));
};

const generateVehicles = (warehouses: Warehouse[]): Vehicle[] => {
  return warehouses.flatMap((warehouse, warehouseIndex) =>
    Array.from({ length: 5 }).map((_, vehicleIndex) => {
      const typeInfo = VEHICLE_TYPES[Math.floor(Math.random() * VEHICLE_TYPES.length)];
      return {
        id: `XE-${(warehouseIndex * 5 + vehicleIndex + 1).toString().padStart(2, '0')}`,
        lat: warehouse.lat + (Math.random() - 0.5) * 0.0025,
        lng: warehouse.lng + (Math.random() - 0.5) * 0.0025,
        type: typeInfo.type,
        max_load: typeInfo.max_load,
        warehouse_id: warehouse.id,
      };
    })
  );
};

const generateOrders = (count: number): Order[] => {
  const baseLat = 21.0285;
  const baseLng = 105.8542;
  return Array.from({ length: count }).map((_, index) => ({
    id: `DH-${index + 1}`,
    lat: baseLat + (Math.random() - 0.5) * 0.04,
    lng: baseLng + (Math.random() - 0.5) * 0.04,
    demand: Math.ceil(Math.random() * 4) + 1,
  }));
};

const BACKEND_BASE = 'http://localhost:8000';

export default function DispatchPage() {
  // States
  const [hasMounted, setHasMounted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [algorithm, setAlgorithm] = useState('GA');
  const [orderCount, setOrderCount] = useState(12);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [results, setResults] = useState<Assignment[]>([]);
  const [orderEtas, setOrderEtas] = useState<OrderEtaMap>({});
  const [selectedVehicleId, setSelectedVehicleId] = useState<string>('');

  const filteredResults = selectedVehicleId
    ? results.filter((res) => res.vehicle_id.toLowerCase() === selectedVehicleId.trim().toLowerCase())
    : results;

  const setupRandomData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_BASE}/api/seed-data`);
      const data = await response.json();
      setWarehouses(data.warehouses || []);
      setVehicles(data.vehicles || []);
      setOrders(generateOrders(orderCount));
      setResults([]);
      setOrderEtas({});
    } catch (error) {
      console.error('Seed data error:', error);
      alert('Không lấy được dữ liệu từ backend. Hãy kiểm tra server backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setHasMounted(true);
    setupRandomData();
  }, []);

  const handleDispatch = async () => {
    if (orders.length === 0 || vehicles.length === 0) return;
    
    setLoading(true);
    try {
      const endpoint = algorithm === 'Exact' ? '/api/dispatch/exact' : '/api/dispatch/ga';
      const response = await fetch(`${BACKEND_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vehicles: vehicles,
          orders: orders,
        }),
      });

      const data = await response.json();
      if (data.status === 'success') {
        setResults(data.assignments);
        setOrderEtas(data.order_eta_hours || {});
      } else {
        alert("Lỗi từ Backend: " + (data.detail || 'Không xác định'));
      }
    } catch (error) {
      console.error("Dispatch Error:", error);
      alert("Không thể kết nối tới Backend. Hãy đảm bảo FastAPI đang chạy.");
    } finally {
      setLoading(false);
    }
  };

  // Trả về null nếu chưa mount để tránh lỗi Hydration
  if (!hasMounted) return null;

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8 font-sans text-slate-900">
      {/* HEADER & CONTROLS */}
      <header className="max-w-[1600px] mx-auto flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-800">
            Trung tâm Điều phối
          </h1>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center gap-3 bg-white p-3 rounded-2xl shadow-sm border border-slate-200">
          <div className="flex items-center gap-2 px-3 border-b border-slate-200 pb-3 sm:border-b-0 sm:border-r sm:pb-0">
            <Settings2 size={18} className="text-slate-400" />
            <span className="text-sm font-semibold text-slate-600">Thuật toán:</span>
          </div>
          <select 
            value={algorithm}
            onChange={(e) => setAlgorithm(e.target.value)}
            className="bg-transparent text-sm font-bold text-blue-600 focus:outline-none cursor-pointer"
          >
            <option value="GA">Genetic Algorithm (GA)</option>
            <option value="Exact">DP Bitmask</option>
          </select>
          <div className="flex items-center gap-2 px-3">
            <label htmlFor="orderCount" className="text-sm font-semibold text-slate-600">Số đơn:</label>
            <input
              id="orderCount"
              type="number"
              min={1}
              max={50}
              value={orderCount}
              onChange={(e) => setOrderCount(Math.max(1, Math.min(50, Number(e.target.value))))}
              className="w-20 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
          </div>
          <button 
            onClick={handleDispatch}
            disabled={loading}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-6 py-2.5 rounded-xl transition-all shadow-lg shadow-blue-200 font-bold"
          >
            {loading ? <Loader2 className="animate-spin" size={20} /> : <Play size={20} />}
            {loading ? 'Đang tính toán...' : 'Chạy điều phối'}
          </button>
          <button
            onClick={setupRandomData}
            disabled={loading}
            className="flex items-center justify-center bg-slate-50 hover:bg-slate-100 text-slate-700 px-5 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold"
          >
            Tạo dữ liệu mới
          </button>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedVehicleId('')}
              disabled={loading}
              className={`px-4 py-2 rounded-2xl text-sm font-semibold ${selectedVehicleId === '' ? 'bg-blue-600 text-white' : 'bg-slate-50 text-slate-700 hover:bg-slate-100'}`}
            >
              Hiển thị tất cả
            </button>
          </div>
        </div>
      </header>

      {/* MAIN CONTENT GRID */}
      <main className="max-w-[1600px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* COLUMN 1: PENDING ORDERS (3/12) */}
        <section className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between px-2">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <Package className="text-amber-500" size={20} />
              Đơn hàng chờ
            </h2>
            <span className="bg-amber-100 text-amber-700 text-xs font-bold px-2.5 py-0.5 rounded-full">
              {orders.length} đơn
            </span>
          </div>
          
          <div className="space-y-3 overflow-y-auto max-h-[700px] pr-2 custom-scrollbar">
            {orders.map((o) => (
              <div key={o.id} className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 hover:border-blue-300 transition-colors">
                <div className="flex justify-between items-start">
                  <span className="font-bold text-slate-700">{o.id}</span>
                  <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400">
                    {orderEtas[o.id] !== undefined ? `${orderEtas[o.id].toFixed(1)} giờ` : 'Chờ lấy'}
                  </span>
                </div>
                <div className="flex flex-wrap gap-2 mt-2 text-xs text-slate-500">
                  <span className="flex items-center gap-1">
                    <MapPin size={12} />
                    {o.lat.toFixed(4)}, {o.lng.toFixed(4)}
                  </span>
                  <span className="uppercase font-semibold text-amber-600">KL: {o.demand}kg</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* COLUMN 2: ASSIGNMENTS (3/12) */}
        <section className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between px-2">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <CheckCircle2 className="text-green-500" size={20} />
              Phân bổ xe
            </h2>
          </div>

          <div className="space-y-4 overflow-y-auto max-h-[700px] pr-2 custom-scrollbar">
            {results.length === 0 && !loading && (
              <div className="text-center py-10 border-2 border-dashed border-slate-200 rounded-2xl text-slate-400 text-sm italic">
                Chưa có kết quả điều phối
              </div>
            )}

            {results.map((res, idx) => (
              <div
                key={idx}
                onClick={() => setSelectedVehicleId(res.vehicle_id)}
                className={`cursor-pointer ${selectedVehicleId.toLowerCase() === res.vehicle_id.toLowerCase() ? 'ring-2 ring-blue-500 shadow-lg' : ''} bg-white rounded-2xl shadow-md border border-slate-100 overflow-hidden transition-all hover:border-blue-300`}
              >
                <div className="bg-slate-50 px-4 py-3 border-b border-slate-100 flex items-center gap-3">
                  <div className="p-2 bg-blue-600 rounded-lg text-white">
                    <Car size={18} />
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 font-medium uppercase">Tài xế</p>
                    <p className="font-bold text-slate-800">{res.vehicle_id}</p>
                    <p className="text-[11px] text-slate-500 mt-1">Loại xe: {res.vehicle_type || 'Không xác định'}</p>
                    <p className="text-[11px] text-slate-500">Tải tối đa: {res.max_load || 0} kg</p>
                  </div>
                </div>
                <div className="p-4 space-y-3">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-tight">Danh sách đơn hàng:</p>
                  {res.orders.length > 0 ? (
                    res.orders.map((orderId, i) => (
                      <div key={i} className="flex items-center gap-3 text-sm text-slate-700 font-medium">
                        <span className="flex items-center justify-center w-5 h-5 rounded-full bg-blue-50 text-blue-600 text-[10px]">
                          {i + 1}
                        </span>
                        {orderId}
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-slate-400 italic">Không có đơn hàng</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* COLUMN 3: MAP VIEW (6/12) */}
        <section className="lg:col-span-6 h-[600px] lg:h-auto">
          <div className="bg-white rounded-3xl shadow-xl border border-slate-200 overflow-hidden h-full flex flex-col">
            <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-white">
              <div className="flex items-center gap-2">
                <Navigation className="text-blue-600" size={20} />
                <h2 className="font-bold text-slate-800">Lộ trình thời gian thực</h2>
              </div>
              <div className="flex flex-wrap gap-2">
                {filteredResults.map((res, idx) => (
                  <div key={idx} className="flex items-center gap-1.5">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: ['#2563eb', '#dc2626', '#16a34a', '#ca8a04', '#9333ea'][idx % 5] }}
                    />
                    <span className="text-[10px] font-bold text-slate-500 uppercase">{res.vehicle_id}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="flex-1 relative">
              <MapComponent 
                routes={filteredResults.length > 0 ? filteredResults.map((r) => r.route) : results.map((r) => r.route)}
                depots={warehouses.map((warehouse) => ({
                  id: warehouse.id,
                  lat: warehouse.lat,
                  lng: warehouse.lng,
                  type: 'Kho hàng',
                }))}
                orders={orders.map((order) => ({
                  id: order.id,
                  lat: order.lat,
                  lng: order.lng,
                  type: `${order.demand}kg`,
                }))}
              />
            </div>
          </div>
        </section>

      </main>
    </div>
  );
}