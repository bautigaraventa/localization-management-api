from .client import get_supabase

async def _fetch_localizations_by_keys(keys, locale, supabase):
    if not keys:
        return []

    key_ids = [key["id"] for key in keys]

    translations_response = supabase.table("translations") \
        .select("*") \
        .in_("key_id", key_ids) \
        .eq("locale", locale) \
        .execute()

    translations = translations_response.data
    translations_by_key = {t["key_id"]: t for t in translations}

    result = []
    for key in keys:
        translation = translations_by_key.get(key["id"])
        result.append({
            "id": key["id"],
            "key": key["key"],
            "category": key["category"],
            "value": translation["value"] if translation else "",
            "updatedAt": translation["updated_at"] if translation else None
        })
    return result

async def fetch_all_localizations(locale: str):
    supabase = get_supabase()
    keys_response = supabase.table("translation_keys") \
        .select("*") \
        .execute()
    keys = keys_response.data
    return await _fetch_localizations_by_keys(keys, locale, supabase)
    
async def fetch_localizations(project_id: str, locale: str):
    supabase = get_supabase()
    keys_response = supabase.table("translation_keys") \
        .select("*") \
        .eq("project_id", project_id) \
        .execute()
    keys = keys_response.data
    return await _fetch_localizations_by_keys(keys, locale, supabase)

async def get_translation_completion(project_id: int):
    supabase = get_supabase()

    keys_response = supabase.table("translation_keys") \
        .select("id") \
        .eq("project_id", project_id) \
        .execute()

    keys = keys_response.data
    total_keys = len(keys)

    if total_keys == 0:
        return {}

    key_ids = [key["id"] for key in keys]
    locales = ["en", "es", "pt"]

    completion = {}

    for locale in locales:
        translations_response = supabase.table("translations") \
            .select("key_id") \
            .in_("key_id", key_ids) \
            .eq("locale", locale) \
            .execute()

        translations = translations_response.data or []
        translated_count = len({t["key_id"] for t in translations})
        percent = round((translated_count / total_keys) * 100, 2)
        completion[locale] = percent

    return {
        "project_id": project_id,
        "completion": completion
    }