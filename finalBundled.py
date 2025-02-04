import csv
import os
from pathlib import Path
import re
import subprocess
import sys
import psutil # type: ignore
import pyzipper  # type: ignore

def print_help():
    print("CERT Kape: A Kape Extension to extract Windows Artefacts using targets SANS-Triage and Server Triage.")
    print("usage: cert_kape.exe [options]")
    print("Options:")
    print("-o <path> : The path to the destination where the collected artefacts are to be saved. Default is set to the current directory, i.e., the directory from where Kape is running.")
    print("-h        : Show this help message and exit.")
    print("-v        : Enable verbose mode for debugging.")
    print("-s <path> : Specify the source path from where data has to be collected.")
    print("-t <targets> : Specify additional targets to be collected (comma-separated).")
    print("-dc       : Collect DNS-Cache Information. False by default")
    print("-ns       : Collect netstat-enriched information. False by default.")
    print("-u        : Update KAPE files only.")
    print("-ut       : Update the tool by running the getupdate.ps1 script.")

def extract_kape():
    bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

    
    if not os.path.exists(bundle_dir):
        print(f"[ERROR]KAPE bundle not found at: {bundle_dir}")
        sys.exit(1)

    # print("[SUCCESS]kape.exe located.")
    print("Running Kape...")
    return bundle_dir

def update_kape_files(kape_dir):
    """
    Runs the kape.exe --sync command to update KAPE files.
    """
    kape_path = os.path.join(kape_dir, "kape.exe")
    kape_command= f'"{kape_path}" --sync'
    if not os.path.exists(kape_path):
        print(f"Error: kape.exe not found at {kape_path}. Please verify the extraction.")
        sys.exit(1)

    try:
        subprocess.run(kape_command, check=True)
        print("KAPE files updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error while updating KAPE files. Exit code: {e.returncode}")
        sys.exit(1)

def update_tool_script(kape_dir):
    """
    Runs the getupdate.ps1 script to update the tool.
    """
   
    script_path = os.path.join(kape_dir, "Get-KAPEUpdate.ps1")
    current_dir=os.getcwd()
    if not os.path.exists(script_path):
        print(f"Error: Get-KAPEUpdate.ps1 not found at {script_path}. Please verify the extraction.")
        sys.exit(1)

    try:
        os.chdir(kape_dir)
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], check=True)
        print("Tool updated successfully using Get-KAPEUpdate.ps1.")
        os.chdir(current_dir)
    except subprocess.CalledProcessError as e:
        print(f"Error while updating the tool. Exit code: {e.returncode}")
        sys.exit(1)

