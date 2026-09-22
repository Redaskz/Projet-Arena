// Ce fichier dit à ESLint quelles règles vérifier dans notre code (erreurs
// JavaScript classiques, typage TypeScript, bon usage des hooks React) quand on
// lance `npm run lint`. ESLint 9 utilise ce format "plat" : un simple tableau
// d'objets JavaScript lus dans l'ordre, qui remplace l'ancien .eslintrc et sa
// cascade de fichiers, plus difficile à suivre.
//
// Versions installées (frontend/package.json) : eslint 9.39, typescript-eslint
// 8.70, eslint-plugin-react-hooks 6.1, eslint-plugin-react-refresh 0.4, globals 16.
import js from '@eslint/js';
import { defineConfig, globalIgnores } from 'eslint/config';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import globals from 'globals';
import tseslint from 'typescript-eslint';

// defineConfig (fourni par ESLint depuis la 9.22) vérifie la forme de la
// configuration et autorise `extends`, plus lisible que d'étaler les presets.
export default defineConfig([
  // dist/ contient le code généré par `npm run build` : ce n'est pas notre
  // code source, le vérifier n'aurait aucun sens.
  globalIgnores(['dist']),
  {
    // Seul notre code applicatif est vérifié : les .ts et .tsx de src/.
    files: ['src/**/*.{ts,tsx}'],
    extends: [
      // Règles de base de JavaScript (variable non définie, code inatteignable...).
      js.configs.recommended,
      // Règles TypeScript : interdit notamment `any` explicite et les
      // variables déclarées mais jamais utilisées.
      tseslint.configs.recommended,
      // Les 2 règles classiques des hooks : pas de hook dans un if ou une
      // boucle (erreur), dépendances de useEffect complètes (avertissement).
      // On ne prend PAS 'recommended-latest' : il ajoute 15 règles liées au
      // React Compiler, qui obligeraient à réécrire du code déjà validé.
      reactHooks.configs.recommended,
      // Preset prévu pour Vite : vérifie qu'un fichier de composant n'exporte
      // que des composants, sinon le rechargement à chaud (HMR) recharge
      // toute la page au lieu du seul composant modifié.
      reactRefresh.configs.vite,
    ],
    rules: {
      // Même réglage que le preset Vite, plus une exception : useAuth.tsx
      // exporte le composant AuthProvider ET le hook useAuth. C'est le schéma
      // habituel d'un contexte React ; le séparer en deux fichiers serait une
      // réécriture. Seul effet : modifier ce fichier recharge toute la page en
      // développement au lieu du seul composant.
      'react-refresh/only-export-components': [
        'error',
        { allowConstantExport: true, allowExportNames: ['useAuth'] },
      ],
    },
    languageOptions: {
      // Le code tourne dans le navigateur : window, document, localStorage...
      // sont connus d'ESLint et ne sont pas signalés comme "non définis".
      globals: globals.browser,
    },
  },
]);
