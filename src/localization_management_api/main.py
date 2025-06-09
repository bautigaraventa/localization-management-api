from fastapi import FastAPI
from localization_management_api.supabase.queries import fetch_localizations, fetch_all_localizations, get_translation_completion

app = FastAPI()

@app.get("/localizations/{locale}")
async def get_all_localizations(locale: str):
    localizations = await fetch_all_localizations(locale)
    return {
        "locale": locale,
        "localizations": localizations
    }

@app.get("/localizations/{project_id}/{locale}")
async def get_localizations(project_id: str, locale: str):
    localizations = await fetch_localizations(project_id, locale)
    return {
        "project_id": project_id,
        "locale": locale,
        "localizations": localizations
    }

@app.get("/analytics/completion/{project_id}")
async def get_completion(project_id: int):
    data = await get_translation_completion(project_id)
    return data
