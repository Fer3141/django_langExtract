from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import langextract as lx
import csv, os, textwrap

def home_view(request):
    return HttpResponse("Welcome to the Language Extractor Home Page!")


def csv_view(request):
    csv_file_path = r'C:\Users\maria\OneDrive\Documentos\DJANGO-LANG\ejemplo.csv'

    if not os.path.exists(csv_file_path):
        return HttpResponse("CSV file not found.")

    prompt = textwrap.dedent("""Extrae PERSONAS (nombres propios) y FECHAS en orden de aparición. Usa texto EXACTO del documento.""")

    examples = [
        lx.data.ExampleData(
            text="Reunion con Roberto a las 3pm el 5 de Mayo de 2023.",
            extractions=[
                lx.data.Extraction(extraction_class="PERSON", extraction_text="Roberto"),
                lx.data.Extraction(extraction_class="DATE", extraction_text="5 de Mayo de 2023"),
            ],
        ),
    ]

    api_key = os.getenv("LANGEXTRACT_API_KEY")
    if not api_key:
        return HttpResponse("API key not found in environment variables.")


    results = []
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        if "columna" not in (reader.fieldnames or []):
            return HttpResponse("CSV file does not contain 'columna' header.")

        for idx, row in enumerate(reader):
            text = (row.get("columna") or "").strip()
            if not text:
                continue

            res = lx.extract(
                text_or_documents=text,
                prompt_description=prompt,
                examples=examples,
                model_id="gemini-2.5-flash",
                api_key=api_key,
                extraction_passes=1, # cuantas pasadas a la linea para extraer cosas
                max_char_buffer=1200,
            )

            extr = [
                {
                    "class": e.extraction_class,
                    "text": e.extraction_text,
                    #"attrs": e.attributes or {},
                    #"start": getattr(e.char_interval, "start_pos", None),
                    #"end": getattr(e.char_interval, "end_pos", None),
                }
                for e in getattr(res, "extractions", [])
            ]

            if extr:
                results.append({
                    "row": idx,
                # "input": text[:160],
                    "extractions": extr,
                })

    return JsonResponse({"ok": True, "results": results}, json_dumps_params={"ensure_ascii": False})