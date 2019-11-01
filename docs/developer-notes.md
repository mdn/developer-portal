# Developer notes

## Articles are surfaced as 'Posts' to users and to editors

`apps.articles.models` contains `Articles` and `Article` page types, where the naming has come from initial development. In user-facing pages, however, and in the Wagtail Admin, we are preferring to use the term "Posts", to give us more semantic flexibility with what we can do with these pages.

This re-labelling may or may not be permanent.

As a result, the changes done were all kept (as part of ticket 624) at surface level, with no table-altering migrations and no change to the CSS classnames which mention `article`. Similarly, no template names were changed, so you'll find `articles.html` and `article.html` not `post.html`, etc.

Streamfield blocks have been renamed from 'article' to 'post' to keep the UI consistent, but the internal use of a `type` or `resource_type` attribute on a Page instance has been left with the value 'article', not changed to 'post' because that would have been a non-visible-to-humans change.

However, in the future, we may decide that we definitely want to stick with "Posts", in which case a proper model-renaming exercise is worth it, along with CSS and template-name changes, too.
