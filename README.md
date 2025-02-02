# CERT KAPE - Windows Artifact Extraction Tool

## Overview
CERT KAPE is a forensic tool designed to automate the extraction of digital artifacts from Windows systems. It utilizes KAPE (Kroll Artifact Parser and Extractor) to gather critical forensic evidence efficiently. The tool supports additional functionalities such as network activity monitoring, DNS cache collection, automatic updates, and secure data packaging.

## Features
- **Automated Artifact Collection**: Uses KAPE with predefined targets like `SANS-Triage` and `Server-Triage`.
- **Network Analysis**: Captures network connection details using `netstat`.
- **DNS Cache Retrieval**: Extracts DNS cache records for forensic analysis.
- **KAPE Updates**: Synchronizes with the latest KAPE releases.
- **Secure Evidence Packaging**: Creates AES-encrypted ZIP archives.
- **Automatic Cleanup**: Ensures temporary files are removed after execution.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cert-kape.git
   cd cert-kape
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure PowerShell execution policy allows running scripts:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force
   ```

## Usage
Run the tool with different options:
```bash
python cert_kape.py -o <output_path> -s <source_path> -t <targets> -dc -ns -u -ut
```

### Command-line Options
| Option   | Description |
|----------|-------------|
| `-o <path>` | Set the output path for collected artifacts (default: current directory). |
| `-s <path>` | Specify the source path for data collection. |
| `-t <targets>` | Define additional targets for collection. |
| `-dc` | Disable DNS cache collection (enabled by default). |
| `-ns` | Disable netstat collection (enabled by default). |
| `-u` | Update KAPE files only. |
| `-ut` | Update the tool using `Get-KAPEUpdate.ps1`. |

## Updating KAPE
To update the bundled KAPE version:
```bash
python updateDependencies.py
```
This script:
- Checks for updates using `Get-KAPEUpdate.ps1`
- Replaces `KAPE.zip` if a new version is available

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Please fork the repository, make changes, and submit a pull request.

## Contact
For support or issues, create an issue on GitHub or reach out to `your-email@example.com`.

---
**Disclaimer:** This tool is intended for forensic and incident response use. Ensure compliance with local laws before using it.

