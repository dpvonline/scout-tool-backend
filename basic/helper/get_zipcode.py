from basic.api_exceptions import ZipCodeNotFound
from basic.models import ZipCode
from rest_framework.request import Request


def get_zipcode_pk(request) -> int:
    # zip_code could be
    # 1. id of zip_code object = 413
    # 2 string of zip_code = "53113"
    # 3. dict = {"id": 1, "zip_code": "53113"}
    # 4. None

    zip_code_data = request.data.get("zip_code")
    zip_code = None

    # handle case 1
    if zip_code_data and type(zip_code_data) is int:
        zip_code_obj = ZipCode.objects.filter(id=zip_code_data).first()
        if not zip_code_obj:
            raise ZipCodeNotFound()
        zip_code = zip_code_obj.id

    # handle case 2
    if zip_code_data and type(zip_code_data) is str:
        zip_code_obj = ZipCode.objects.filter(zip_code=zip_code_data).first()
        if not zip_code_obj:
            raise ZipCodeNotFound()
        zip_code = zip_code_obj.id

    # handle dict case 3
    if zip_code_data and type(zip_code_data) is dict:
        zip_code = zip_code_data.get("id")

    return zip_code
