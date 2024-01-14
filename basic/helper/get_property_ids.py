from basic.api_exceptions import ZipCodeNotFound
from basic.models import ZipCode, ScoutHierarchy
from rest_framework.request import Request


def get_zipcode(request: Request) -> int | None:
    # zip_code could be
    # 1. id of zip_code object = 413
    # 2 string of zip_code = "53113"
    # 3. dict = {"id": 1, "zip_code": "53113"}
    # 4. None

    zip_code_data = request.data.get("zip_code")

    if not zip_code_data:
        return None

    zip_code: ZipCode | None = None
    zip_code_filter: dict = {}

    # handle dict case 3
    if isinstance(zip_code_data, dict):
        if zip_code_data.get("id"):
            zip_code_filter = {"id": zip_code_data.get("id")}
        else:
            zip_code_var = zip_code_data.get("zip_code")
            if zip_code_var:
                zip_code_filter = {"zip_code": zip_code_var}

    # handle case 1
    if isinstance(zip_code_data, int):
        zip_code_filter = {"id": zip_code_data}

    # handle case 2
    if isinstance(zip_code_data, str):
        zip_code_filter = {"zip_code": zip_code_data}

    if zip_code_filter:
        zip_code = ZipCode.objects.filter(**zip_code_filter).first()
        if not zip_code:
            raise ZipCodeNotFound()

    if zip_code:
        request.data['zip_code'] = zip_code.id

    return zip_code


def get_scout_group(request: Request) -> ScoutHierarchy | None:
    scout_group_var = request.data.get("scout_group")
    scout_group_id: int | None = None

    if isinstance(scout_group_var, dict):
        scout_group_id = request.data["scout_group"].get('id')
    elif isinstance(scout_group_var, int):
        scout_group_id = request.data["scout_group"]

    if scout_group_id:
        scout_group = ScoutHierarchy.objects.filter(id=scout_group_id).first()
    else:
        scout_group = request.user.person.scout_group

    if scout_group:
        request.data['scout_group'] = scout_group.id

    return scout_group
