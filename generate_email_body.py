import os
import json
import pytz
from datetime import datetime
import pandas as pd

# Read SonarQube results JSON file
json_path = os.getenv("SONAR_JSON", "sonar_results.json")
if not os.path.exists(json_path):
    raise FileNotFoundError(f"SonarQube JSON not found at: {json_path}")

with open(json_path, 'r') as f:
    data = json.load(f)

measures = data['component']['measures']

# Define metrics and safe thresholds
metric_definitions = {
    "bugs": ("Bugs", "Code defects affecting reliability", "= 0", lambda v: v <= 0),
    "vulnerabilities": ("Vulnerabilities", "Security weaknesses in code", "= 0", lambda v: v <= 0),
    "code_smells": ("Code Smells", "Maintainability issues", "<= 5", lambda v: v <= 5),
    "coverage": ("Coverage", "Code coverage from tests", ">= 80%", lambda v: v >= 80),
    "duplicated_lines_density": ("Duplicated Lines %", "Code duplication", "<= 5%", lambda v: v <= 5),
    "reliability_rating": ("Reliability Rating", "Reliability score", "= 1.0", lambda v: float(v) == 1.0),
    "security_rating": ("Security Rating", "Security score", "= 1.0", lambda v: float(v) == 1.0),
    "sqale_rating": ("Maintainability Rating", "Maintainability score", "= 1.0", lambda v: float(v) == 1.0),
    "ncloc": ("Lines of Code", "Non-comment lines", "--", lambda v: True),
    "functions": ("Functions", "Function count", "--", lambda v: True),
    "classes": ("Classes", "Class count", "--", lambda v: True),
    "complexity": ("Complexity", "Code complexity", "--", lambda v: True),
    "alert_status": ("Alert Status", "Quality Gate result", "OK", lambda v: v == "OK")
}

rows = []
for m in measures:
    key = m['metric']
    if key in metric_definitions:
        name, desc, safe_range, evaluator = metric_definitions[key]
        raw_val = m['value']
        try:
            if isinstance(raw_val, str) and raw_val.endswith('%'):
                numeric_val = float(raw_val.strip('%'))
            elif key == "alert_status":
                numeric_val = raw_val  # Keep as string
            else:
                numeric_val = float(raw_val)
        except ValueError:
            numeric_val = raw_val

        status = "✅ Fine" if evaluator(numeric_val) else "⚠️ Needs Check"
        rows.append([name, desc, safe_range, raw_val, status])

df = pd.DataFrame(rows, columns=["Metric", "Description", "Safe Range", "Actual Value", "Status"])

# Build HTML
ist = pytz.timezone('Asia/Kolkata')
timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
html = f"""
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
        }}
        h2 {{
            color: #2E86C1;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
    <h2>📊 SonarQube Analysis Summary</h2>
    <p><strong>Generated on:</strong> {timestamp}</p>
    {df.to_html(index=False, escape=False)}
</body>
</html>
"""

# Save HTML
output_path = os.path.join(os.path.dirname(json_path), "email_body.html")
with open(output_path, 'w') as f:
    f.write(html)

print(f"✅ Email body generated at: {output_path}")
