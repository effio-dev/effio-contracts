import subprocess
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any

# Directory containing OpenAPI JSON files
INPUT_DIR = Path("schemas/openapi")
# Directory where generated Pydantic models will be saved
OUTPUT_DIR = Path("effio/generated")

def extract_service_name(path: str) -> str:
    """
    Extracts the service name from a URL path.
    Example: "/v1/account/get_by_id" -> "account"
    Example: "/account/create" -> "account"
    """
    parts = [p for p in path.split("/") if p]
    if not parts:
        return "common"
    
    # Check if first part is a version (v1, v2, etc.)
    if re.match(r'^v\d+$', parts[0]):
        if len(parts) > 1:
            return parts[1]
        return "common"
    
    return parts[0]

def generate_schemas():
    if not INPUT_DIR.exists():
        print(f"Input directory {INPUT_DIR} does not exist. Creating it...")
        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py if it doesn't exist
    (OUTPUT_DIR / "__init__.py").touch()

    json_files = [f for f in INPUT_DIR.glob("*.json") if not f.name.startswith("_temp_")]
    
    if not json_files:
        print(f"No .json files found in {INPUT_DIR}")
        return

    for json_file in json_files:
        print(f"Processing {json_file}...")
        try:
            with open(json_file, "r") as f:
                spec = json.load(f)
        except Exception as e:
            print(f"Failed to load {json_file}: {e}")
            continue

        paths = spec.get("paths", {})
        services: Dict[str, Dict[str, Any]] = {}

        for path, path_item in paths.items():
            service_name = extract_service_name(path)
            if service_name not in services:
                # Initialize a new spec for this service
                services[service_name] = {
                    "openapi": spec.get("openapi", "3.0.0"),
                    "info": spec.get("info", {}).copy(),
                    "paths": {},
                    "components": spec.get("components", {})
                }
                # Update title to include service name
                if "title" in services[service_name]["info"]:
                    services[service_name]["info"]["title"] += f" - {service_name.capitalize()}"
            
            services[service_name]["paths"][path] = path_item

        for service_name, service_spec in services.items():
            # If the filename contains a version, we might want to preserve it to avoid overwrites
            # for different versions of the same service.
            # Look for version in the JSON filename (e.g., openapi_v1.json)
            version_match = re.search(r'v(\d+)', json_file.name)
            version_suffix = f"_v{version_match.group(1)}" if version_match else ""
            
            # Use service_name as base. If it's v1 and the only one, maybe just service_name?
            # But the user said "v1/account/get_by_id should be called account.py"
            # So if it's v1, we omit the suffix?
            if version_suffix == "_v1":
                version_suffix = ""
            
            output_filename = f"{service_name}{version_suffix}.py"
            output_file = OUTPUT_DIR / output_filename
            
            # Create a temporary file for the split spec
            temp_spec_path = INPUT_DIR / f"_temp_{service_name}_{json_file.name}"
            with open(temp_spec_path, "w") as f:
                json.dump(service_spec, f)

            print(f"Generating schemas for service '{service_name}' from {json_file} into {output_filename}...")
            
            cmd = [
                "datamodel-codegen",
                "--input", str(temp_spec_path),
                "--output", str(output_file),
                "--input-file-type", "openapi",
                "--output-model-type", "pydantic_v2.BaseModel",
                "--use-schema-description",
                "--use-field-description",
                "--field-constraints",
                "--output-datetime-class", "datetime",
                "--use-title-as-name",
            ]

            # Add scopes based on what's available in the spec
            scopes = []
            if service_spec.get("paths"):
                scopes.append("paths")
            if service_spec.get("components", {}).get("schemas"):
                scopes.append("schemas")
            
            for scope in scopes:
                cmd.extend(["--openapi-scopes", scope])
            
            try:
                subprocess.run(cmd, check=True)
                print(f"Successfully generated: {output_file}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to generate schemas for {service_name}: {e}")
            finally:
                if temp_spec_path.exists():
                    os.remove(temp_spec_path)

if __name__ == "__main__":
    generate_schemas()
