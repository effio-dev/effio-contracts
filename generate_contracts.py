import subprocess
import os
from pathlib import Path

# Mapping of service name to its OpenAPI JSON source (URL or local path)
SERVICES = {
    "account": "account_service_openapi.json",
    # "auth": "https://auth-service.dev.effio.com/openapi.json",
}

OUTPUT_DIR = Path("effio/generated")

def generate_schemas():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py if it doesn't exist
    (OUTPUT_DIR / "__init__.py").touch()

    for service_name, source in SERVICES.items():
        output_file = OUTPUT_DIR / f"{service_name}.py"
        print(f"Generating schemas for {service_name} from {source}...")
        
        cmd = [
            "datamodel-codegen",
            "--input", source,
            "--output", str(output_file),
            "--input-file-type", "openapi",
            "--output-model-type", "pydantic_v2.BaseModel",
            "--use-schema-description",
            "--use-field-description",
            "--field-constraints",
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"Successfully generated: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to generate schemas for {service_name}: {e}")

if __name__ == "__main__":
    generate_schemas()
