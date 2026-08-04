/**
 * ErrorMessage — Displays an error message from API or validation.
 *
 * Props:
 * - message: string | null
 */

interface ErrorMessageProps {
  message: string | null;
}

export function ErrorMessage({ message }: ErrorMessageProps) {
  if (!message) return null;

  return (
    <div role="alert">
      {/* TODO: Styled error box */}
      <p>{message}</p>
    </div>
  );
}
