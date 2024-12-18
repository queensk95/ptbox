import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [domain, setDomain] = useState("");
  const [tool, setTool] = useState("theHarvester");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [testMessage, setTestMessage] = useState("");

  const handleScan = async () => {
    if (!domain) {
      setError("Please enter a domain.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await axios.post("/scan", { domain, tool });
      console.log("API Response for Scan:", response.data); // Debug log

      const { data } = response;
      if (data && data.results) {
        setResults([...results, data]);
      } else {
        setError("No results found.");
      }
    } catch (err) {
      console.error(err);
      setError("Error occurred while scanning the domain.");
    }

    setLoading(false);
  };

  const handleExport = async (domainToExport) => {
    console.log("Exporting domain:", domainToExport); // Debug log
    try {
      const response = await axios.get(`/export?domain=${domainToExport}`, {
        responseType: "blob",
      });
      console.log("Export Response:", response); // Debug log

      const blob = new Blob([response.data], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = `${domainToExport}_results.xlsx`;
      link.click();
    } catch (err) {
      console.error(err);
      setError("Error exporting results.");
    }
  };

  const handleTest = async () => {
    setTestMessage("Testing...");
    try {
      const response = await axios.get("/test");
      const { data } = response;
      setTestMessage(`Test Successful: ${data.message}`);
    } catch (err) {
      console.error(err);
      setTestMessage("Test Failed: Unable to connect to the server.");
    }
  };

  return (
    <div className="App">
      <h1>OSINT Web Application</h1>

      <div>
        <button onClick={handleTest}>Test Server</button>
        {testMessage && <div className="test-message">{testMessage}</div>}
      </div>

      <div>
        <input
          type="text"
          placeholder="Enter domain (e.g., google.com)"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
        />
        <select value={tool} onChange={(e) => setTool(e.target.value)}>
          <option value="theHarvester">theHarvester</option>
          <option value="Amass">Amass</option>
          <option value="both">Both</option>
        </select>
        <button onClick={handleScan} disabled={loading}>
          {loading ? "Scanning..." : "Scan"}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="results">
        {results.map((result, index) => (
          <div key={index} className="result-card">
            <h3>{result.domain}</h3>
            <p>Start Time: {new Date(result.start_time * 1000).toLocaleString()}</p>
            <p>End Time: {new Date(result.end_time * 1000).toLocaleString()}</p>
            <button onClick={() => handleExport(result.domain)}>Export to Excel</button>
            <details>
              <summary>View Details</summary>
              <pre>
                <strong>Emails:</strong> {JSON.stringify(result.results.emails, null, 2)}{"\n"}
                <strong>Hosts:</strong> {JSON.stringify(result.results.hosts, null, 2)}{"\n"}
                <strong>IPs:</strong> {JSON.stringify(result.results.ips, null, 2)}{"\n"}
                <strong>Geo ASN Info:</strong> {JSON.stringify(result.results.geo_asn_info, null, 2)}
              </pre>
            </details>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
