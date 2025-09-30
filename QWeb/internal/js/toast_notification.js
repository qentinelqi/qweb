// toast_notification.js
// Display toast notification in the browser via JavaScript.

function createToastNotification(message, level = "info", position = "center", fontSize = 18, heading = "Test Automation Notification", timeout = 3) {
    var host = document.createElement('div');
    host.style.position = 'fixed';
    host.style.top = '0';
    host.style.left = '0';
    host.style.width = '100%';
    host.style.height = '100%';
    host.style.pointerEvents = 'none';
    host.style.zIndex = '2147483647';
    document.body.appendChild(host);

    var shadow = host.attachShadow({ mode: 'open' });

    var style = document.createElement('style');
    style.textContent = `
      * {
        box-sizing: border-box;
        font-family: sans-serif, system-ui, Arial, Helvetica;
        color: white;
      }
    `;
    shadow.appendChild(style);

    var toast = document.createElement('div');
    var iconText = '';
    var bgColor = 'black';

    if (level === 'success') { iconText = '✔️'; bgColor = 'green'; }
    else if (level === 'warning') { iconText = '⚠️'; bgColor = 'orange'; }
    else if (level === 'error') { iconText = '✖'; bgColor = 'red'; }
    else { iconText = 'ℹ️'; bgColor = 'black'; }

    toast.style.position = 'fixed';
    toast.style.padding = '20px';
    toast.style.borderRadius = '10px';
    toast.style.zIndex = '10000';
    toast.style.fontSize = fontSize + 'px';
    toast.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.4)';
    toast.style.border = '2px solid white';
    toast.style.opacity = '0';
    toast.style.background = bgColor;
    toast.style.transition = 'opacity 0.5s ease';
    toast.style.display = 'flex';
    toast.style.flexDirection = 'column';
    toast.style.alignItems = 'flex-start';
    toast.style.gap = '8px';

    if (position === 'top-left') { toast.style.top = '20px'; toast.style.left = '20px'; }
    else if (position === 'top-right') { toast.style.top = '20px'; toast.style.right = '20px'; }
    else if (position === 'bottom-left') { toast.style.bottom = '20px'; toast.style.left = '20px'; }
    else if (position === 'bottom-right') { toast.style.bottom = '20px'; toast.style.right = '20px'; }
    else { toast.style.top = '50%'; toast.style.left = '50%'; toast.style.transform = 'translate(-50%, -50%)'; }

    var headingElem = document.createElement('div');
    headingElem.style.display = 'flex';
    headingElem.style.alignItems = 'center';
    headingElem.style.fontSize = '13px';
    headingElem.style.fontWeight = 'bold';
    headingElem.style.marginBottom = '4px';

    var headingIcon = document.createElement('span');
    headingIcon.textContent = iconText;
    headingIcon.style.fontSize = '16px';
    headingIcon.style.marginRight = '5px';

    headingElem.appendChild(headingIcon);
    headingElem.appendChild(document.createTextNode(heading));
    toast.appendChild(headingElem);

    var text = document.createElement('div');
    text.textContent = message;
    toast.appendChild(text);

    shadow.appendChild(toast);

    void toast.offsetHeight;
    toast.style.opacity = '1';

    setTimeout(function() {
      toast.style.opacity = '0';
      setTimeout(function() { host.remove(); }, 500);
    }, timeout * 1000);
}
