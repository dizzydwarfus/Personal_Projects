import React, { useState } from 'react';
import './App.css';
import BasketballCourt from './BasketballCourt';
import DynamicTable from './DynamicTable';

function App() {
    const [tableData, setTableData] = useState([]);
    const [endpoint, setEndpoint] = useState('');  // State to store user input

    const fetchDataFromEndpoint = async () => {
        try {
            const response = await fetch(`http://localhost:5000/api/${endpoint}`);
            const data = await response.json();
            setTableData(data[endpoint]);  // Assuming the response object has a key named after the endpoint
        } catch (error) {
            console.error(`Failed to fetch data from /api/${endpoint}:`, error);
        }
    };

    return (
        <div className="App-container">
            <h1>Basketball Court Visualizer</h1>
            <BasketballCourt />

            <h1>Dynamic Table</h1>
            <div>
                <input 
                    type="text" 
                    placeholder="Enter endpoint (e.g., 'tables')" 
                    value={endpoint}
                    onChange={(e) => setEndpoint(e.target.value)}
                />
                <button onClick={fetchDataFromEndpoint}>Fetch Data</button>
            </div>
            <DynamicTable data={tableData} />
        </div>
    );
}

export default App;
