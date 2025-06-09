# AI/ML Blog Platform

A modern, feature-rich blog platform focused on Artificial Intelligence and Machine Learning content. Built with Django and designed for technical content creators.

##  Features

- **Content Management**
  - Markdown support for rich content creation
  - Image upload and management
  - Category and tag organization
  - Draft and published post states

- **User Management**
  - Custom user model with email authentication
  - Phone number verification
  - Social authentication support
  - User roles and permissions

- **Search & Discovery**
  - Full-text search across posts
  - Category-based filtering
  - Author filtering
  - Date range filtering
  - Search analytics

- **Modern UI/UX**
  - Responsive design
  - Clean and intuitive interface
  - Mobile-friendly layout
  - Real-time search results

## Tech Stack

- **Backend**
  - Django 5.0
  - Python 3.10
  - Django Markdownx
  - Django AllAuth
  - Google Cloud Storage

- **Frontend**
  - HTML5
  - CSS3
  - JavaScript
  - Responsive Design

- **Infrastructure**
  - Docker
  - Google Cloud Storage
  - SQLite (Development)
  - PostgreSQL (Production-ready)

##  Getting Started

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- Google Cloud account (for storage)
- Phone number verification service

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aiml-blog.git
   cd aiml-blog
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Using Docker:
   ```bash
   docker-compose up --build
   ```

4. Without Docker:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

### Configuration

1. Set up Google Cloud Storage:
   - Create a service account
   - Download the service account key
   - Mount the key in Docker or set the environment variable

2. Configure phone verification:
   - Set up your phone verification service
   - Update the settings in `core/settings.py`

##  Usage

### Creating Posts

1. Log in to your account
2. Click "Write Post" in the navigation
3. Use Markdown for content formatting
4. Add categories and tags
5. Upload images if needed
6. Save as draft or publish

### Managing Content

- Use the admin interface at `/admin`
- Filter posts by status, author, or category
- Edit or delete existing posts
- Manage user permissions

### Search Functionality

- Use the search bar in the navigation
- Filter results by:
  - Category
  - Author
  - Date range
- Sort by relevance or date

## 🔧 Development

### Project Structure


### Running Tests

```bash
python manage.py test
```

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Document functions and classes
- Write unit tests for new features

##  Security

- CSRF protection enabled
- XSS protection
- Secure password hashing
- Phone number verification
- Google Cloud Storage security

## Analytics

- Search analytics tracking
- Post view counting
- User engagement metrics

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Django community
- Markdownx for rich text editing
- Google Cloud Platform
- All contributors and users

##  Support

For support, please:
- Open an issue
- Contact the maintainers
- Check the documentation

##  Updates

Stay updated with the latest changes by:
- Watching the repository
- Following the release notes
- Checking the changelog
