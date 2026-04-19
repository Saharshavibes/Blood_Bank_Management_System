import { type ButtonHTMLAttributes, type PropsWithChildren } from "react";

type Variant = "solid" | "ghost" | "outline";

type ButtonProps = PropsWithChildren<
  ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: Variant;
    fullWidth?: boolean;
  }
>;

const baseClass =
  "inline-flex items-center justify-center rounded-xl px-4 py-2.5 text-sm font-semibold transition duration-200 disabled:cursor-not-allowed disabled:opacity-50";

const variantClass: Record<Variant, string> = {
  solid: "bg-ink text-white hover:bg-black",
  ghost: "bg-transparent text-ink hover:bg-black/5",
  outline: "border border-black/20 bg-white text-ink hover:border-black/40",
};

export function Button({
  children,
  className = "",
  variant = "solid",
  fullWidth = false,
  ...props
}: ButtonProps) {
  return (
    <button
      className={`${baseClass} ${variantClass[variant]} ${fullWidth ? "w-full" : ""} ${className}`.trim()}
      {...props}
    >
      {children}
    </button>
  );
}
