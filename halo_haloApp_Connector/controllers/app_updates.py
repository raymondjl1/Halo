from odoo import http
from odoo.http import request, Response
import json
import base64
import io
import tarfile
import logging

# Set up logging
_logger = logging.getLogger(__name__)

class AppUpdateController(http.Controller):
    @http.route('/get_updates', type='http', auth='public', methods=['POST'], csrf=False)
    def get_updates(self, **post):
        try:
            # Get the client's current version from POST data
            current_version = post.get('current_version', '0.0.0')

            # Get all updates newer than current version
            updates = request.env['halo.cus.app.updates'].sudo().search([
                ('version', '>', current_version)
            ], order='version ASC')

            if not updates:
                return Response(
                    json.dumps({'message': 'No updates available'}),
                    content_type='application/json'
                )

            # Create a memory file for our update package
            package_buffer = io.BytesIO()

            # Create the package with all updates
            with tarfile.open(fileobj=package_buffer, mode='w:gz') as archive:
                for update in updates:
                    if update.attachment_id:
                        # Get the attachment data (the actual update file)
                        file_content = base64.b64decode(update.attachment_id.datas)
                        if not file_content:
                            raise ValueError(f"File content for update {update.name} is empty.")

                        # Add the update file to the archive
                        file_buffer = io.BytesIO(file_content)
                        info = tarfile.TarInfo(name=f"{update.version}/{update.file_name}")
                        info.size = len(file_content)
                        _logger.info(f"HALO SW Update: Adding file: {update.version}/{update.file_name}, size: {info.size} bytes")  # info
                        archive.addfile(info, file_buffer)

                        # Add metadata for each update in a separate file (metadata.json)
                        metadata = {
                            'version': update.version,
                            'name': update.name,
                            'filename': update.file_name
                        }
                        metadata_str = json.dumps(metadata)
                        metadata_buffer = io.BytesIO(metadata_str.encode('utf-8'))
                        meta_info = tarfile.TarInfo(name=f"{update.version}/metadata.json")
                        meta_info.size = len(metadata_str.encode('utf-8'))
                        _logger.info(f"HALO SW Update: Adding metadata: {update.version}/metadata.json, size: {meta_info.size} bytes")  # info
                        archive.addfile(meta_info, metadata_buffer)

            # Get the final content of the update package
            package_content = package_buffer.getvalue()
            _logger.info(f"HALO SW Update: Package size: {len(package_content)} bytes")  # info

            # Return the response with the .tar.gz file content
            return Response(
                package_content,
                content_type='application/x-tar',
                headers=[
                    ('Content-Disposition', 'attachment; filename="updates.tar.gz"'),
                    ('Content-Length', str(len(package_content)))
                ]
            )

        except Exception as e:
            # Log the error and return the error message as JSON
            _logger.error(f"HALO SW Update: Error while preparing updates: {str(e)}")
            return Response(
                json.dumps({'error': str(e)}),
                content_type='application/json'
            )