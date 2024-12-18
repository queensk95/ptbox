import React, { useState } from 'react';
import { initiateScan } from '../api/api'; // Import the reusable API function

function ScanForm({ onScanComplete }) {
    const [domain, setDomain] = useState('');
    const [tool, setTool] = useState('theHarvester');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleScan = async () => {
        setLoading(true);
        setError('');
        try {
            const results = await initiateScan(domain, tool); // Use the function from api.js
            onScanComplete(results);
        } catch (err) {
            console.error(err);
            setError('Failed to initiate scan. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <input
                type="text"
                placeholder="Enter domain"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
            />
            <select value={tool} onChange={(e) => setTool(e.target.value)}>
                <option value="theHarvester">theHarvester</option>
                <option value="Amass">Amass</option>
            </select>
            <button onClick={handleScan} disabled={loading}>
                {loading ? 'Scanning...' : 'Scan'}
            </button>
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    );
}

export default ScanForm;
