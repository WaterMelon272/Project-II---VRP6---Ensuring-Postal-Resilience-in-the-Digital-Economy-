'use client';

import React from 'react';
import { Truck, CheckCircle, AlertCircle, TrendingUp, Star } from 'lucide-react';
import dynamic from 'next/dynamic';

const MapComponent = dynamic(() => import('@/components/Map'), { ssr: false });

export default function AdminDashboard() {
  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard icon={<CheckCircle className="text-green-500"/>} title="Đơn hoàn thành" value="1,284" sub="+12% so với tháng trước" />
        <StatCard icon={<TrendingUp className="text-blue-500"/>} title="Doanh thu" value="450M VNĐ" sub="+5% so với hôm qua" />
        <StatCard icon={<AlertCircle className="text-red-500"/>} title="Giao trễ" value="24" sub="Cần xử lý ngay" />
        <StatCard icon={<Star className="text-yellow-500"/>} title="Đánh giá TB" value="4.8/5" sub="Từ 200 tài xế" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Section */}
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Truck size={20} /> Vị trí các xe đang giao hàng
          </h2>
          <div className="h-[500px] bg-gray-100 rounded-xl overflow-hidden relative">
            <MapComponent />
            {/* Giả lập các icon xe trên map */}
            <div className="absolute top-10 left-20 animate-bounce"><Truck className="text-blue-600" /></div>
            <div className="absolute bottom-20 right-40 animate-pulse"><Truck className="text-red-600" /></div>
          </div>
        </div>

        {/* Charts Placeholder Section */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 h-full">
            <h2 className="text-lg font-bold mb-4">Biểu đồ tăng trưởng</h2>
            <div className="flex flex-col items-center justify-center h-64 text-gray-400 border-2 border-dashed rounded-xl">
              [ Biểu đồ Doanh thu / Lợi nhuận ]
            </div>
            <div className="mt-6 flex flex-col items-center justify-center h-64 text-gray-400 border-2 border-dashed rounded-xl">
              [ Biểu đồ Tỷ lệ giao hàng ]
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, title, value, sub }: any) {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
      <div className="flex items-center gap-4 mb-3">
        <div className="p-2 bg-gray-50 rounded-lg">{icon}</div>
        <span className="text-gray-500 font-medium">{title}</span>
      </div>
      <div className="text-2xl font-bold text-gray-800">{value}</div>
      <div className="text-xs text-gray-400 mt-1">{sub}</div>
    </div>
  );
}