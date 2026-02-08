import os
import re
import json
import sys

def get_risk_level(license_name):
    if not license_name:
        return "medium" # Treat as UNKNOWN
    
    ln = license_name.upper()
    if "GPL" in ln and "LGPL" not in ln: # Strict GPL is high risk
        return "high"
    if "UNKNOWN" == ln:
        return "medium"
    return "low"

def normalize_license(name, detected_license):
    mapping = {
        "ZLIB": "Zlib",
        "GTEST": "BSD-3-Clause",
        "CJSON": "MIT",
        "BOOST": "BSL-1.0"
    }
    
    if detected_license:
        return detected_license
    
    upper_name = name.upper()
    if upper_name in mapping:
        return mapping[upper_name]
    
    return "UNKNOWN"

def scan_file(filepath):
    dependencies = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    patterns = [
        r'find_package\s*\(\s*(\w+)',
        r'ExternalProject_Add\s*\(\s*(\w+)',
        r'FetchContent_Declare\s*\(\s*(\w+)'
    ]
    
    for i, line in enumerate(lines):
        dep_name = None
        for pat in patterns:
            match = re.search(pat, line)
            if match:
                dep_name = match.group(1)
                break
        
        if dep_name:
            license_comment = None
            comment_match = re.search(r'#\s*License:\s*([\w\-\.]+)', line, re.IGNORECASE)
            if comment_match:
                license_comment = comment_match.group(1)
            
            dependencies.append({
                "name": dep_name,
                "license_source": license_comment,
                "dir": os.path.dirname(filepath)
            })
            
    return dependencies

def main():
    root_dirs = [".", "./example", "./test"]
    all_deps = []
    
    for root_dir in root_dirs:
        search_path = os.path.normpath(root_dir)
        if not os.path.exists(search_path):
            continue
            
        for root, dirs, files in os.walk(search_path):
            if "CMakeLists.txt" in files:
                filepath = os.path.join(root, "CMakeLists.txt")
                deps = scan_file(filepath)
                all_deps.extend(deps)

    dep_map = {}
    
    for dep in all_deps:
        name = dep['name']
        detected_license = dep['license_source']
        
        final_license = normalize_license(name, detected_license)
        risk = get_risk_level(final_license)
        
        if name not in dep_map:
            dep_map[name] = {"name": name, "license": final_license, "risk": risk}
        else:
            current_risk = dep_map[name]["risk"]
            if risk == "high":
                dep_map[name]["risk"] = "high"
                dep_map[name]["license"] = final_license
            elif risk == "medium" and current_risk == "low":
                dep_map[name]["risk"] = "medium"
                dep_map[name]["license"] = final_license

    report = list(dep_map.values())
    
    with open("dependency-report.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
