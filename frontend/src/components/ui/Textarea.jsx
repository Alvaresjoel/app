export default function Textarea({ className = "", ...props }) {
  return (
    <textarea
      className={`border rounded px-3 py-2 w-full text-sm focus:ring-2 focus:ring-primary/40 ${className}`}
      {...props}
    />
  );
}