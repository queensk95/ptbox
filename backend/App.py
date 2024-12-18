from flask import Flask, request, jsonify, send_file, send_from_directory
from utils.harvester import harvest_info
from utils.toolamass import AmassScanner
from utils.results_combiner import combine_results
from utils.exporter import export_to_excel
import os
import time
import asyncio

# Absolute path to the React build folder
STATIC_FOLDER = r"C:\Users\theka\PycharmProjects\final\frontend\build"

# Initialize Flask app
app = Flask(
    __name__,
    static_folder=STATIC_FOLDER,
    static_url_path=""
)

# Temporary directory for storing exported files
TEMP_DIR = "temp_results"
os.makedirs(TEMP_DIR, exist_ok=True)

# Initialize Amass scanner
amass_scanner = AmassScanner(amass_path="C:\\Users\\theka\\go\\bin\\amass.exe")


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    """
    Serve React frontend files or fall back to index.html for React routing.
    """
    full_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


@app.route("/scan", methods=["POST"])
def scan():
    """
    Endpoint to run theHarvester, Amass, or both tools on a domain.
    """
    data = request.json
    domain = data.get("domain")
    tool = data.get("tool")

    if not domain or tool not in ["theHarvester", "Amass", "both"]:
        return jsonify({"error": "Invalid input"}), 400

    start_time = time.time()
    combined_results = []

    # Run theHarvester if requested
    if tool in ["theHarvester", "both"]:
        try:
            harvester_results = asyncio.run(harvest_info(domain))
            combined_results.append(harvester_results)
        except Exception as e:
            print(f"Error running theHarvester: {e}")
            combined_results.append({"error": f"Error running theHarvester: {str(e)}"})

    # Run Amass if requested
    if tool in ["Amass", "both"]:
        try:
            amass_results = amass_scanner.scan_domain(domain)
            combined_results.append(amass_results)
        except Exception as e:
            print(f"Error running Amass: {e}")
            combined_results.append({"error": f"Error running Amass: {str(e)}"})

    # Combine and deduplicate results
    final_results = combine_results(combined_results)

    end_time = time.time()

    # Prepare scan data for response
    scan_data = {
        "domain": domain,
        "start_time": start_time,
        "end_time": end_time,
        "results": final_results
    }

    # Export to Excel
    result_file = os.path.join(TEMP_DIR, f"{domain}_results.xlsx")
    try:
        export_to_excel(scan_data, result_file)
    except Exception as e:
        print(f"Error exporting results to Excel: {e}")

    return jsonify(scan_data), 200


@app.route("/export", methods=["GET"])
def export():
    """
    Endpoint to export scan results as an Excel file.
    """
    domain = request.args.get("domain")
    file_path = os.path.join(TEMP_DIR, f"{domain}_results.xlsx")
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404


@app.route("/test", methods=["GET"])
def test():
    """
    Test endpoint to ensure the server is running correctly.
    """
    return jsonify({
        "status": "success",
        "message": "Test endpoint is working!",
        "tools": {
            "theHarvester": "Configured",
            "Amass": "Configured"
        }
    }), 200


if __name__ == "__main__":
    # Print static folder path for debugging
    print("Static folder path:", app.static_folder)
    app.run(debug=True, host="0.0.0.0")
