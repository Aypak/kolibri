import mimetypes
import os
import zipfile

from django.http import Http404
from django.http import HttpResponse
from django.http.response import FileResponse
from django.http.response import HttpResponseNotModified
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.base import View
from le_utils.constants import exercises
from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import urlunparse

from .api import cache_forever
from .utils.paths import get_content_storage_file_path
from kolibri.utils.conf import OPTIONS

# Do this to prevent import of broken Windows filetype registry that makes guesstype not work.
# https://www.thecodingforums.com/threads/mimetypes-guess_type-broken-in-windows-on-py2-7-and-python-3-x.952693/
mimetypes.init([os.path.join(os.path.dirname(__file__), 'constants', 'mime.types')])


def _add_access_control_headers(request, response):
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    requested_headers = request.META.get("HTTP_ACCESS_CONTROL_REQUEST_HEADERS", "")
    if requested_headers:
        response["Access-Control-Allow-Headers"] = requested_headers


def get_referrer_url(request):
    if request.META.get('HTTP_REFERER'):
        # If available use HTTP_REFERER to infer the host as that will give us more
        # information if Kolibri is behind a proxy.
        return urlparse(request.META.get('HTTP_REFERER'))


def generate_image_prefix_url(request, zipped_filename):
    parsed_referrer_url = get_referrer_url(request)
    # Remove trailing slash
    zipcontent = reverse(
        'kolibri:core:zipcontent',
        kwargs={
            "zipped_filename": zipped_filename,
            "embedded_filepath": ''
        })[:-1]
    if parsed_referrer_url:
        # Reconstruct the parsed URL using a blank scheme and host + port(1)
        zipcontent = urlunparse(('', parsed_referrer_url[1], zipcontent, '', '', ''))
    return zipcontent.encode()


def get_host(request):
    parsed_referrer_url = get_referrer_url(request)
    if parsed_referrer_url:
        host = urlunparse((parsed_referrer_url[0], parsed_referrer_url[1], '', '', '', ''))
    else:
        host = request.build_absolute_uri(OPTIONS['Deployment']['URL_PATH_PREFIX'])
    return host.strip("/")


class ZipContentView(View):

    @xframe_options_exempt
    def options(self, request, *args, **kwargs):
        """
        Handles OPTIONS requests which may be sent as "preflight CORS" requests to check permissions.
        """
        response = HttpResponse()
        _add_access_control_headers(request, response)
        return response

    @cache_forever
    @xframe_options_exempt
    def get(self, request, zipped_filename, embedded_filepath):
        """
        Handles GET requests and serves a static file from within the zip file.
        """

        # calculate the local file path to the zip file
        zipped_path = get_content_storage_file_path(zipped_filename)

        # file size
        file_size = 0

        # if the zipfile does not exist on disk, return a 404
        if not os.path.exists(zipped_path):
            raise Http404('"%(filename)s" does not exist locally' % {'filename': zipped_filename})

        # if client has a cached version, use that (we can safely assume nothing has changed, due to MD5)
        if request.META.get('HTTP_IF_MODIFIED_SINCE'):
            return HttpResponseNotModified()

        with zipfile.ZipFile(zipped_path) as zf:

            # if no path, or a directory, is being referenced, look for an index.html file
            if not embedded_filepath or embedded_filepath.endswith("/"):
                embedded_filepath += "index.html"

            # get the details about the embedded file, and ensure it exists
            try:
                info = zf.getinfo(embedded_filepath)
            except KeyError:
                raise Http404('"{}" does not exist inside "{}"'.format(embedded_filepath, zipped_filename))

            # try to guess the MIME type of the embedded file being referenced
            content_type = mimetypes.guess_type(embedded_filepath)[0] or 'application/octet-stream'

            if not os.path.splitext(embedded_filepath)[1] == '.json':
                # generate a streaming response object, pulling data from within the zip  file
                response = FileResponse(zf.open(info), content_type=content_type)
                file_size = info.file_size
            else:
                image_prefix_url = generate_image_prefix_url(request, zipped_filename)
                # load the stream from json file into memory, replace the path_place_holder.
                content = zf.open(info).read()
                str_to_be_replaced = ('$' + exercises.IMG_PLACEHOLDER).encode()
                content_with_path = content.replace(str_to_be_replaced, image_prefix_url)
                response = HttpResponse(content_with_path, content_type=content_type)
                file_size = len(content_with_path)

        # set the content-length header to the size of the embedded file
        if info.file_size:
            response["Content-Length"] = file_size

        # ensure the browser knows not to try byte-range requests, as we don't support them here
        response["Accept-Ranges"] = "none"

        # add headers to ensure AJAX requests will be permitted for these files, even from a null origin
        _add_access_control_headers(request, response)

        # restrict CSP to only allow resources to be loaded from the Kolibri host, to prevent info leakage
        # (e.g. via passing user info out as GET parameters to an attacker's server), or inadvertent data usage
        host = get_host(request)
        response["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: " + host

        return response


class DownloadContentView(View):

    def get(self, request, filename, new_filename):
        """
        Handles GET requests and serves a static file as an attachment.
        """

        # calculate the local file path of the file
        path = get_content_storage_file_path(filename)

        # if the file does not exist on disk, return a 404
        if not os.path.exists(path):
            raise Http404('"%(filename)s" does not exist locally' % {'filename': filename})

        # generate a file response
        response = FileResponse(open(path, 'rb'))

        # set the content-type by guessing from the filename
        response['Content-Type'] = mimetypes.guess_type(filename)[0]

        # set the content-disposition as attachment to force download
        response['Content-Disposition'] = 'attachment;'

        # set the content-length to the file size
        response['Content-Length'] = os.path.getsize(path)

        return response
