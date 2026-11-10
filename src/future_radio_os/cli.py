import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Future Radio OS local API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run("future_radio_os.app:app", host=args.host, port=args.port, reload=False)
