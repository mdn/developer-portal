// Transforms a normal YouTube URL into an iframe embed URL
function transformYouTubeURL(url) {
  const re = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
  const match = url.match(re);
  if (!match) throw new Error('Failed to match YouTube ID');
  const id = match[2];
  if (id.length !== 11) throw new Error(`Invalid YouTube ID ${id}`);
  return `https://www.youtube.com/embed/${id}?autoplay=1&enablejsapi=1&modestbranding=1&rel=0`;
}

module.exports = class Modal {
  static create(trigger) {
    const { content, ...options } = this.createModalOptions(trigger);
    const element = document.createElement('div');
    element.className = 'mzp-u-modal-content';
    element.appendChild(content);
    return {
      open() {
        Mzp.Modal.createModal(element, content, {
          ...options,
          // The following methods prevent the video from autoplaying when the
          // modal is closed in some browsers.
          onCreate() {
            document.body.appendChild(element);
          },
          onDestroy() {
            document.body.removeChild(element);
          },
        });
      },
    };
  }

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

  static createModalOptions(element) {
    const content = this.createModalContent(element);
    const { className, closeText = 'Close modal', title } = element.dataset;
    return { className, closeText, content, title };
  }

  static init() {
    const elements = document.querySelectorAll('.js-modal-trigger');
    Array.from(elements).forEach(content => new Modal(content));
  }

  constructor(trigger) {
    this.trigger = trigger;
    this.trigger.addEventListener('click', event => this.open(event));
  }

  open(event) {
    try {
      if (!('modal' in this)) {
        this.modal = Modal.create(this.trigger);
      }
      // Prevent navigation only if a modal has been created
      event.preventDefault();
      this.modal.open();
    } catch (error) {
      // eslint-disable-next-line no-console
      console.warn(`Error creating modal: ${error.message}`);
    }
  }
};
