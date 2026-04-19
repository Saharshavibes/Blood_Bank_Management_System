import { type InputHTMLAttributes } from "react";

type TextFieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  helperText?: string;
};

export function TextField({ label, helperText, className = "", ...props }: TextFieldProps) {
  return (
    <label className="block space-y-1.5">
      <span className="text-sm font-medium text-black/80">{label}</span>
      <input
        className={`w-full rounded-xl border border-black/15 bg-white px-3 py-2.5 text-sm outline-none transition focus:border-calm focus:ring-2 focus:ring-calm/20 ${className}`.trim()}
        {...props}
      />
      {helperText ? <span className="text-xs text-black/55">{helperText}</span> : null}
    </label>
  );
}
