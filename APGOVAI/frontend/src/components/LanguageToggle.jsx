import { LANGUAGES } from "../i18n";

export default function LanguageToggle({
  language,
  onChange,
  label = "Language",
  compact = false,
  options = LANGUAGES,
}) {
  return (
    <div
      className={
        compact
          ? "language-control compact"
          : "language-control"
      }
      aria-label={label}
    >
      <span>
        {label}
      </span>

      <div className="language-toggle">
        {
          options.map(option => (
            <button
              key={option.code}
              type="button"
              className={
                language === option.code
                  ? "active"
                  : ""
              }
              aria-pressed={
                language === option.code
              }
              onClick={() =>
                onChange(option.code)
              }
            >
              {option.label}
            </button>
          ))
        }
      </div>
    </div>
  );
}
