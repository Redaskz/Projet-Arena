interface ErrorMessageProps {
  message: string;
}

function ErrorMessage({ message }: ErrorMessageProps) {
  return <p role="alert">{message}</p>;
}

export default ErrorMessage;