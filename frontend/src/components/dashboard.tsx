import axios from "axios";
import { useState, useEffect } from "react";
import { Bar } from "react-chartjs-2";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from "chart.js";

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

// Define TypeScript interface for the dashboard data
interface DashboardData {
    active_loans: number;
    books_lent: number;
    total_loans: number;
    loans_per_title: { [key: string]: number };
    all_loans: Array<{
        duration: number | null;
        loan_date: string;
        return_date: string | null;
        title: string;
        username: string;
    }>;
}

const Dashboard: React.FC = () => {
    const [data, setData] = useState<DashboardData>({
        active_loans: 0,
        books_lent: 0,
        total_loans: 0,
        loans_per_title: {},
        all_loans: [],
    });

    useEffect(() => {
        axios
            .get("/api/dashboard")  // Use proxy path
            .then((response) => {
                console.log("Dashboard data:", response.data);
                setData(response.data);
            })
            .catch((error) => {
                console.error("Error fetching dashboard data:", error);
            });
    }, []);

    // Prepare chart data for loans_per_title
    const chartData = {
        labels: Object.keys(data.loans_per_title),  // ["Book 1", "Book 2"]
        datasets: [
            {
                label: "Loans per Title",
                data: Object.values(data.loans_per_title),  // [1, 1]
                backgroundColor: "rgba(75, 192, 192, 0.6)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1,
            },
        ],
    };

    // Chart options
    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: "top" as const,
            },
            title: {
                display: true,
                text: "Loans per Book Title",
            },
        },
    };

    return (
        <div>
            <h1 className="font-bold m-4 ml-2.5 mr-2.5 mb-4 border-b-2 text-center  text-4xl   ">Dashboard</h1>
            <p className="text-2xl flex-col text-center ">Welcome to the dashboard</p>
            <div className="flex flex-col items-baseline justify-center ml-8 text-xl">
            <h2>Total Loans: {data.total_loans}</h2>
            <h2>Active Loans: {data.active_loans}</h2>
            <h2>Books Lent: {data.books_lent}</h2>
            </div>
            
            <div style={{ width: "900px", margin: "20px auto" }}>
                <Bar data={chartData} options={options} />
            </div>
        </div>
    );
};

export default Dashboard;