# Running Future Radio OS from a USB stick on Chromebook

This is a portable development/runtime bundle for ChromeOS Linux. It does not replace ChromeOS, install a new operating system, or make the USB executable by ChromeOS on its own.

The supported path is:

1. Enable the Chromebook Linux development environment.
2. Insert the USB stick and copy or clone this repository onto it.
3. In the ChromeOS Files app, right-click the repository directory and choose Share with Linux.
4. Open the Terminal app and run the repository's `scripts/chromebook-usb` launcher.
5. Open the local studio URL in Chrome.

The repository and runtime data remain on the USB stick. The Linux container still owns its normal package cache and system files.

## USB layout

Keep the repository at the top level of the stick when possible:

```text
USB/
└── future-radio-os/
    ├── scripts/chromebook-usb
    ├── pyproject.toml
    ├── uv.lock
    └── ...
```

Do not copy a `.venv` from another machine. Python virtual environments contain platform- and architecture-specific executables. The launcher creates the environment on the Chromebook instead.

## First-time setup

From the shared repository directory in ChromeOS Terminal:

```bash
cd /path/to/future-radio-os
./scripts/chromebook-usb prepare
./scripts/chromebook-usb doctor
```

`prepare` requires either:

- `uv` already installed in the Linux container; or
- Python 3.11 plus `venv` and `pip` available in the container.

The preferred path is `uv`, because `uv.lock` makes dependency resolution reproducible. Install `uv` through its official installation instructions, then run `prepare` again. The launcher does not download or execute an unverified installer.

If the Chromebook's Debian container does not include Python 3.11 and `uv` is unavailable, install the required package through the container's normal package manager, then rerun `prepare`:

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv
```

The exact package availability depends on the ChromeOS Linux container image.

## Run the local station

```bash
./scripts/chromebook-usb run
```

The default bind address is `127.0.0.1` and the default port is `8000`:

```text
http://127.0.0.1:8000/studio/view
```

Override the port without exposing the service to the local network:

```bash
./scripts/chromebook-usb run --port 8123
```

To bind beyond localhost, pass `--host` explicitly. This is not recommended on an untrusted network:

```bash
./scripts/chromebook-usb run --host 0.0.0.0 --port 8000
```

The studio is currently a read-only, in-memory projection seeded by callers. The USB bundle makes the code and local environment portable; it does not claim durable production station state or public availability.

## Commands

```text
prepare       Create/update the Chromebook-local environment and install dev dependencies.
doctor        Check the environment and required local API routes.
test          Run the repository test suite.
run           Start the local API and studio.
help          Print command usage.
```

All commands operate relative to the script's repository root, so they continue to work when the USB is mounted at a different path.

## Safe removal

Stop the server with Ctrl-C, then flush pending writes before ejecting the stick:

```bash
sync
```

Do not remove the USB while `prepare`, `test`, or `run` is writing. SQLite files and generated receipts should be closed before ejecting.

## Known boundaries

- ChromeOS must have Linux development enabled; ChromeOS browser-only mode is not sufficient.
- The USB directory must be shared with Linux before the Terminal app can access it.
- The launcher supports Linux containers on `x86_64` and `aarch64`; native Python dependencies may still vary by Chromebook architecture.
- No external publishing, spending, payment, or provider call is enabled by this setup.
- A USB stick is not a backup. Keep a second copy or push the repository to its remote before carrying the stick.
