from basic.api_exceptions import ZipCodeNotFound
from basic.models import ZipCode


def get_zipcode_pk(request):
    zip_code_data = request.data.get("zip_code")
    zip_code = None
    if zip_code_data:
        zip_code = ZipCode.objects.filter(zip_code=zip_code_data).first()
        if not zip_code:
            raise ZipCodeNotFound()
        request.data["zip_code"] = zip_code.id
    return zip_code
