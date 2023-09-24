import React,  { useState }from 'react';
import Plot from 'react-plotly.js';

function BasketballCourt() {
    // Define the ellipse_arc function using JavaScript
    const ellipse_arc = ({
    x_center = 0,
    y_center = 0,
    a = 10.5,
    b = 10.5,
    start_angle = 0.0,
    end_angle = 2 * Math.PI,
    N = 200
} = {}) => {
        const t = Array.from({ length: N }, (_, i) => start_angle + i * (end_angle - start_angle) / (N - 1));
        const x = t.map(angle => x_center + a * Math.cos(angle));
        const y = t.map(angle => y_center + b * Math.sin(angle));
        let path = `M ${x[0]}, ${y[0]}`;
        for (let k = 1; k < N; k++) {
            path += `L${x[k]}, ${y[k]}`;
        }
        return path;
    };

    // Define the shapes and layout for the basketball court using the ellipse_arc function
    const threept_break_y = 89.47765084;
    const three_line_col = "black";
    const main_line_col = "black";
    const basket = "#981717";

    const shapes = [
        // ... (Add the shapes here using the ellipse_arc function and other logic from the original function)
        {
            type: "rect", // court outline
            x0: -250,
            y0: -52.5,
            x1: 250,
            y1: 417.5,
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "rect", // rectangle resembling the key
            x0: -80,
            y0: -52.5,
            x1: 80,
            y1: 137.5,
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "rect", // rectangle encasing restricted-area and basket
            x0: -60,
            y0: -52.5,
            x1: 60,
            y1: 137.5,
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "circle", // free-throw circle
            x0: -60,
            y0: 77.5,
            x1: 60,
            y1: 197.5,
            xref: 'x',
            yref: 'y',
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "line", // free-throw line
            x0: -60,
            y0: 137.5,
            x1: 60,
            y1: 137.5,
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "rect", // rim-holder
            x0: -2,
            y0: -7.25,
            x1: 2,
            y1: -12.5,
            line: { color: basket, width: 2 },
            fillcolor: basket,
        },
        {
            type: "circle", // rim circle
            x0: -7.5,
            y0: -7.5,
            x1: 7.5,
            y1: 7.5,
            xref: 'x',
            yref: 'y',
            line: { color: basket, width: 3 },
        },
        {
            type: "line", // backboard line
            x0: -30,
            y0: -12.5,
            x1: 30,
            y1: -12.5,
            line: { color: basket, width: 5 },
        },
        {
            type: "path", // restricted area arc
            path: ellipse_arc({a: 40, b: 40, start_angle: 0, end_angle: Math.PI}),
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "path", // 3pt line arc
            path: ellipse_arc({a: 237.5, b: 237.5, start_angle: 0.38628310, end_angle: Math.PI - 0.38628310}),
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "line", // vertical line marking start of 3pt circle (left of basket if south of backboard is endline)
            x0: -220,
            y0: -52.5,
            x1: -220,
            y1: threept_break_y,
            line: { color: three_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "line", // vertical line marking start of 3pt circle (right of basket if south of backboard is endline)
            x0: 220,
            y0: -52.5,
            x1: 220,
            y1: threept_break_y,
            line: { color: three_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "line", // horizontal line marking start of 3pt circle (left of basket if south of backboard is endline)
            x0: -250,
            y0: 227.5,
            x1: -220,
            y1: 227.5,
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "line", // horizontal line marking start of 3pt circle (right of basket if south of backboard is endline)
            x0: 250,
            y0: 227.5,
            x1: 220,
            y1: 227.5,
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "line", // 4th line from the key (left of basket if south of backboard is endline)
            x0: -90,
            y0: 17.5,
            x1: -80,
            y1: 17.5,
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "line", // 3rd line from the key (left of basket if south of backboard is endline)
            x0: -90,
            y0: 27.5,
            x1: -80,
            y1: 27.5,
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "line", // 2nd line from the key (left of basket if south of backboard is endline)
            x0: -90,
            y0: 57.5,
            x1: -80,
            y1: 57.5,
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "line", // 1st line from the key (left of basket if south of backboard is endline)
            x0: -90,
            y0: 87.5,
            x1: -80,
            y1: 87.5,
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "line", // 4th line from the key (right of basket if south of backboard is endline)
            x0: 90,
            y0: 17.5,
            x1: 80,
            y1: 17.5,
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "line", // 3rd line from the key (right of basket if south of backboard is endline)
            x0: 90,
            y0: 27.5,
            x1: 80,
            y1: 27.5,
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "line", // 2nd line from the key (right of basket if south of backboard is endline)
            x0: 90,
            y0: 57.5,
            x1: 80,
            y1: 57.5,
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "line", // 1st line from the key (right of basket if south of backboard is endline)
            x0: 90,
            y0: 87.5,
            x1: 80,
            y1: 87.5,
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
        {
            type: "path", // half-court semi-circle
            path: ellipse_arc({y_center: 417.5, a: 60, b: 60, start_angle: 0, end_angle: - Math.PI}),
            line: { color: main_line_col, width: 1 },
            layer: 'below'
        },
    ];

    const layout = {
        width: 1000,
        height: 1000 * (470 + 2) / (500 + 2),
        xaxis: {
            range: [-250, 250],
            showgrid: false,
            zeroline: true,
            showline: false,
            ticks: '',
            showticklabels: false,
            fixedrange: true,
        },
        yaxis: {
            range: [-52.5, 417.5],
            scaleanchor: "x",
            scaleratio: 1,
            showgrid: false,
            zeroline: true,
            showline: false,
            ticks: '',
            showticklabels: false,
            fixedrange: true,
        },
        shapes: shapes,
        margin: { l: 0, r: 0, t: 0, b: 0 },
        paper_bgcolor: "#dfbb85",
        plot_bgcolor: "#dfbb85",
    };

     // State for player_id input, shots data, and player_name
     const [playerId, setPlayerId] = useState('');
     const [shotsData, setShotsData] = useState([]);
     const [playerName, setPlayerName] = useState('');
 
     // Function to fetch shots data based on player_id
     const fetchShots = async () => {
         try {
             const response = await fetch(`/api/shots?player_id=${playerId}`);
             const data = await response.json();
             setShotsData(data.shots);
 
             // Assuming the player_name is consistent across all shots for the player
             if (data.shots.length > 0) {
                 setPlayerName(data.shots[0].player_name);
             } else {
                 setPlayerName(''); // Reset player name if no shots found
             }
         } catch (error) {
             console.error("Failed to fetch shots:", error);
         }
     };
 
     return (
         <div>
             {/* Input for player_id and display player_name */}
             <div>
                 <label>Enter Player ID: </label>
                 <input 
                     type="number" 
                     value={playerId} 
                     onChange={e => setPlayerId(e.target.value)} 
                 />
                 <button onClick={fetchShots}>Fetch Shots</button>
                 {playerName && <span>Player Name: {playerName}</span>}
             </div>
 
             {/* Basketball Court Visualization */}
             <Plot
                 data={[
                     {
                         x: shotsData.map(shot => shot.x_shot_pos),
                         y: shotsData.map(shot => shot.y_shot_pos),
                         type: 'scatter',
                         mode: 'markers',
                         marker: { color: 'red', size: 20 }
                     }
                 ]}
                 layout={layout}
                 config={{ 
                     staticPlot: false, 
                     displayModeBar: true, 
                     scrollZoom: false, 
                     responsive: true 
                 }}
             />
         </div>
     );
 }

export default BasketballCourt;
