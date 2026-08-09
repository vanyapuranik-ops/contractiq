export default function Navbar() {
  return (
    <nav className="w-full bg-white border-b border-gray-100 px-8 py-4 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <span className="text-white text-sm font-bold">C</span>
        </div>
        <span className="text-lg font-semibold text-gray-900 tracking-tight">ContractIQ</span>
      </div>
      <div className="flex items-center gap-6">
        <span className="text-sm text-gray-400 hidden md:block">AI Contract Intelligence</span>
        <div className="w-2 h-2 rounded-full bg-green-400"></div>
      </div>
    </nav>
  )
}
