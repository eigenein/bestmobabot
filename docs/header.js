// Run:
// cat header.js heroes.js footer.js | sed 's/h.AS3 = L;/h.AS3 = L; window.h = h;/g' | node

const { performance } = require('perf_hooks');

window = function() {
    return window;
}

window.document = window;
window.navigator = window;
window.performance = performance;
window.createElement = window;
window.getContext = window;
window.fillRect = window;
window.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36';
