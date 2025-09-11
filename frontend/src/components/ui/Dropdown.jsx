import { useState, useRef, useEffect } from "react";

export default function Dropdown({ trigger, children, align = "end", className = "" }) {
  const [open, setOpen] = useState(false);
  const ref = useRef();

  useEffect(() => {
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    if (open) document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open]);

  return (
    <div className="relative" ref={ref}>
      <div onClick={() => setOpen((v) => !v)}>{trigger}</div>
      {open && (
        <div
          className={`absolute z-20 mt-2 min-w-[12rem] bg-white border border-gray-200 rounded shadow-lg ${className} ${
            align === "end" ? "right-0" : ""
          }`}
        >
          {children({ close: () => setOpen(false) })}
        </div>
      )}
    </div>
  );
}