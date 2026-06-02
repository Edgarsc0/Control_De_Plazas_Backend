import re

def refactor():
    file_path = '/home/edgar/ANAM/EjeCentral/eje_central_back/plantilla/views.py'
    with open(file_path, 'r') as f:
        content = f.read()

    # Add imports and constant at the top
    if 'from django.db.models.expressions import RawSQL' not in content:
        import_str = "from django.db.models import Count, Q, Sum, Case, When, IntegerField, Max, Subquery, OuterRef\nfrom django.db.models.expressions import RawSQL\n\nLATEST_MOVPOS_RAW_SQL = \"\"\"\n    SELECT id FROM (\n        SELECT id, ROW_NUMBER() OVER (\n            PARTITION BY `Nº Pos Actual` \n            ORDER BY `F Efva` DESC, `Fecha Captura` DESC, `F/H Últ Actz` DESC, id DESC\n        ) as rn\n        FROM MOV_POS\n    ) ranked WHERE rn = 1\n\"\"\"\n"
        content = content.replace(
            "from django.db.models import Count, Q, Sum, Case, When, IntegerField, Max, Subquery, OuterRef\n",
            import_str
        )

    # Replace sub = ... with sub = RawSQL(...)
    old_sub = "sub = MovPos.objects.values('no_pos_actual').annotate(max_id=Max('id')).values('max_id')"
    new_sub = "sub = RawSQL(LATEST_MOVPOS_RAW_SQL, [])"
    content = content.replace(old_sub, new_sub)

    # Replace id__in=Subquery(sub) with id__in=sub
    # Since sub is now RawSQL, we don't need Subquery
    content = content.replace("id__in=Subquery(sub)", "id__in=sub")

    with open(file_path, 'w') as f:
        f.write(content)

    print("Refactored successfully")

if __name__ == '__main__':
    refactor()
