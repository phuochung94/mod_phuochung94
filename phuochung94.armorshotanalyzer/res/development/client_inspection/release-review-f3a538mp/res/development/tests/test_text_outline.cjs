const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname,
    '../../gui/ArmorShotAnalyzer/gameface/ArmorShotAnalyzerBattleView.js'), 'utf8')
    .replace(/^import .*;$/m, 'const ModelObserver = () => ({});');
const elements = {};
const context = vm.createContext({
    document: { getElementById: id => (elements[id] ||= {style: {}}) },
    engine: { whenReady: { then() {} } },
});
vm.runInContext(source, context);
for (const [fill, outline] of [['9CFF3A','rgb(39,64,15)'],
    ['FFC04D','rgb(64,48,19)'], ['FF4040','rgb(64,16,16)'],
    ['FFFFFF','rgb(64,64,64)'], ['D0D0D0','rgb(52,52,52)'],
    ['CCE143','rgb(51,56,17)']]) {
    assert.equal(context.outlineColor(fill), outline);
    context.renderRow(elements['armor-label'], '-', true, fill);
    assert.equal(elements['armor-label'].style.color, '#' + fill);
    assert.ok(elements['armor-label'].style.textShadow.includes(outline));
}
assert.equal(context.outlineColor('invalid'), '#171A10');
context.renderRow(elements['armor-label'], '-', false, 'FFC04D');
assert.equal(elements['armor-label'].style.display, 'none');
console.log('Tinted outlines: green/orange/red/white/grey/gradient and visibility OK');
