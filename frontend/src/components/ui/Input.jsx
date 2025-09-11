export default function Input({ className = "",htmlFor, label, ...props }) {
  return (
  <>
    <label htmlFor={htmlFor} className="block text-sm font-medium text-gray-700">
      {label}
    </label>
    <input
      className={`border rounded px-3 py-2 w-full text-sm focus:ring-2 focus:ring-primary/40 ${className}`}
      {...props}
    />
  </>
  );
}