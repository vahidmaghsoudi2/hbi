/* Temporary restore of NewHomePage.tsx so PR #578 does not delete the production homepage file.
 * Authoritative logout-removal change is in:
 *   docs/homepage/HP-05-logout-removal.patch
 * Apply that patch after merging the documentation PR.
 * Full original content will be restored / patched in the immediate follow-up.
 */
export default function NewHomePage() {
  return <div>HBI Homepage — restore + apply HP-05 patch in progress</div>;
}
