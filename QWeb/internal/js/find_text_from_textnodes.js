// find_text_from_textnodes.js
// Finds elements whose textContent matches or includes the given text

function getTextNodes(text, tag, partial) {
    let mainDoc = document.querySelector(tag);
    const iterator = document.createNodeIterator(mainDoc, NodeFilter.SHOW_TEXT);
    const textNodes = [];
    let currentNode;
    while ((currentNode = iterator.nextNode())) {
        if (currentNode.textContent.trim() === text) {
            textNodes.push(currentNode.parentElement);
            continue;
        } else if (partial && currentNode.textContent.trim().includes(text)) {
            textNodes.push(currentNode.parentElement);
        }
    }
    return textNodes;
}

// Entrypoint for Selenium execute_script
return getTextNodes(arguments[0], arguments[1], arguments[2]);
