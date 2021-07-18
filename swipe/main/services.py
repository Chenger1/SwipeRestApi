from django.http import HttpResponse
from django.utils.encoding import escape_uri_path

import mimetypes

mimetypes.types_map['.docx'] = 'application/msword'  # mimetypes library doesnt contain '.docx' extension


def generate_http_response_to_download(instance):
    """
    Get instance of available models and generate HttpResponse with file - to download
    :param instance: Document, Attachment
    :return: HttpResponse
    """

    with open(instance.file.path, 'rb') as file:
        file_name = instance.file.name.split('/')[-1].encode('utf-8')

        response = HttpResponse(file, content_type=mimetypes.guess_type(instance.file.name)[0])
        response['Content-Disposition'] = f'attachment; filename={escape_uri_path(file_name)}'
        return response
