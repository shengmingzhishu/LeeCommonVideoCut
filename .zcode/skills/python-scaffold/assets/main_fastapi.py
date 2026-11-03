from fastapi import FastAPI

from {{ package_name }}.config import settings

app = FastAPI(title=settings.project_name)


@app.get("/")
def read_root():
    return {"message": f"Starting {settings.project_name} in {settings.environment} mode..."}


# ─── 子路由注册 ───


def main():
    """Main entry point for local execution."""
    import uvicorn

    uvicorn.run("{{ package_name }}.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
