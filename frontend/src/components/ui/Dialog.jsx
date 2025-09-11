export default function Dialog({ open, onOpenChange, children }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-md relative">
        {children}
        <button
          className="absolute top-2 right-2 text-gray-400 hover:text-gray-600"
          onClick={() => onOpenChange(false)}
          aria-label="Close"
        >
          ×
        </button>
      </div>
    </div>
  );
}