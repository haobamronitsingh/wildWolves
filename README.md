# WildWolves

# First Hackathon project based on tourism

WildWolves is a Django tourism web application focused on discovering places
in Manipur and connecting tourists with local guides and transport options.
It uses Django templates for its interface and SQLite for local development.

## Features

- Browse destination recommendations for Loktak Lake, Kangla Fort, and Shirui
  Hills.
- View nearby cafe recommendations.
- Optionally rank destinations and cafes using YouTube engagement data. Without
  a YouTube API key, the site uses its built-in curated recommendations.
- Register as a tourist or local guide. Tourists can request assistance and
  guides can manage requests from their dashboard.
- Browse ride sharing, local bus and auto routes, and vehicle rental options.
- Use the tourist SOS feature to submit an alert with browser-provided
  coordinates. SMS delivery is not configured; the app logs intended
  recipients instead.

## Requirements

- Windows, macOS, or Linux.
- Python 3.12 or newer recommended.
- `pip` (included with standard Python installations).
- Internet access to install Python packages. Internet access is also needed
  for live YouTube recommendations when an API key is configured.
- A YouTube Data API v3 key is optional. The rest of the application can be
  used without one.

The Python dependencies are listed in [requirements.txt](requirements.txt).
The project uses SQLite, so a separate database server is not required.

## Set up locally

Run these commands from the project root.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_transport
python manage.py runserver
```

If PowerShell does not allow activating the virtual environment, use its
Python executable directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_transport
.\.venv\Scripts\python.exe manage.py runserver
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_transport
python manage.py runserver
```

The `seed_transport` command loads sample local routes and rental listings.
Running it again updates those sample records rather than duplicating them.
It can be skipped if you do not need the sample transport data.

Open **http://127.0.0.1:8000/** in a browser. The SQLite database is created
at the project root as `db.sqlite3` when migrations are applied.

## Optional YouTube recommendations

Create a YouTube Data API v3 key in Google Cloud if you want live popularity
ranking. Add a `.env` file in the project root (the file is ignored by Git):

```dotenv
YOUTUBE_API_KEY=your_api_key
YOUTUBE_RECOMMENDATION_CACHE_SECONDS=900
```

Restart the development server after changing `.env`. The cache duration is in
seconds and defaults to 900 (15 minutes). If the key is missing or a YouTube
request fails, curated recommendations are shown instead.

## Using the application

- **Home (`/`)**: browse and search destinations. Select a place to see cafes
  near it.
- **Cafes (`/cafes/`)**: view cafe recommendations; a destination can be
  selected with a URL such as `/cafes/?spot=Kangla%20Fort`.
- **Tourist account**: use **Register** or **Login** to choose the tourist
  account option. After logging in, use the dashboard to request local guide
  assistance or submit an SOS alert.
- **Local guide account**: use **Register** or **Login** to choose the guide
  option. The guide dashboard supports availability and assistance requests.
- **Transport (`/transport/`)**: browse shared rides, local routes, and
  available private rentals. Some actions require an account.
- **Django admin (`/admin/`)**: manage application data with a staff account.
  Create one with:

  ```powershell
  python manage.py createsuperuser
  ```

  On macOS or Linux, run the same command from the activated virtual
  environment.

## Use from another device on your local network

For a Windows hotspot or LAN demonstration:

1. Connect both devices to the same network.
2. Run `run_network.bat` from the project root.
3. Open the network URL printed by the script on the other device and keep the
   command window open.

The launcher binds Django to port `8000` and may need permission to add a
Windows Firewall rule. This is intended for trusted local networks only. For
manual startup, run `python manage.py runserver 0.0.0.0:8000` and allow inbound
connections to port 8000 as needed.

## Useful commands

```text
python manage.py check          Check Django configuration
python manage.py migrate        Apply database migrations
python manage.py seed_transport Load or update sample transport data
python manage.py test           Run the Django test suite
python manage.py createsuperuser Create an admin account
```

## Project layout

```text
Tourist/          Tourist accounts, dashboard, and assistance/SOS features
localGuide/       Local guide accounts and assistance requests
transport/        Ride sharing, local routes, and vehicle rentals
wildWolves/       Django project settings, homepage, and recommendation service
manage.py         Django management entry point
requirements.txt  Python dependencies
```

## Deployment note

The included settings and Django development server are for local development
and demonstrations, not production. Before deploying publicly, configure a
unique secret key through environment settings, set `DEBUG=False`, restrict
`ALLOWED_HOSTS`, configure a production-ready database and static-file
serving, and run Django's deployment checks. Do not expose the development
server or commit `.env` credentials.
