/**
 * @constant
 * @type {RegExp}
    ^https?:\/\/              Start with 'http://' or 'https://'
    (?:                       non-capturing group matching
      (?:www\.)?                an optional 'www.' subdomain
      youtube(?:-nocookie)?     'youtube' or 'youtube-nocookie' domain
      \.com\/                   '.com/' TLD (explicit slash to prevent matching 'https://youtube.com.foo/')
      .*                        any characters
      (?:                       non-capturing group matching
        \/|                       '/' or
        v\/|                      'v/' or
        u\/\w\/|                  'u/w/' or
        embed\/|                  'embed/' or
        \?v=|                     '?v=' or
        &v=                       '&v='
      )                         end non-capturing group
    |                         or
      youtu.be\/                'youtu.be/' domain and TLD (explicit slash to prevent matching 'https://youtu.be.foo/')
    )                         end non-capturing group
    (?                        a capturing group matching
      [\w-]{11}                 11 characters matching A-Z, a-z, 0-9, hyphen or underscore
    )                         end capture group
 */
const RE_MATCH_YOUTUBE_URL = /^https?:\/\/(?:(?:www\.)?youtube(?:-nocookie)?\.com\/.*(?:\/|v\/|u\/\w\/|embed\/|\?v=|&v=)|youtu.be\/)([\w-]{11})/;

/**
 * Helper method, transforms a normal YouTube URL into an iframe embed URL
 *
 * @param {string} url A YouTube URL string
 * @returns {string}
 */
function transformYouTubeURL(url) {
  const match = url.match(RE_MATCH_YOUTUBE_URL);
  if (!match) throw new Error('Failed to match YouTube ID');
  const id = match[1];
  return `https://www.youtube.com/embed/${id}?autoplay=1&enablejsapi=1&modestbranding=1&rel=0`;
}

/**
 * Listens to a trigger element for click events and constructs content for use
 * with Mzp.Modal.
 *
 * @class Modal
 */
module.exports = class Modal {
  /**
   * Returns modal content for given trigger element, via delegation.
   *
   * @param {Element} element
   * @returns {Element}
   */
  static createModalContent(element) {
    const content = document.createElement('div');
    switch (element.dataset.type) {
      // Handle more content types here.
      case 'video':
        content.appendChild(this.createModalContentVideo(element));
        break;
      default:
        throw new Error(`Unhandled type '${element.dataset.type}'`);
    }
    return content;
  }

  /**
   * Returns modal content for 'video' type trigger elements.
   *
   * @param {Element} element
   * @returns {Element}
   */
  static createModalContentVideo(element) {
    const container = document.createElement('div');
    container.className = 'responsive-object';
    container.style.paddingBottom = '56.25%';
    const iframe = document.createElement('iframe');
    iframe.allowFullscreen = true;
    iframe.frameBorder = 0;
    iframe.src = transformYouTubeURL(element.href);
    iframe.setAttribute(
      'allow',
      'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture',
    );
    container.appendChild(iframe);
    return container;
  }

  /**
   * Returns Mzp.Modal options from an element’s data attributes.
   *
   * @param {Element} element
   * @returns {object}
   */
  static createModalOptions(element) {
    const content = this.createModalContent(element);
    const { className, closeText = 'Close modal', title } = element.dataset;
    return { className, closeText, content, title };
  }

  /**
   * Constructs an instance of Modal class for each trigger element.
   *
   * @returns {Modal[]}
   */
  static init() {
    const elements = document.querySelectorAll('.js-modal-trigger');
    return Array.from(elements).map(element => new Modal(element));
  }

  /**
   * Binds click event listener to trigger element.
   *
   * @param {Element} trigger
   */
  constructor(trigger) {
    this.trigger = trigger;
    this.trigger.addEventListener('click', event => this.onClick(event));
  }

  /**
   * Initial set up for modal, called on demand instead of in constructor.
   */
  createModal() {
    const { content, ...options } = Modal.createModalOptions(this.trigger);
    this.content = content;
    this.options = options;
    this.modal = document.createElement('div');
    this.modal.className = 'mzp-u-modal-content';
    this.modal.appendChild(content);
  }

  /**
   * Creates the Mzp.Modal instance.
   */
  open() {
    Mzp.Modal.createModal(this.modal, this.content, {
      ...this.options,
      // The following methods prevent the video from autoplaying when the
      // modal is closed in some browsers.
      onCreate: () => document.body.appendChild(this.modal),
      onDestroy: () => document.body.removeChild(this.modal),
    });
  }

  /**
   * Creates a modal if one does not exist and opens it.
   *
   * @param {Event} event
   */
  onClick(event) {
    try {
      if (!this.modal) this.createModal();
      // Prevent navigation only if a modal has been created
      event.preventDefault();
      this.open();
    } catch (error) {
      // eslint-disable-next-line no-console
      console.warn(`Error creating modal: ${error.message}`);
    }
  }
};
