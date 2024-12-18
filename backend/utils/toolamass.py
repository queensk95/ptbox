import subprocess
import json
import os
import re
from datetime import datetime


class AmassScanner:
    def __init__(self, amass_path="amass", log_file="amass_scanner.log"):
        self.amass_path = amass_path
        self.log_file = log_file

    def log_message(self, message):
        with open(self.log_file, "a") as log:
            log.write(f"{datetime.now()} - {message}\n")

    def run_amass(self, domain, passive=False, max_dns_queries=10, timeout=1000):
        output_file = f"{domain}_amass_output.json"
        command = [
            self.amass_path, 'enum', '-d', domain,
            '-o', output_file,
            '-timeout', str(timeout), '-max-dns-queries', str(max_dns_queries)
        ]

        if passive:
            command.append('-passive')

        self.log_message(f"Running command: {' '.join(command)}")
        print(f"Running command: {' '.join(command)}")

        try:
            subprocess.run(command, check=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            self.log_message(f"Amass scan for {domain} timed out after {timeout} seconds.")
            print(f"Amass scan for {domain} timed out after {timeout} seconds.")
        except subprocess.CalledProcessError as e:
            self.log_message(f"Error running Amass: {e.stderr}")
            print(f"Error running Amass: {e.stderr}")
        except FileNotFoundError:
            self.log_message("Amass binary not found. Ensure Amass is installed and added to PATH.")
            print("Amass binary not found. Ensure Amass is installed and added to PATH.")
        except Exception as e:
            self.log_message(f"Unexpected error: {e}")
            print(f"Unexpected error: {e}")

        # Attempt to read output regardless of scan completion
        if os.path.exists(output_file):
            try:
                with open(output_file, "r") as json_file:
                    return json.load(json_file)
            except json.JSONDecodeError:
                self.log_message("Error parsing Amass output as JSON. Attempting to process as text.")
                print("Error parsing Amass output as JSON. Attempting to process as text.")
                try:
                    with open(output_file, "r") as text_file:
                        return {"raw_output": text_file.read()}
                except Exception as e:
                    self.log_message(f"Error reading output file: {e}")
                    print(f"Error reading output file: {e}")
                    return {"error": str(e)}
        else:
            self.log_message(f"Output file {output_file} not found.")
            print(f"Output file {output_file} not found.")
            return {"error": f"Output file {output_file} not found."}

    def extract_relevant_details(self, results):
        if "raw_output" in results:
            raw_data = results["raw_output"]
            subdomains = set(re.findall(r'\b[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', raw_data))
            ips = set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', raw_data))
            emails = set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', raw_data))

            return {
                "subdomains": list(subdomains),
                "ips": list(ips),
                "emails": list(emails)
            }

        relevant_data = {"subdomains": set(), "ips": set(), "emails": set()}

        try:
            for entry in results:
                if isinstance(entry, dict):
                    relevant_data["subdomains"].add(entry.get("name", ""))
                    for address in entry.get("addresses", []):
                        if isinstance(address, dict):
                            relevant_data["ips"].add(address.get("ip", ""))
        except Exception as e:
            self.log_message(f"Error parsing results: {e}")
            print(f"Error parsing results: {e}")
            return {"error": str(e)}

        return {
            "subdomains": list(relevant_data["subdomains"]),
            "ips": list(relevant_data["ips"]),
            "emails": list(relevant_data["emails"]),
        }

    def export_results_to_file(self, domain, results):
        output_file = f"{domain}_exported_results.json"
        try:
            with open(output_file, "w") as file:
                json.dump(results, file, indent=4)
            self.log_message(f"Results exported to {output_file}")
            print(f"Results exported to {output_file}")
        except Exception as e:
            self.log_message(f"Error exporting results: {e}")
            print(f"Error exporting results: {e}")

    def scan_domain(self, domain, passive=False, max_dns_queries=10, timeout=100):
        self.log_message(f"Starting Amass scan for: {domain}")
        print(f"Starting Amass scan for: {domain}")
        raw_results = self.run_amass(domain, passive, max_dns_queries, timeout)

        if "error" in raw_results:
            self.export_results_to_file(domain, raw_results)
            return raw_results

        extracted_results = self.extract_relevant_details(raw_results)
        self.log_message(f"Extracted Results for {domain}: {extracted_results}")
        print(f"Extracted Results: {extracted_results}")

        # Export results to a file
        self.export_results_to_file(domain, {
            "domain": domain,
            "start_time": datetime.now().timestamp(),
            "results": extracted_results
        })

        return extracted_results


# Test the code
if __name__ == "__main__":
    domains = ["google.com"]
    scanner = AmassScanner(amass_path="C:\\Users\\theka\\go\\bin\\amass.exe")
    results = scanner.scan_domain(domains[0], timeout=1000)
    print("\nFinal Results:")
    print(json.dumps(results, indent=4))