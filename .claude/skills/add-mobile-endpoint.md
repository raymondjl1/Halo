---
name: add-mobile-endpoint
description: Add a new REST API endpoint for the Android app in halo_mobile. Triggers when working on /halo/api/v1/* routes or android/ code.
---

# Add Mobile API Endpoint

## Steps

1. **Add controller method** in `halo_mobile/controllers/main.py`:
   ```python
   @http.route('/halo/api/v1/{resource}', type='json', auth='user', methods=['GET'])
   def get_resource(self, **kwargs):
       business_id = request.env.user.business_id.id
       records = request.env['halo.model'].search_read(
           [('business_id', '=', business_id)],
           ['field1', 'field2'],
           order='create_date desc',
           limit=50,
       )
       return {'status': 'ok', 'data': records}
   ```

2. **Always include**:
   - `auth='user'` (requires authentication)
   - `business_id` filter (data isolation)
   - Explicit field list in `search_read` (don't leak internal fields)
   - Error handling with meaningful messages

3. **Add Retrofit method** in `android/app/.../api/HaloApiService.kt`:
   ```kotlin
   @GET("/halo/api/v1/{resource}")
   suspend fun getResource(): ResourceResponse
   ```

4. **Add ViewModel/Repository** methods in Android app.

5. **Test**: Odoo HttpCase for the endpoint, JUnit for Android ViewModel.
