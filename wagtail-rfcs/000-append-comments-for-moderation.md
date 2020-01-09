# RFC 1: Provide option to require a comment when submitting content for moderation

- RFC: 1
- Authors: Val Grimm (@valgrimm) and Steve Jalim (@stevejalim)
- Created: 2019-12-21
- Last Modified: 2019-12-30

## Abstract

Moderators for Wagtail websites do not always have context about a change made to Page content when it is submitted to them for moderation. They receive a notification that something has changed on the Page, and it is possible in Wagtail to see which Page fields have changed (and how) by comparing the Page pending moderation with its live version, but there is no summary information about _why_ (ie, something akin to a source-code commit, which has a log entry).
Being able to require the inclusion of a comment with each moderation request would help address this information gap, resulting in a more effective coordination workflow.

## Specification

### Rationale

- Currently there is no way provided in Wagtail for moderators and editors to communicate.
- This necessitates the use of email or instant message between moderators and editors to discuss submissions.
- This adds overhead which can constitute a bottleneck in the publication of content, becoming especially onerous when editors are much more numerous than moderators.
- Editors may appreciate the reduced friction of being able to clarify their wishes to moderators in the submission flow, rather than outside of it.

### Acceptance Criteria

_End-user behavior_:

1. After an Editor (or role with equivalent permissions) selects "Submit for Moderation" in the main combo-button _and_ a configuration setting to require a submission comment is enabled:

   - They will be presented with a modal dialog box
   - The dialog box will contain a comment field
   - The comment field will be required
   - The comment field will have an enforced and clearly marked maximum length of 500 characters
   - The comment field will have a label that reads "Please add a comment here to provide context for your submission"
   - The dialog box will have a "Complete submission for Moderation" button beneath it
   - This submission button will remain disabled until the user enters content in the comment field

If the setting to require a submission comment is not enabled, the behaviour of the workflow remains the same as the current version of Wagtail.

_Administration behavior_:

1. It should be possible to activate/deactivate this functionality via Wagtail/Django `settings`, but it is not necessary to surface this option in the Wagtail Admin's Settings UI.

Note: the rationale for only making this functionality deactivatable via code is:

- it will be easier to implement
- keeping it out of the Admin UI means it cannot be disabled without good reason

### Technical specification

_This specification is still loose and suggestions are welcome_

1. A new Wagtail setting is added: `REQUIRE_COMMENT_FOR_MODERATION_SUBMISSION`
2. A new field (`moderation_comment`, `models.CharField(max_length=500, blank=True)`) is added to the `PageRevision` class.
3. Given the Admin UI for creation and editing uses a Django form as its transport mechanism, we slot in an additional form field (`moderation_comment`, `forms.CharField(max_length=500, required=True, widget=forms.Textarea()`) for the submission comment's text, _but only if `REQUIRE_COMMENT_FOR_MODERATION_SUBMISSION` is `True`._
   - If this field is present in the DOM, its visibility will initially be hidden.
4. An update to the Admin UI's JS is required:

   - The JS must watch for submission of a Page for moderation and prevent the HTTP POST that would normally send the form's payload to the server
   - It will then trigger a basic modal popup to capture the required info from the Editor
   - The modal will show the label, as described above
   - The modal will have a button to complete the submission, as described above. It will take the `disabled` state while the `moderation_comment` `<textarea>`'s content has no length or is greater than 500 characters. The page's JS will update the `disabled` state of the submission button accordingly, so that only valid comment content can be submitted.
   - Once the submission-completion button has been clicked, the full page PLUS the new moderation-request comment will be sent to the server. (How this is done is definitely open: it could be that the payload state is copied/held when the original POST is blocked, and then that payload is updated before finally being POSTed; alternatively, the whole page could be re-POSTed now the hidden `moderation_comment` field has been populated)

5. The server receives the form payload and, upon seeing a `moderation_comment` field:

   - validates that it is between 0 and 500 characters.
   - ensures that data is saved with the `PageRevision` it creates.
     - Note: If validation fails, Wagtail does not save the new revision and instead returns an error message using the same workflow as per any required field missing data.
       - It might be useful to outline the Publish combo-button in red, to show where the user needs to go to amend the problem.

6. When any Editor is informed via email that a Page has been submitted for moderation, the `moderation_comment` shall also be included (but must be marked safe/sanitised)
7. When any Editor views the details of a Page pending Moderation (ie at `admin/pages/<pageid>/revisions/compare/live...<newrev>/`), if the relevant revision has a `moderation_comment`, it should be shown above the list of field diffs.

Notes:

- The same behaviour will need to be present on both page creation and page editing forms

## Drawbacks

- A code change will be needed to enable/disable the functionality as described above.
- In some situations the functionality will not be needed, so this change adds complexity to provide non-core functionality.
- This functionality will not guarantee an improved workflow: Editors can still circumvent it by typing nonsense into the comment field.

## Alternatives

- A reminder emailed to editors upon submission to ensure that they give context to moderators by email or instant message.
- A reminder screen displayed to editors after submission, asking them to do similar.

## Open Questions

- Is there a better way to slot on the `moderation_comment` data without having to block the submission first?
- Is this option compatible with any known plans to move away from using a Django `Form` for the page payload transport?
- Do we want to make the max-length of the moderation comment more than 500 chars?
