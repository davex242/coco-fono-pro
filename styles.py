def load_styles():
    return """
    <style>
        .main {
            background-color: #0f172a;
        }

        section[data-testid="stSidebar"] {
            background-color: #111827;
            border-right: 1px solid #1f2937;
        }

        .sidebar-title {
            font-size: 22px;
            font-weight: 700;
            color: white;
        }

        .card {
            background-color: #1e293b;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
        }

        .metric-title {
            font-size: 14px;
            color: #9ca3af;
        }

        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: white;
        }
    </style>
    """