'use client';

import React, { useState } from 'react';
import { Search, Package, Truck, MapPin, CheckCircle, Clock, ChevronRight } from 'lucide-react';
import dynamic from 'next/dynamic';

const MapComponent = dynamic(() => import('@/components/Map'), {
  ssr: false,
  loading: () => <div className="flex h-full items-center justify-center bg-gray-50 text-gray-500">Đang tải bản đồ...</div>
});

// Dữ liệu giả (Dummy Data)
const DUMMY_ORDERS = Array.from({ length: 10 }).map((_, i) => ({
  id: `VN${123456 + i}`,
  status: i < 5 ? 'Đang giao' : i < 7 ? 'Đã giao' : 'Đã hủy',
  eta: '10:15 AM',
  date: '15/04/2026',
  timeline: [
    { title: 'Đang giao hàng', desc: 'Tài xế đang đến', time: '08:30 AM', icon: <Truck size={16}/>, color: 'bg-blue-500' },
    { title: 'Đã đến trạm', desc: 'Bưu cục Hà Nội', time: '22:00 PM', icon: <Package size={16}/>, color: 'bg-gray-300' },
  ]
}));

export default function UserPage() {
  const [activeTab, setActiveTab] = useState('Tất cả');
  const [selectedOrder, setSelectedOrder] = useState<any>(null);

  const tabs = ['Tất cả', 'Đang giao', 'Đã giao', 'Đã hủy', 'Đánh giá'];

  // Lọc đơn hàng theo tab
  const filteredOrders = DUMMY_ORDERS.filter(order => 
    activeTab === 'Tất cả' || order.status === activeTab
  );

  // Nếu đã chọn 1 đơn hàng cụ thể, hiện giao diện chi tiết (Code cũ của bạn)
  if (selectedOrder) {
    return (
      <div className="min-h-screen bg-gray-50">
        <button 
          onClick={() => setSelectedOrder(null)}
          className="m-4 text-blue-600 flex items-center gap-2 hover:underline"
        >
          ← Quay lại danh sách
        </button>
        <main className="max-w-6xl mx-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-500">
            <div className="lg:col-span-1 space-y-6">
              <div className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-l-blue-500">
                <div className="flex items-center gap-3 mb-2">
                  <Clock className="text-blue-500" size={24} />
                  <h3 className="text-lg font-semibold text-gray-700">Thời gian đến dự kiến (ETA)</h3>
                </div>
                <p className="text-3xl font-bold text-blue-600">{selectedOrder.eta}</p>
                <p className="text-sm text-gray-500 mt-1">{selectedOrder.date}</p>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h3 className="text-lg font-semibold text-gray-800 mb-6">Lộ trình bưu kiện</h3>
                <div className="relative border-l-2 border-gray-200 ml-3 space-y-8">
                  {selectedOrder.timeline.map((step: any, idx: number) => (
                    <div key={idx} className="relative">
                      <div className={`absolute -left-3.5 ${step.color} p-1 rounded-full text-white ring-4 ring-white`}>
                        {step.icon}
                      </div>
                      <div className="pl-6">
                        <h4 className="font-bold text-gray-800">{step.title}</h4>
                        <p className="text-sm text-gray-500">{step.desc}</p>
                        <span className="text-xs font-semibold text-blue-600 mt-1 block">{step.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col h-[500px]">
              <div className="p-4 border-b border-gray-100 flex items-center gap-2">
                <MapPin className="text-red-500" size={20} />
                <h3 className="font-semibold text-gray-800">Vị trí trực quan</h3>
              </div>
              <div className="flex-1 relative"><MapComponent /></div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-blue-600 text-white p-4 shadow-md">
        <div className="max-w-6xl mx-auto flex items-center gap-2">
          <Package size={28} />
          <h1 className="text-2xl font-bold">Hanoi Post</h1>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-6">
        {/* Tabs Navigation */}
        <div className="flex gap-4 mb-8 overflow-x-auto pb-2">
          {tabs.map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-2 rounded-full whitespace-nowrap transition-all ${
                activeTab === tab ? 'bg-blue-600 text-white shadow-md' : 'bg-white text-gray-600 hover:bg-gray-100'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Order List */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredOrders.slice(0, activeTab === 'Đang giao' ? 5 : filteredOrders.length).map(order => (
            <div 
              key={order.id}
              onClick={() => setSelectedOrder(order)}
              className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:border-blue-300 cursor-pointer transition-all group"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
                  <Package size={24} />
                </div>
                <span className="text-xs font-medium px-2 py-1 bg-gray-100 rounded text-gray-500">
                  {order.status}
                </span>
              </div>
              <h3 className="font-bold text-gray-800 text-lg">{order.id}</h3>
              <p className="text-sm text-gray-500 mb-4">Dự kiến: {order.eta}</p>
              <div className="flex items-center text-blue-600 text-sm font-semibold group-hover:gap-2 transition-all">
                Xem chi tiết <ChevronRight size={16} />
              </div>
            </div>
          ))}
        </div>

        {/* Nút xem tất cả cho tab Đang giao */}
        {activeTab === 'Đang giao' && filteredOrders.length > 5 && (
          <div className="mt-8 text-center">
            <button className="bg-white border border-blue-600 text-blue-600 px-8 py-2 rounded-lg hover:bg-blue-50">
              Xem tất cả đơn đang giao
            </button>
          </div>
        )}
      </main>
    </div>
  );
}