# RFC 1: Provide option to require a comment when submitting content for moderation

* RFC: 1
* Author: Steve Jalim and Val Grimm
* Created: 2019-12-21
* Last Modified: 2019-12-23

## Abstract

Moderators for Wagtail websites do not always have context when content is submitted to them for moderation.
Requiring that a comment be included with each moderation request prompts content contributors to follow an effective coordination workflow. This mirrors similar workflows in Github.

## Specification

#### Rationale ####
* Currently there is no way provided in Wagtail for moderators and editors to communicate.
* This necessitates the use of email or instant message between moderators and editors to discuss submissions.
* That adds overhead.
* This overhead can constitute a bottleneck in the publication of content, becoming especially onerous when editors are much more numerous than moderators.
* Editors may appreciate the reduced friction of being able to clarify their wishes to moderators in the submission flow, rather than outside of it. 

#### AC ####
*End user behavior*: 
1) After an Editor (or role with equivalent permissions) selects "Submit for Moderation" in the [?name] dropdown
they should be redirected to a page
with a required comment field with the label
"Please write a comment here to provide context for your submission",
of length 150 characters and a
"Confirm submission" button beneath it.
The button should remain grayed out and un-clickable until after the user has entered content in the comment field.

*Administration behavior*:
1) It should be possible to deactivate this functionality in code. It is not necessary to make this functionality deactivatable through the admin GUI.
* Rationale for only making this functionality deactivatable via code is that then it will be easier to implement,
and not disabled without good reason. 

### Technical specification

[Content to come]

### Drawbacks
* A developer will be needed to deactivate the functionality as described above.
* In some situations the functionality will not be needed.
* When this functionality is implemented, it will be easy for editors to circumvent by typing nonsense into the comment field. 

### Alternatives
* More detailed linting functionality to enable administrators to ensure that comment submissions are not spurious. 
* A reminder emailed to editors upon submission to ensure that they give context to moderators by email or instant message. 
* A reminder screen displayed to editors after submission. 

## Open Questions

// Include any questions until Status is ‘Accepted’
