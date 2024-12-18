import axios from "axios";

const API_BASE_URL = "http://localhost:5000"; // Change if the backend URL is different

/**
 * Initiate a scan using the selected tool.
 * @param {string} domain - The domain to scan (e.g., "example.com").
 * @param {string} tool - The tool to use ("theHarvester" or "Amass").
 * @returns {Promise<object>} - The scan results.
 */
export const initiateScan = async (domain, tool) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/scan`, { domain, tool });
        return response.data;
    } catch (error) {
        console.error("Error initiating scan:", error);
        throw error.response?.data || { error: "An unexpected error occurred" };
    }
};

/**
 * Export scan results as an Excel file.
 * @param {string} domain - The domain whose results should be exported.
 * @returns {Promise<Blob>} - The exported Excel file.
 */
export const exportResults = async (domain) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/export`, {
            params: { domain },
            responseType: "blob", // Ensure the response is treated as a file
        });
        return response.data;
    } catch (error) {
        console.error("Error exporting results:", error);
        throw error.response?.data || { error: "An unexpected error occurred" };
    }
};
