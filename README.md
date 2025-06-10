# Odoo MCP Server
# 🎯 Odoo MCP Server

An AI-powered CRM automation tool that integrates Claude AI with Odoo ERP systems using the Model Context Protocol (MCP).

## 🚀 Features

- **🤖 AI Lead Classification**: Automatically classify leads using Claude AI and BANT methodology (Budget, Authority, Need, Timeline)
- **📝 Smart Lead Creation**: Create CRM leads with intelligent salesperson auto-assignment
- **📊 Project Management**: Retrieve and manage Odoo project tasks
- **🔄 Real-time Integration**: Seamless connection between Claude conversations and Odoo CRM
- **🎨 User-Friendly Interface**: Clean Gradio web interface for easy interaction

## 📋 Prerequisites

- Python 3.8+
- Access to an Odoo instance (URL, database, credentials)
- Claude API key from Anthropic
- Required Python packages (see requirements.txt)

## ⚡ Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd odoo-mcp-server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   # Odoo Configuration
   ODOO_URL=https://your-odoo-instance.com
   ODOO_DB=your_database_name
   ODOO_USERNAME=your_username
   ODOO_PASSWORD_OR_API_KEY=your_password_or_api_key
   
   # Claude AI Configuration
   CLAUDE_API_KEY=your_claude_api_key
   ```

4. **Test your Odoo connection**
   ```bash
   python test_connection.py
   ```

5. **Launch the application**
   ```bash
   python app.py
   ```

6. **Open your browser** to `http://localhost:7860`

## 🛠️ Core Components

### Lead Classification with BANT
The AI analyzes email content and classifies leads based on:
- **Budget**: Financial capacity assessment
- **Authority**: Decision-making power
- **Need**: Urgency and importance
- **Timeline**: When they need a solution

### Smart Auto-Assignment
- Automatically assigns salespeople based on email domain matching
- Prioritizes leads from known companies
- Updates lead status based on qualification

### Project Task Management
- Retrieve tasks from specific Odoo projects
- Filter and limit results for focused management
- Real-time project status updates

## 📖 Usage Examples

### Creating a Lead
```python
# Through the web interface or programmatically
result = mcp_create_odoo_lead(
    lead_title="Enterprise Software Inquiry",
    company="Tech Corp",
    contact="Jane Smith",
    email_address="jane@techcorp.com",
    phone_number="+1-555-0199",
    notes="Interested in our enterprise solution"
)
```

### AI Lead Classification
```python
# Classify an email and update the lead
email_content = """
Hi, I'm the CTO at StartupXYZ. We're looking for a CRM solution 
for our 50-person team. Our budget is around $10k annually, and 
we need something implemented within the next 2 months. 
Can you help?
"""

result = mcp_classify_and_update_lead(
    email_text=email_content,
    email_address="cto@startupxyz.com"
)
```

## 🔧 Configuration

### Environment Variables
- `ODOO_URL`: Your Odoo instance URL
- `ODOO_DB`: Database name
- `ODOO_USERNAME`: Odoo username
- `ODOO_PASSWORD_OR_API_KEY`: Password or API key
- `CLAUDE_API_KEY`: Anthropic Claude API key

### Customization
- Modify BANT classification criteria in `app.py`
- Adjust salesperson assignment logic in `odoo_actions.py`
- Customize UI themes and layouts in the Gradio interface

## 🔍 Troubleshooting

### Common Issues

1. **Odoo Connection Failed**
   - Verify your Odoo URL and credentials
   - Check if your Odoo instance allows XML-RPC connections
   - Ensure your user has appropriate permissions

2. **Claude API Errors**
   - Verify your API key is valid and has sufficient credits
   - Check the model name matches available Claude models
   - Review rate limits and usage

3. **JSON Parsing Errors**
   - The app handles markdown code blocks from Claude responses
   - Check Claude's response format in console logs

### Testing Connection
```bash
python3 test_connection.py
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gradio UI     │    │   Claude AI     │    │   Odoo ERP      │
│   (Frontend)    │◄──►│   (MCP Client)  │◄──►│   (Backend)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │              ┌─────────────────┐              │
        └─────────────►│   Python App    │◄─────────────┘
                       │   (MCP Server)  │
                       └─────────────────┘
```

## 🎯 Hackathon Highlights

This project demonstrates:
- **AI Integration**: Seamless Claude AI integration for intelligent lead processing
- **Real-world Application**: Practical CRM automation solving actual business problems
- **Modern Architecture**: MCP protocol implementation for scalable AI-human collaboration
- **User Experience**: Intuitive interface making AI accessible to non-technical users

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Anthropic for Claude AI and MCP protocol
- Odoo for the excellent ERP platform
- Gradio team for the fantastic UI framework