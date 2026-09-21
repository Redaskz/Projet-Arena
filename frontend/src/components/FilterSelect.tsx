import './FilterSelect.css';

export interface FilterOption {
  value: string;
  label: string;
}

interface FilterSelectProps {
  id: string;
  label: string;
  value: string;
  // Libellé de la première option, celle qui désactive le filtre (valeur 'all').
  allLabel: string;
  options: FilterOption[];
  onChange: (value: string) => void;
}

// Liste déroulante de filtre, partagée par GamesPage (genre) et TeamsPage (jeu).
// Le composant est "contrôlé" : il n'a pas d'état, la page lui donne la valeur
// et reçoit chaque changement. C'est la page qui décide où la valeur est stockée.
function FilterSelect({ id, label, value, allLabel, options, onChange }: FilterSelectProps) {
  return (
    <div className="filter-select">
      {/* htmlFor relie le label au select : cliquer sur le texte ouvre la liste. */}
      <label htmlFor={id}>{label}</label>
      <select id={id} value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="all">{allLabel}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

export default FilterSelect;
