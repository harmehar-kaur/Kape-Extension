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
   git clone https://github.com/yourusername/Kape-Extension.git
   cd Kape-Extension
   ```
2. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```
3. Build the executable for easier execution:
   ```bash
   pyinstaller --onefile --add-data "KAPE:." finalBundled.py
   ```
   The generated executable will be in the `dist/` directory.

## Update Dependencies
To update dependencies, follow these steps:
1. Run the `Get-KAPEUpdate.ps1` script located in the `KAPE` directory of the cloned repository to update the tool(execute with admin privileges):
   ```powershell
   ./KAPE/Get-KAPEUpdate.ps1
   ```
2. Recompile the executable:
   ```bash
   pyinstaller --onefile --add-data "KAPE:." finalBundled.py
   ```

## Usage
The executable generated in the `dist/` directory can be used on victim systems to collect data. Transfer the executable into a USB or a share with the victim system owner(in case of remote acquisition) and follow the steps as followed for collecting the evidence as per the requirements. 

### Running the Executable
#### Using GUI
Run the executable as an administrator by double-clicking it.

#### Using PowerShell
```powershell
./finalBundled.exe
```

#### Specifying Output or Source Path
```powershell
./finalBundled.exe -o <output-path> -s <source-path>
```

#### Collecting Specific Targets
```powershell
./finalBundled.exe -t <targets comma separated>
```

#### Updating KAPE Files and Tool
```powershell
./finalBundled.exe -ut -u
```

#### Disabling Netstat and DNS Collection
```powershell
./finalBundled.exe -dc -ns
```

## Contact
For support or issues, create an issue on GitHub or reach out to `kaurharmehar9717@example.com`.

---
**Disclaimer:** This tool is intended for forensic and incident response use. Ensure compliance with local laws before using it.

