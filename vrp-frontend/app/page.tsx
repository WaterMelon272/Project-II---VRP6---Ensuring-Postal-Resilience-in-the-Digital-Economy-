import Link from 'next/link';
export default function Home() {
  return (
    <div className="flex h-screen items-center justify-center gap-10">
      <Link href="/user" className="p-10 bg-blue-500 text-white rounded-xl">Vào trang Khách hàng</Link>
      <Link href="/admin/dashboard" className="p-10 bg-red-500 text-white rounded-xl">Vào trang Quản lý</Link>
    </div>
  );
}