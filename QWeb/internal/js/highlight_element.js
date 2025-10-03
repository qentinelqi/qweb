// highlight_element.js
// Highlights a web element with a border, optionally blinking or flashing

function blink(el, style, color) {
    el.style.border = `5px solid ${color}`;
    setTimeout(function(){
        el.style.border = style;
    }, 2000);
}

function flash(el, style, color) {
    el.style.border = `5px solid ${color}`;
    setTimeout(function(){
        el.style.border = style;
    }, 300);
}

function show(el, draw_only, flash_border, color) {
    let style = el.style.border;
    if (draw_only === false && flash_border === false) {
        blink(el, style, color);
    } else if (flash_border === true && draw_only === false) {
        flash(el, style, color);
    } else {
        blink(el, "5px solid " + color, color);
    }
}

// Entrypoint for Selenium execute_script
show(arguments[0], arguments[1], arguments[2], arguments[3]);
