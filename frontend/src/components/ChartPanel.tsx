import React from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

interface ChartPanelProps {
  vectorData: any;
  rasterData: any;
}

const ChartPanel: React.FC<ChartPanelProps> = ({ vectorData, rasterData }) => {
  // Mock data for NDVI time series
  const ndviData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: 'NDVI Index',
        data: [0.2, 0.25, 0.3, 0.4, 0.5, 0.65, 0.7, 0.75, 0.6, 0.5, 0.4, 0.3],
        borderColor: 'rgb(75, 192, 75)',
        backgroundColor: 'rgba(75, 192, 75, 0.5)',
      },
    ],
  };

  // Mock data for rainfall trends
  const rainfallData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: 'Rainfall (mm)',
        data: [20, 30, 45, 60, 120, 250, 300, 280, 150, 70, 40, 25],
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
      },
    ],
  };

  return (
    <div className="chart-panel">
      <h3>Data Visualization</h3>
      
      {/* NDVI Time Series Chart */}
      <div className="chart-container">
        <h4>NDVI Vegetation Index (Annual)</h4>
        <Line 
          data={ndviData}
          options={{
            responsive: true,
            plugins: {
              legend: {
                position: 'top' as const,
              },
              title: {
                display: false,
              },
            },
          }}
        />
      </div>
      
      {/* Rainfall Chart */}
      <div className="chart-container">
        <h4>Monthly Rainfall Distribution</h4>
        <Bar
          data={rainfallData}
          options={{
            responsive: true,
            plugins: {
              legend: {
                position: 'top' as const,
              },
              title: {
                display: false,
              },
            },
          }}
        />
      </div>
    </div>
  );
};

export default ChartPanel;