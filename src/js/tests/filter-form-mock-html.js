exports.PostsFilterFormTestHTML = `
  <aside class="mzp-l-sidebar custom-width">

    <details class="filter-list-sidebar-content filter-list-sidebar-content-mobile">
      <summary>Filter</summary>

      <form class="filter-form js-filter-form" data-controls="article_or_video-cards" action="/posts/">

        <header class="filter-form-section js-filter-form-clear-section">
          <a href="#" class="filter-form-clear js-filter-clear">
            <span class="icon">
              <svg width="12" height="12" xmlns="http://www.w3.org/2000/svg"><path d="M6 4.586L10.243.343a1 1 0 1 1 1.414 1.414L7.414 6l4.243 4.243a1 1 0 1 1-1.414 1.414L6 7.414l-4.243 4.243a1 1 0 1 1-1.414-1.414L4.586 6 .343 1.757A1 1 0 1 1 1.757.343L6 4.586z" fill="currentColor" fill-rule="evenodd"></path></svg>

            </span>
            Clear all
          </a>
        </header>

        <fieldset class="filter-form-section">
          <header class="filter-form-section-header">
            <h5>Products &amp; Technologies</h5>
            <a href="#" class="filter-form-clear js-filter-clear" data-controls="topic">
              <span class="icon">
                <svg width="12" height="12" xmlns="http://www.w3.org/2000/svg"><path d="M6 4.586L10.243.343a1 1 0 1 1 1.414 1.414L7.414 6l4.243 4.243a1 1 0 1 1-1.414 1.414L6 7.414l-4.243 4.243a1 1 0 1 1-1.414-1.414L4.586 6 .343 1.757A1 1 0 1 1 1.757.343L6 4.586z" fill="currentColor" fill-rule="evenodd"></path></svg>

              </span>
              Clear
            </a>
          </header>

            <label>
              <input type="checkbox" name="topic" value="av1-video">
              AV1 &amp; Video
            </label>

            <label>
              <input type="checkbox" name="topic" value="browser-extensions">
              Browser Extensions
            </label>

            <label>
              <input type="checkbox" name="topic" value="css">
              CSS
            </label>

            <label>
              <input type="checkbox" name="topic" value="firefox-mobile">
              Firefox for mobile
            </label>

            <label>
              <input type="checkbox" name="topic" value="javascript">
              JavaScript
            </label>

            <label>
              <input type="checkbox" name="topic" value="unused-test-topic">
              Test topic with no logo
            </label>

            <label>
              <input type="checkbox" name="topic" value="voice">
              Voice
            </label>

            <label>
              <input type="checkbox" name="topic" value="test-topic">
              WebThings
            </label>

        </fieldset>

        <fieldset class="filter-form-section">
          <header class="filter-form-section-header">
            <h5>Search</h5>
              <a href="#" class="filter-form-clear js-filter-clear" data-controls="search">
              <span class="icon">
                <svg width="12" height="12" xmlns="http://www.w3.org/2000/svg"><path d="M6 4.586L10.243.343a1 1 0 1 1 1.414 1.414L7.414 6l4.243 4.243a1 1 0 1 1-1.414 1.414L6 7.414l-4.243 4.243a1 1 0 1 1-1.414-1.414L4.586 6 .343 1.757A1 1 0 1 1 1.757.343L6 4.586z" fill="currentColor" fill-rule="evenodd"></path></svg>
              </span>
              Clear
            </a>
          </header>
          <input class="filter-form-search js-search-input" name="search" value="" placeholder="Refine with keywords">
        </fieldset>

        <div class="filter-form-section filter-form-footer">
          <button class="js-filter-form-submit mzp-c-button mzp-t-small" type="submit">Refine results</button>
        </div>
      </form>

    </details>

    <div class="filter-list-sidebar-content filter-list-sidebar-content-desktop">
      <form class="filter-form js-filter-form" data-controls="article_or_video-cards" action="/posts/">
        <header class="filter-form-section js-filter-form-clear-section">
          <a href="#" class="filter-form-clear js-filter-clear">
            <span class="icon">
              <svg width="12" height="12" xmlns="http://www.w3.org/2000/svg"><path d="M6 4.586L10.243.343a1 1 0 1 1 1.414 1.414L7.414 6l4.243 4.243a1 1 0 1 1-1.414 1.414L6 7.414l-4.243 4.243a1 1 0 1 1-1.414-1.414L4.586 6 .343 1.757A1 1 0 1 1 1.757.343L6 4.586z" fill="currentColor" fill-rule="evenodd"></path></svg>
            </span>
            Clear all
          </a>
        </header>

        <fieldset class="filter-form-section">
          <header class="filter-form-section-header">
            <h5>Products &amp; Technologies</h5>
            <a href="#" class="filter-form-clear js-filter-clear" data-controls="topic">
              <span class="icon">
                <svg width="12" height="12" xmlns="http://www.w3.org/2000/svg"><path d="M6 4.586L10.243.343a1 1 0 1 1 1.414 1.414L7.414 6l4.243 4.243a1 1 0 1 1-1.414 1.414L6 7.414l-4.243 4.243a1 1 0 1 1-1.414-1.414L4.586 6 .343 1.757A1 1 0 1 1 1.757.343L6 4.586z" fill="currentColor" fill-rule="evenodd"></path></svg>

              </span>
              Clear
            </a>
          </header>

          <label>
            <input type="checkbox" name="topic" value="av1-video">
            AV1 &amp; Video
          </label>

          <label>
            <input type="checkbox" name="topic" value="browser-extensions">
            Browser Extensions
          </label>

          <label>
            <input type="checkbox" name="topic" value="css">
            CSS
          </label>

          <label>
            <input type="checkbox" name="topic" value="firefox-mobile">
            Firefox for mobile
          </label>

          <label>
            <input type="checkbox" name="topic" value="javascript">
            JavaScript
          </label>

          <label>
            <input type="checkbox" name="topic" value="unused-test-topic">
            Test topic with no logo
          </label>

          <label>
            <input type="checkbox" name="topic" value="voice">
            Voice
          </label>

          <label>
            <input type="checkbox" name="topic" value="test-topic">
            WebThings
          </label>

        </fieldset>

        <fieldset class="filter-form-section">
          <header class="filter-form-section-header">
            <h5>Search</h5>
              <a href="#" class="filter-form-clear js-filter-clear" data-controls="search">
              <span class="icon">
                <svg width="12" height="12" xmlns="http://www.w3.org/2000/svg"><path d="M6 4.586L10.243.343a1 1 0 1 1 1.414 1.414L7.414 6l4.243 4.243a1 1 0 1 1-1.414 1.414L6 7.414l-4.243 4.243a1 1 0 1 1-1.414-1.414L4.586 6 .343 1.757A1 1 0 1 1 1.757.343L6 4.586z" fill="currentColor" fill-rule="evenodd"></path></svg>
              </span>
              Clear
            </a>
          </header>
          <input class="filter-form-search js-search-input" name="search" value="" placeholder="Refine with keywords">
        </fieldset>

        <div class="filter-form-section filter-form-footer">
          <button class="js-filter-form-submit mzp-c-button mzp-t-small" type="submit">Refine results</button>
        </div>
      </form>
    </div>
  </aside>`;
