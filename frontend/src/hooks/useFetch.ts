import { useCallback, useEffect, useState } from 'react';
import { ApiError, get } from '../api/client';

interface UseFetchResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useFetch<T>(url: string): UseFetchResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [requestKey, setRequestKey] = useState<number>(0);

  const refetch = useCallback(() => {
    setRequestKey((currentKey) => currentKey + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function fetchData(): Promise<void> {
      setLoading(true);
      setError(null);

      try {
        const result = await get<T>(url);

        if (!cancelled) {
          setData(result);
        }
      } catch (requestError: unknown) {
        if (cancelled) {
          return;
        }

        if (requestError instanceof ApiError) {
          setError(requestError.message);
        } else {
          setError('Une erreur est survenue.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void fetchData();

    return () => {
      cancelled = true;
    };
  }, [url, requestKey]);

  return {
    data,
    loading,
    error,
    refetch,
  };
}