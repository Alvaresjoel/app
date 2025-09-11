export default function Select({ value, onChange, options, placeholder, ...props }) {
  return (
    <select
      className="border rounded px-3 py-2 w-full text-sm focus:ring-2 focus:ring-primary/40"
      value={value}
      {...props}
      onChange={e => onChange(e.target.value)}
    >
      <option value="" disabled>
        {placeholder}
      </option>
      {options.map(opt => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}