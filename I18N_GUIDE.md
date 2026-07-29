# Internationalization Guide for Lute v3

## Installation

To use internationalization features, install Flask-Babel:

```bash
pip install Flask-Babel>=4.0.0
```

## Supported Languages

- **English** (en) - default
- **Spanish** (es)
- **French** (fr)

## Usage

### Changing Language

1. Use the "Language" menu in the navigation bar
2. Or visit directly:
   - `/language/set/en` for English
   - `/language/set/es` for Spanish
   - `/language/set/fr` for French

### Test Page

A demonstration page is available at `/test_i18n` to see internationalization in action.

## File Structure

```
lute/
├── i18n/
│   └── __init__.py              # Flask-Babel configuration
├── language_selection/
│   ├── __init__.py
│   └── routes.py                # Routes for language switching
└── translations/
    ├── es/LC_MESSAGES/
    │   ├── messages.po          # Spanish translations
    │   └── messages.mo          # Compiled translations
    └── fr/LC_MESSAGES/
        ├── messages.po          # French translations
        └── messages.mo          # Compiled translations
```

## For Developers

### Adding New Translatable Strings

1. In templates, use `{{ _('Your text') }}`
2. In Python code, use `_('Your text')` (after import)

### Extracting New Strings

```bash
pybabel extract -F babel.cfg -k _ -o messages.pot .
```

### Updating Translations

```bash
pybabel update -i messages.pot -d lute/translations
```

### Compiling Translations

```bash
pybabel compile -d lute/translations
```

### Adding a New Language

```bash
pybabel init -i messages.pot -d lute/translations -l LANGUAGE_CODE
```

## Configuration

Languages are configured in `lute/i18n/__init__.py`:

```python
app.config['LANGUAGES'] = {
    'en': 'English',
    'es': 'Español', 
    'fr': 'Français'
}
```

## Testing

Run internationalization tests:

```bash
python test_i18n.py
```

## Included Translations

### Main Menu
- Home / Inicio / Accueil
- Books / Libros / Livres
- Terms / Términos / Termes
- Settings / Configuración / Paramètres
- Languages / Idiomas / Langues
- Backup / Copia de seguridad / Sauvegarde
- About / Acerca de / À propos

### Common Actions
- Create new Book / Crear nuevo Libro / Créer un nouveau Livre
- Import web page / Importar página web / Importer une page web
- Import Terms / Importar Términos / Importer des Termes
- Create backup / Crear copia de seguridad / Créer une sauvegarde

### System Messages
- Warning / Advertencia / Avertissement
- Statistics / Estadísticas / Statistiques
- Version and software info / Información de versión y software / Informations de version et logiciel

## Notes

- The selected language is stored in the user session
- If no language is set, the application uses English as default
- The implementation is compatible even without Flask-Babel installed (with warnings)