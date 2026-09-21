import { useEffect, useState } from 'react';
import type { Dispatch, SetStateAction } from 'react';

// Même usage que useState, mais la valeur survit à un rechargement (F5) :
//   const [genre, setGenre] = useLocalStorage<string>('games.genre', 'all');
// Générique <T> : le même hook sert pour un texte, un nombre ou un objet.
function useLocalStorage<T>(
  key: string,
  initialValue: T,
): [T, Dispatch<SetStateAction<T>>] {
  // Initialisation "paresseuse" (on passe une fonction à useState) :
  // localStorage n'est lu qu'au premier rendu, pas à chaque re-rendu.
  const [value, setValue] = useState<T>(() => {
    try {
      const stored = window.localStorage.getItem(key);
      // Rien d'enregistré : première visite, on prend la valeur par défaut.
      if (stored === null) {
        return initialValue;
      }
      // On fait confiance au format : c'est ce hook lui-même qui a écrit la valeur.
      const parsed: T = JSON.parse(stored);
      return parsed;
    } catch {
      // JSON corrompu, navigation privée, stockage bloqué...
      // La page doit fonctionner quand même : on retombe sur la valeur par défaut.
      return initialValue;
    }
  });

  // Écriture après chaque changement de valeur. Dans un useEffect et pas dans
  // un setter maison : on garde le vrai setValue de React, qui accepte aussi
  // la forme fonction setValue((prev) => ...).
  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // Stockage plein ou interdit : on perd seulement la mémorisation,
      // le filtre continue de fonctionner pendant la visite.
    }
  }, [key, value]);

  return [value, setValue];
}

export default useLocalStorage;
