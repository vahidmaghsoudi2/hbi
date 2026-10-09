# Gallery Operator Authentication V1

The gallery operator is a separate operational identity. It is not a customer identity and it is not an Admin identity.

## Required server configuration

Set these server-side environment variables before starting the application:

- `HBI_GALLERY_OPERATOR_USERNAME`: unique operator username.
- `HBI_GALLERY_OPERATOR_PASSWORD`: strong operator password.
- `HBI_GALLERY_OPERATOR_SUBJECT`: optional stable subject ID; defaults to `USR_GALLERY_OPERATOR`.

The configured account is provisioned with the `GalleryOperator` role during application startup. There is intentionally no default username or password. Use a username distinct from the Admin account.

## Access boundary

- GalleryOperator may search/select customers, perform intake using mobile + surname matching, and create/read consultation cases and recommendations for the selected customer.
- A mobile number already attached to a different surname returns HTTP 409; it is not silently rebound to another identity.
- Customer tokens remain owner-scoped for self-service routes.
- Financial sale creation remains Admin-only. The frontend obtains a separate Admin session for the sale mutation; it must never pass an operator token as a substitute.
- Do not expose either token to the customer or log credentials/tokens.
- Deployment configuration is not performed by this code change. Production behavior must be verified after the environment variables are set.
