import type { InputHTMLAttributes } from "react";

/**
 * FormField — Reusable form field with label and error display.
 *
 * Props:
 * - label: string
 * - error?: string
 * - ...rest: standard input attributes
 */

interface FormFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export function FormField({ label, error, id, ...props }: FormFieldProps) {
  return (
    <div>
      <label htmlFor={id}>{label}</label>
      <input id={id} {...props} />
      {error && <span role="alert">{error}</span>}
    </div>
  );
}
