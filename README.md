### CI/CD Integration for Flask OpenAPI Generation

This project is configured to automatically generate Pydantic models from OpenAPI JSON files. This allows you to maintain a single source of truth in your microservices without exposing your API documentation to the public internet.

#### 1. Flask Service: Export Script

In your Flask microservice (e.g., Account Service), you can create a script to export the OpenAPI schema. If you are using `apispec` or a similar library, your script might look like this:

```python
# scripts/export_openapi.py
import json
from your_app import create_app
from your_app.extensions import spec  # Assuming you use apispec

def export_schema():
    app = create_app()
    with app.app_context():
        # Depending on your Flask-OpenAPI implementation:
        # For apispec:
        openapi_dict = spec.to_dict()
        
        with open("openapi.json", "w") as f:
            json.dump(openapi_dict, f, indent=2)

if __name__ == "__main__":
    export_schema()
```

#### 2. CI/CD Workflow

The recommended workflow for updating contracts without public exposure is:

1.  **Microservice Pipeline (e.g., Account Service):**
    *   On merge to `main`:
    *   Run the export script to generate `openapi.json`.
    *   Push the `openapi.json` to the `effio-contracts` repository's `schemas/openapi/` directory.
    *   Alternatively, use a tool like `curl` to trigger a GitHub Action in the `effio-contracts` repo, passing the JSON as an artifact.

2.  **Contracts Pipeline (`effio-contracts` repo):**
    *   When a new file is added/updated in `schemas/openapi/`:
    *   Run `python generate_contracts.py`.
    *   The script will scan `schemas/openapi/` and update the corresponding models in `effio/generated/`.
    *   Commit the changes and publish a new version of the package.

#### 3. Manual Generation

If you have a JSON file locally, simply place it in `schemas/openapi/` and run:

```bash
pip install ".[dev]"
python generate_contracts.py
```

The output will be available in `effio/generated/<service_name>.py`.

#### 4. Naming Conventions

The generated file name is derived from the URL paths inside your OpenAPI JSON files:
- Example path: `/v1/account/get_by_id` -> `effio/generated/account.py`
- If a JSON file contains multiple services (e.g., `/v1/account/...` and `/v1/auth/...`), it will generate multiple Python files (`account.py` and `auth.py`).
- If the source filename contains a version other than `v1` (e.g., `openapi_v2.json`), the version will be appended to the service name: `account_v2.py`.
- If the schema uses `title` fields, those will be used as the Pydantic class names.
