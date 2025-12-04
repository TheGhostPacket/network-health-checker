# 🌐 Network Health Checker

A real-time network monitoring dashboard that tracks website and server health with beautiful visualizations and comprehensive analytics.


## ✨ Features

### **Core Monitoring**
- 🟢 **Real-time Health Checks** - Monitor multiple hosts simultaneously
- ⚡ **Response Time Tracking** - Measure and visualize website performance
- 📊 **Interactive Dashboard** - Beautiful, responsive web interface
- 📈 **Historical Analytics** - 24-hour uptime and performance statistics

### **Visual Intelligence**
- 🎯 **Status Indicators** - Color-coded health status (Online/Slow/Offline)
- 📊 **Response Time Charts** - Real-time performance visualization
- 📈 **Uptime Statistics** - Comprehensive availability metrics
- 🔄 **Auto-refresh** - Continuous monitoring with 30-second updates

### **Management Features**
- ➕ **Dynamic Host Management** - Add/remove monitored websites
- 💾 **Data Persistence** - SQLite database for historical tracking
- 🎨 **Modern UI** - Dark theme matching cybersecurity aesthetic
- 📱 **Responsive Design** - Works perfectly on all devices

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- pip package manager

### **Installation**

1. **Clone the repository**
```bash
git clone https://github.com/TheGhostPacket/network-health-checker.git
cd network-health-checker
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Open your browser**
```
http://localhost:5000
```

## 🛠️ Project Structure

```
network-health-checker/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html         # Dashboard interface
├── data/
│   └── health_data.db     # SQLite database (auto-created)
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── screenshots/          # Demo images
```

## 🎯 How It Works

### **Health Check Process**
1. **HTTP Requests** - Sends GET requests to monitored hosts
2. **Response Analysis** - Measures response time and status codes
3. **Status Classification**:
   - 🟢 **Online**: < 500ms response time
   - 🟡 **Slow**: 500ms - 2s response time
   - 🔴 **Offline**: Timeout or connection failed

### **Data Flow**
```
Monitor Hosts → HTTP Checks → Database Storage → Web Dashboard → Real-time Updates
```

## 🔧 Configuration

### **Default Monitored Hosts**
The application comes pre-configured with these hosts:
- Google.com
- GitHub.com
- Stack Overflow
- Python.org
- Flask Documentation

### **Adding Custom Hosts**
- Use the "Add Host" button in the dashboard
- Supports HTTP and HTTPS URLs
- Automatic protocol detection
- Custom display names

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/api/health-check` | GET | Check all monitored hosts |
| `/api/stats` | GET | Get 24-hour statistics |
| `/api/add-host` | POST | Add new host to monitor |
| `/api/host-history/<host>` | GET | Get historical data for host |

## 💻 Technical Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite
- **Charts**: Chart.js
- **Icons**: Font Awesome
- **Styling**: Custom CSS with CSS Grid/Flexbox

## 🔒 Cybersecurity Relevance

This project demonstrates key cybersecurity concepts:

- **Network Monitoring** - Essential for detecting outages and attacks
- **Infrastructure Health** - Monitoring critical services and dependencies  
- **Performance Analysis** - Identifying potential DDoS or resource exhaustion
- **Incident Detection** - Early warning system for service disruptions
- **Data Analytics** - Pattern recognition in network behavior

## 🚀 Deployment

### **Local Development**
```bash
python app.py
# Runs on http://localhost:5000
```

### **Production Deployment**

**Render.com (Recommended)**
1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn app:app`
4. Deploy automatically

**Heroku**
```bash
# Install Heroku CLI, then:
heroku create network-health-checker
git push heroku main
```

## 📈 Future Enhancements

- [ ] **Email Alerts** - Notifications when hosts go down
- [ ] **Multi-location Monitoring** - Check from different geographic locations
- [ ] **Advanced Charts** - Historical trends and predictive analytics
- [ ] **API Authentication** - Secure API access with tokens
- [ ] **Custom Intervals** - Configurable check frequencies
- [ ] **Export Reports** - PDF/CSV report generation
- [ ] **Slack Integration** - Send alerts to Slack channels
- [ ] **Docker Support** - Containerized deployment

## 🎨 Screenshots

### Dashboard Overview
- Real-time status grid
- Response time charts
- Uptime statistics
- Modern dark theme

### Host Management
- Add/remove hosts easily
- Custom display names
- Bulk monitoring capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Links

- **Live Demo**: [Coming Soon]
- **GitHub**: [https://github.com/TheGhostPacket/network-health-checker](https://github.com/TheGhostPacket/network-health-checker)
- **Portfolio**: [https://theghostpacket.com](https://theghostpacket.com)

## 👨‍💻 Author

**TheGhostPacket**
- GitHub: [@TheGhostPacket](https://github.com/TheGhostPacket)
- LinkedIn: [Nhyira Yanney](https://www.linkedin.com/in/nhyira-yanney-b19898178)
- Email: contact@theghostpacket.com

---

⭐ **Star this repository if you found it helpful!**

*Built with ❤️ for the cybersecurity community*
