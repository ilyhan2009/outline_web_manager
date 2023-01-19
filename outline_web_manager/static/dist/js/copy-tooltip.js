var btns = document.querySelectorAll('.btn-clipboard');

for (var i = 0; i < btns.length; i++) {
//    btns[i].addEventListener('mouseleave', function(e, b, c) {
//        setTimeout(clearTooltip, 2500, e);
//    });
    btns[i].addEventListener('blur', function(e) {
        if (e.target.getAttribute('aria-label-backup')) {
          e.target.setAttribute('aria-label', e.target.getAttribute('aria-label-backup'));
          e.target.removeAttribute('aria-label-backup');
        }
    });
}

function clearTooltip(e) {
    if (e.target.getAttribute('aria-label-backup')) {
      e.target.setAttribute('aria-label', e.target.getAttribute('aria-label-backup'));
      e.target.removeAttribute('aria-label-backup');
    }
}

function showTooltip(elem, msg) {
    if (elem.getAttribute('aria-label')) {
      elem.setAttribute('aria-label-backup', elem.getAttribute('aria-label'));
    }
    elem.setAttribute('aria-label', msg);

    elem.classList.add('tooltipped');
    elem.classList.add('tooltipped-ne');
}

function fallbackMessage(action) {
    var actionMsg = '';
    var actionKey = (action === 'cut' ? 'X' : 'C');
    if (/iPhone|iPad/i.test(navigator.userAgent)) {
        actionMsg = 'No support :(';
    } else if (/Mac/i.test(navigator.userAgent)) {
        actionMsg = 'Press ⌘-' + actionKey + ' to ' + action;
    } else {
        actionMsg = 'Press Ctrl-' + actionKey + ' to ' + action;
    }
    return actionMsg;
}

var clipboard_buttons = new ClipboardJS('.btn-clipboard');

clipboard_buttons.on('success', function(e) {
    e.clearSelection();
    showTooltip(e.trigger, 'Copied!');
});

clipboard_buttons.on('error', function(e) {
    showTooltip(e.trigger, fallbackMessage(e.action));
});