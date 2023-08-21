import React from 'react';

const DynamicTable = ({ data }) => {
    // Extract column headers from data
    const columns = data[0] ? Object.keys(data[0]) : [];

    return (
        <table border="1">
            <thead>
                <tr>
                    {columns.map((col, index) => (
                        <th key={index}>{col}</th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {data.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                        {columns.map((col, colIndex) => (
                            <td key={colIndex}>{row[col]}</td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

export default DynamicTable;