def capture_netstat(output_dir):
    netstat_txt_file = os.path.join(output_dir, "netstat_output.txt")
    netstat_csv_path = os.path.join(output_dir, "netstat_info.csv")

    try:
        # Step 1: Run netstat command and save output to a text file
        with open(netstat_txt_file, "w", encoding="utf-8") as file:
            subprocess.run(["powershell", "netstat -ano"], stdout=file, text=True)

        # Step 2: Read the netstat output and parse data
        connections = []
        
        with open(netstat_txt_file, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Regular expression to extract required fields
        netstat_pattern = re.compile(r"(?P<protocol>\S+)\s+(?P<local_address>\S+)\s+(?P<foreign_address>\S+)\s+(?P<state>\S+)?\s+(?P<pid>\d+)")

        for line in lines:
            match = netstat_pattern.search(line)
            if match:
                protocol = match.group("protocol")
                local_address = match.group("local_address")
                foreign_address = match.group("foreign_address")
                state = match.group("state") if match.group("state") else "N/A"
                pid = int(match.group("pid"))

                # Step 3: Get process name and binary path
                try:
                    process = psutil.Process(pid)
                    process_name = process.name()
                    binary_path = process.exe()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_name = "N/A"
                    binary_path = "N/A"

                # Store the extracted data
                connections.append([protocol, local_address, foreign_address, state, pid, process_name, binary_path])

        # Step 4: Write data to CSV
        with open(netstat_csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Protocol", "LocalAddress", "ForeignAddress", "State", "ProcessID", "ProcessName", "BinaryPath"])
            writer.writerows(connections)

        print(f"Netstat data saved to {netstat_csv_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Cleanup: Remove the text file
        if os.path.exists(netstat_txt_file):
            os.remove(netstat_txt_file)
            print(f"Deleted temporary file: {netstat_txt_file}")



def capture_dns_cache(output_dir):
    dns_csv_path = os.path.join(output_dir, "dns_cache.csv")
    
    try:
        print("[INFO] Capturing DNS cache information...")
        command = f'Get-DnsClientCache | Select-Object Entry, Name, Status, Type, TimeToLive, Data | Export-Csv -NoTypeInformation -Path "{dns_csv_path}"'
        
        # Run PowerShell command
        subprocess.run(["powershell", "-Command", command], shell=True, check=True)
        
        print(f"[SUCCESS] DNS cache information saved to: {dns_csv_path}")
    except Exception as e:
        print(f"[ERROR] Failed to capture DNS cache: {e}")

def zip_evidence(folder_path):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    password = "thisisgoingtoberandom"
    zip_file_name = os.path.basename(folder_path.rstrip(os.sep)) + ".zip"
    output_path = os.path.join(desktop_path, zip_file_name)
    
    error_log_path = os.path.join(folder_path, "faulty_files.csv")
    faulty_files = []
    
    print("[INFO] Zipping collected data...")
    
    try:
        with pyzipper.AESZipFile(output_path, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zip_file:
            zip_file.pwd = password.encode('utf-8')
            
            for root, _, files in os.walk(folder_path):
                for file_name in files:
                    absolute_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(absolute_path, os.path.dirname(folder_path))
                    try:
                        zip_file.write(absolute_path, relative_path)
                    except (FileNotFoundError, OSError) as e:
                        faulty_files.append([absolute_path, str(e)])

            if faulty_files:
                with open(error_log_path, "w", newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(["File Path", "Error Encountered"])
                    writer.writerows(faulty_files)
                zip_file.write(error_log_path, os.path.relpath(error_log_path, os.path.dirname(folder_path)))
                print(f"[INFO] Added error log to ZIP: {error_log_path}")
        
        print(f"[SUCCESS] Password-protected ZIP file created at: {output_path}")
        
    except Exception as e:
        print(f"[ERROR] Failed to create ZIP file: {e}")
    finally:
        if os.path.exists(error_log_path):
            try:
                os.remove(error_log_path)
                print(f"[INFO] Error log file removed: {error_log_path}")
            except Exception as e:
                print(f"[WARNING] Failed to remove error log file: {e}")

def main():
    output_path = None 
    source_path = "C:/"
    verbose = False
    target = "!SANS_Triage,ServerTriage"
    ns=True
    dc=True
    update_files=False
    update_tool=False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "-o" and i + 1 < len(args):
            output_path = args[i + 1]
            i += 1
        elif arg == "-s" and i + 1 < len(args):
            source_path = args[i + 1]
            i += 1
        elif arg == "-v":
            verbose = True
        elif arg == "-t" and i + 1 < len(args):
            target = f",{args[i + 1]}"
            i += 1
        elif arg == "-h":
            print_help()
            return
        elif arg == "-u":
            update_files = True
        elif arg == "-ut":
            update_tool = True
        elif arg == "-dc":
            dc = False
        elif arg == "-ns":
            ns = False 
        else:
            print(f"Unknown option: {arg}")
            print_help()
            return
        i += 1

    extracted_kape_path = extract_kape()
    if update_files:
        update_kape_files(extracted_kape_path)
    if update_tool:
        update_tool_script(extracted_kape_path)
    # If no output path is provided, set it to the KAPE extraction location
    
    if output_path is None:
        output_path = os.path.join(extracted_kape_path, "Collected_Evidence")

    # Ensure the output directory exists
    output_dir = Path(output_path)
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True)
        except Exception as e:
            print(f"Failed to create output directory: {output_path}\nError: {e}")
            sys.exit(1)
    kPath =os.path.join(extracted_kape_path, "kape.exe")
    kape_command = f'"{kPath}" --tsource "{source_path}" --tdest "{output_path}" --target "{target}"'
    if verbose:
        print(f"Executing: {kape_command}")
    try:
        subprocess.run(kape_command, shell=True, check=True)
        print(f"KAPE completed. Artifacts collected at: {output_path}")

        if(ns):
            capture_netstat(output_path)
        if(dc):    
            capture_dns_cache(output_path)

        zip_evidence(output_path)
        return
    except subprocess.CalledProcessError as e:
        print(f"Error while running KAPE. Exit code: {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    os.environ['LONG_PATH_SUPPORT'] = 'true'
    main()
