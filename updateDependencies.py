import os
import subprocess
import sys
import tempfile
import zipfile
import requests  # type: ignore

def update_bundled_kape():
    """
    Compares the extracted KAPE version with the latest available and updates the bundled KAPE.zip if necessary.
    """
    bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(bundle_dir, "Get-KAPEUpdate.ps1")
    current_dir=os.getcwd()
    if not os.path.exists(script_path):
        print("Error: Update script not found in extracted KAPE.")
        return
    
    try:
        os.chdir(bundle_dir)
        update_command='Get-KapeUpdate.ps1'
        result = subprocess.run(update_command, capture_output=True, text=True, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error checking KAPE version: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def get_kape_online():
    """
    Downloads the KAPE.zip file from the specified URL, extracts it to a temporary directory,
    and updates the KAPE files.
    Returns the path to the extracted directory.
    """
    kape_url = "https://s3.amazonaws.com/cyb-us-prd-kape/kape.zip"
    temp_dir = tempfile.gettempdir()
    kape_zip_path = os.path.join(temp_dir, "KAPE.zip")
    extracted_dir = os.path.join(temp_dir, f"_MEI{os.getpid()}")

    # Download KAPE.zip
    if not os.path.exists(kape_zip_path):
        # print(f"Downloading KAPE.zip from {kape_url}...")
        try:
            response = requests.get(kape_url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            with open(kape_zip_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"KAPE.zip successfully downloaded to: {kape_zip_path}")
        except requests.RequestException as e:
            print(f"Error downloading KAPE.zip: {e}")
            sys.exit(1)
    else:
        print(f"KAPE.zip already exists at: {kape_zip_path}")

    # Extract the ZIP file
    os.makedirs(extracted_dir, exist_ok=True)
    print(f"Extracting KAPE files to {extracted_dir}...")
    try:
        with zipfile.ZipFile(kape_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)
        print(f"KAPE files extracted to: {extracted_dir}")
    except zipfile.BadZipFile:
        print("Error: The downloaded KAPE.zip file is corrupted.")
        sys.exit(1)

    kape_path = os.path.join(extracted_dir, "kape.exe")
    if not os.path.exists(kape_path):
        print(f"Error: kape.exe not found at {kape_path}. Please verify the extraction.")
        sys.exit(1)

    try:
        subprocess.run([kape_path, "--sync"], check=True)
        print("KAPE files updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error while updating KAPE files. Exit code: {e.returncode}")
        sys.exit(1)

    script_path = os.path.join(extracted_dir, "Get-KAPEUpdate.ps1")
    if not os.path.exists(script_path):
        print(f"Error: Get-KAPEUpdate.ps1 not found at {script_path}. Please verify the extraction.")
        sys.exit(1)
    try:
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], check=True)
        print("Tool updated successfully using getupdate.ps1.")
    except subprocess.CalledProcessError as e:
        print(f"Error while updating the tool. Exit code: {e.returncode}")
        sys.exit(1)
        