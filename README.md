# Spotify Playlist CLI Downloader (FLAC Format)

A simple command-line tool to download Spotify playlists in FLAC format.

## Getting Started

### Prerequisites

Ensure you have Python installed, then install the required dependencies:

```sh
pip install -r requirements.txt
```

### Setup

1. Create a `.env` file in the project directory.
2. Add your Spotify API credentials:

```
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
```

## Usage

Run the following command to download a playlist:

```sh
python gnomify.py -u "[PLAYLIST_LINK]"
```

The downloaded playlist will be saved in the same directory where the script is located.



