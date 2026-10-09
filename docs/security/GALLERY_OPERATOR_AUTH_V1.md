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
- Customers are records in the gallery workflow, not system users. Public customer registration and customer-token issuance/refresh are disabled; customer records do not receive direct API access.
- Financial sale creation remains Admin-only. The frontend obtains a separate Admin session for the sale mutation; it must never pass an operator token as a substitute.
- Do not expose either token to the customer or log credentials/tokens.
- Deployment configuration is not performed by this code change. Production behavior must be verified after the environment variables are set.

## Legacy pilot role-token endpoints

- `/auth/pilot-operator-token` and `/auth/pilot-po-token` are disabled by default, including in development.
- They require the explicit server-side opt-in `HBI_ENABLE_PILOT_TOKENS=true` and are still denied whenever `HBI_ENV=production`.
- This opt-in exists only for isolated local development/test environments while the legacy Product Editor/PO UI flow is being replaced. Never enable it on a shared or publicly reachable environment; these endpoints mint internal-role tokens without authenticating a person.
- A successful HTTP response from these endpoints is not evidence that a real operator or Admin identity was authenticated.
