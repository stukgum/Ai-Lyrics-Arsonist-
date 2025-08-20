# BeatLyrics - AI-Powered Beat-Synced Lyric Generation

BeatLyrics is a comprehensive web application that analyzes audio files and generates perfectly timed lyrics synchronized to beats, bars, and musical structure. Built with Next.js, FastAPI, and advanced audio processing libraries.

## 🎵 Features

- **Audio Analysis**: Advanced beat detection, tempo analysis, key estimation, and section segmentation
- **AI Lyric Generation**: Generate high-quality lyrics aligned to musical structure using OpenAI
- **Interactive Editor**: Waveform visualization with beat overlay and drag-to-edit functionality  
- **Multiple Export Formats**: LRC, SRT, TXT, and professional PDF outputs
- **URL Support**: Process YouTube links and direct audio URLs with rights confirmation
- **Production Ready**: Docker deployment, monitoring, and comprehensive testing

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (required)
- YouTube Data API key (optional, for URL processing)

### Local Development

1. **Clone and setup**:
   \`\`\`bash
   git clone <repository-url>
   cd beatlyrics-app
   cp secrets.example.env .env
   \`\`\`

2. **Configure API keys** in `.env`:
   \`\`\`env
   OPENAI_API_KEY=sk-your-openai-api-key-here
   YOUTUBE_API_KEY=your-youtube-api-key-here  # optional
   \`\`\`

3. **Start the application**:
   \`\`\`bash
   chmod +x run_local.sh
   ./run_local.sh
   \`\`\`

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🏗️ Architecture

### Frontend (Next.js + TypeScript)
- **Pages**: Home, Upload, Job Status, Editor, Exports, Account
- **Audio**: wavesurfer.js for waveform visualization, howler.js for playback
- **UI**: shadcn/ui components with Tailwind CSS

### Backend (FastAPI + Python)
- **API**: RESTful endpoints for upload, analysis, generation, and export
- **Workers**: Celery workers for audio processing and AI generation
- **Storage**: PostgreSQL for metadata, Redis for queues, S3 for files

### Audio Processing Pipeline
1. **Ingest**: Upload or URL download with rights confirmation
2. **Transcode**: Convert to 16-bit 44.1kHz WAV using ffmpeg
3. **Analysis**: Extract beats, tempo, key, and structure using librosa/madmom
4. **Generation**: AI-powered lyric creation with OpenAI function calling
5. **Export**: Generate LRC, SRT, TXT, and PDF formats

## 🔧 API Endpoints

\`\`\`
POST /api/v1/upload          # Upload audio file
POST /api/v1/ingest-url      # Process audio URL
GET  /api/v1/jobs/:id/status # Check processing status
GET  /api/v1/jobs/:id/features # Get audio analysis
POST /api/v1/generate        # Generate lyrics
GET  /api/v1/generation/:id  # Get generated lyrics
POST /api/v1/export/:id      # Export in various formats
\`\`\`

## 🧪 Testing

Run the complete test suite:
\`\`\`bash
./run_tests.sh
\`\`\`

Individual test categories:
\`\`\`bash
npm test                    # Frontend tests
docker-compose exec backend pytest tests/ -v  # Backend tests
\`\`\`

## 🔐 Security & Legal

- **Rights Confirmation**: Required modal for URL processing with audit logging
- **Content Moderation**: OpenAI moderation API integration
- **Data Protection**: Secure file handling and user data encryption
- **Terms of Service**: Included template for deployment

## 📦 Deployment

### Docker Compose (Development)
\`\`\`bash
docker-compose up -d
\`\`\`

### Kubernetes (Production)
\`\`\`bash
helm install beatlyrics ./deploy/helm/
\`\`\`

### Environment Variables
See `secrets.example.env` for complete configuration options.

## 🎼 Audio Format Support

**Supported Formats**: WAV, MP3, M4A, AAC, OGG, FLAC (up to 200MB)
**URL Sources**: YouTube (with consent), direct HTTP links
**Output**: 16-bit 44.1kHz/48kHz WAV for processing

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For issues and support, please open a GitHub issue or contact the development team.
