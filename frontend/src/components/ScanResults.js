import React from 'react';

function ScanResults({ scan }) {
    return (
        <div className="scan-card">
            <h3>Domain: {scan.domain}</h3>
            <p>Start: {new Date(scan.start_time * 1000).toLocaleString()}</p>
            <p>End: {new Date(scan.end_time * 1000).toLocaleString()}</p>
            <p>Subdomains: {scan.results.subdomains.join(', ')}</p>
            <p>Emails: {scan.results.emails.join(', ')}</p>
        </div>
    );
}

export default ScanResults;
