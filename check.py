import os
import re
import yaml
from glob import glob


def check_filename_convention(filename):
    # Matches name_lastname.yml
    return re.match(r"^[^_/]+-[^_/]+\.yml$", os.path.basename(filename))


def get_expected_object_name(filename):
    base_filename = os.path.basename(filename).rsplit(".", 1)[0]
    expected_name = base_filename.replace("-", ".")
    return expected_name


def get_object_name(obj):
    return obj.get("metadata", {}).get("name", "")


def check_object_name_convention(obj, filename):
    object_name = get_object_name(obj)
    # Extract base file name without extension
    base_filename = get_expected_object_name(filename)
    # Check both object name and file name match the convention
    pattern = r"^[^.]+\.[^.]+$"
    return re.match(pattern, object_name) and object_name == base_filename


def main():
    base_path = "clusters/production/namespaces"
    yml_files = glob(f"{base_path}/**/*.yml", recursive=True)
    errors = []

    for file in yml_files:
        with open(file, "r") as f:
            try:
                docs = list(yaml.safe_load_all(f))
            except Exception as e:
                errors.append(f"{file}: YAML parse error: {e}")
                continue

        for doc in docs:
            if not isinstance(doc, dict):
                continue
            kind = doc.get("kind", "")
            if kind in ["Role", "RoleBinding"]:
                if not check_filename_convention(file):
                    errors.append(
                        f"{file}: Filename does not match 'name-lastname.yml'"
                    )
                if not check_object_name_convention(doc, file):
                    errors.append(
                        f"{file}: Object name does not match 'name.lastname' (expected: {get_expected_object_name(file)}, found: {get_object_name(doc)})"
                    )

        # Check kustomization.yml resource references
        if os.path.basename(file) == "kustomization.yml":
            kustomization_dir = os.path.dirname(file)
            with open(file, "r") as f:
                try:
                    kustomization = yaml.safe_load(f)
                except Exception as e:
                    errors.append(f"{file}: YAML parse error: {e}")
                    continue
            resources = set(kustomization.get("resources", []))
            # Check declared resources exist
            for res in resources:
                res_path = os.path.join(kustomization_dir, res)
                if not os.path.exists(res_path):
                    errors.append(f"{file}: Resource '{res}' not found in directory.")
            # Check for missing resource declarations
            for neighbor in os.listdir(kustomization_dir):
                # neighbor_path = os.path.join(kustomization_dir, neighbor)
                if (
                    neighbor != "kustomization.yml"
                    and neighbor.endswith(".yml")
                    and neighbor not in resources
                ):
                    errors.append(
                        f"{file}: '{neighbor}' missing resource declaration in kustomization.yml"
                    )

    if errors:
        print("Errors found:")
        for err in errors:
            print(err)
        exit(1)
    else:
        print("All files and objects follow the conventions.")
        exit(0)


if __name__ == "__main__":
    main()
