# Jungle Soop AI Assistant Instructions

This document collects knowledge that an AI agent needs to be effective in the `jungle-soop` codebase.  It is **not** a style guide or a substitute for human review – instead it points out the patterns, conventions and commands that are unique to this project.

---
## 🏗 Big‑Picture Architecture

- Python/Flask monolith with server‑side rendered templates (Jinja2).  There is no separate SPA or frontend framework – HTML pages are returned from Flask and some AJAX is used on the client side.
- MongoDB holds all data.  The application uses `pymongo` directly; there is **no ORM**.
- The `app` package is tiny: `__init__.py` creates the Flask application, configures the secret key and Mongo URI, then calls two helpers:
  - `db.init_mongo(app)` (stores a `MongoClient` in `app.extensions["mongo_client"]`).
  - `routes.register_routes(app)` (registers all HTTP endpoints).
- Routes are defined in `app/routes.py` as simple `@app.get(...)` handlers that render templates or return JSON for `/health`.  Business logic and database access are currently not implemented – new code should either live here or in new modules imported by `register_routes`.
- The database helper provides:
  ```python
  get_mongo_client(app)  # returns MongoClient
  get_database(app)      # returns client[db_name]
  ```
  Use `get_database(current_app)` when you need to read/write collections.
- Templates under `app/templates` correspond 1:1 with the scaffolded routes (`index.html`, `login.html`, `meeting_list.html`, etc.).
- Static assets are located in `app/static` (CSS under `css/style.css`).

---
## ⚙️ Configuration & Environment

- **ENV vars** control secrets and connections.  See `app/__init__.py` for defaults:
  ```python
  SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
  MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/jungle_soop")
  MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "jungle_soop")
  ```
- Local development often sets a `.env` file (used by `docker-compose` via `env_file`).  Example variables:
  ```ini
  SECRET_KEY=supersecret
  MONGO_URI=mongodb://localhost:27017/jungle_soop_dev
  ```
- Tests use a different database name (`jungle_soop_test`).  The `docker-compose.test.yml` file injects `MONGO_URI` accordingly.

---
## 🧩 Key Developer Workflows

1. **Run locally**
   ```powershell
   python run.py            # starts Flask on 0.0.0.0:5000
   # or via docker-compose:
   cd docker && docker-compose -f docker-compose.dev.yml up --build
   ```
2. **Run tests**
   - Simple: `python -m pytest -q` from project root.
   - Markers separate unit vs integration (see `pytest.ini`).
   - CI uses `docker-compose -f docker/docker-compose.test.yml up --build` which starts a mongo container and runs `pytest` in the `test` service.
3. **SQLite / Mongo commands**
   - There is no ORM or migrations; create or remove collections directly with `db = get_database(app)`.
4. **Static analysis / linting**
   - Not configured in repo, but you can add `flake8`/`black` if desired – keep existing 4‑space indentation and no trailing whitespace.

---
## 🔍 Project‑Specific Conventions

- **App factory pattern**: always use `create_app()` to get a Flask instance.  Tests and `run.py` rely on this.
- **Extensions**: the only extension is the Mongo client; it's stored in `app.extensions["mongo_client"]`.  Do **not** create global clients at import time.
- **Route registration**: all endpoints are added inside `register_routes(app)` rather than by importing blueprints.  New domains should follow the same pattern or introduce a blueprint with a similar register‑function for consistency.
- **Testing fixtures**: `tests/conftest.py` provides `app` and `client` fixtures used across unit and integration tests.  Mark tests with `@pytest.mark.unit` or `@pytest.mark.integration` as appropriate.
- **Database URI parsing**: `_extract_db_name_from_uri` ensures a default DB name when the path is empty.  It is tested in `tests/unit/test_db.py` – keep this behavior when modifying the database module.
- **Template data injection**: `meeting_detail` passes `meeting_id` into the template.  When adding new parameters, follow the existing pattern of passing kwargs to `render_template`.

---
## 🔗 Integration Points & External Dependencies

- MongoDB connection string is the only external dependency; all calls originate from `app/db.py`.
- Docker is used for local/on‑CI orchestration; see `docker/Dockerfile` and the `docker-compose` files.
- CI pipeline (inferred from README) runs `pytest` and builds images; the repository does **not** include workflow YAML, so continue editing `.github/workflows` if you add new steps.

---
## 📝 Miscellaneous Notes

- The README contains extensive documentation and diagrams; refer to it for conceptual understanding.
- The UI uses Tailwind classes in the static template files – modifications should preserve mobile responsive layout.
- There are two bootstrap scripts under `scripts/` for cross‑platform setup; they are invoked manually during deployment.

---
## ✅ What To Do When Making Changes

1. Update or add a unit test under `tests/unit` for any new utility function or configuration change.
2. Add integration tests for new routes or template rendering under `tests/integration`.
3. Reflect new env vars in README and `docker-compose` files if they are required for containerized runs.
4. When adding Python modules, respect the existing package structure (`app/…`) and import them lazily inside `register_routes` to avoid circular imports.

---
Feel free to ask for clarification if any part of the application seems opaque – this project is intentionally small, so most logic lives in the three files under `app/` and supporting tests.

---
*End of instructions.*
