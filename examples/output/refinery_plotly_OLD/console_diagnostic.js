// Copy and paste this entire script into the browser console on http://localhost:8764
// It will search for and inspect all filter-related elements

console.log('=== TRELLISCOPE FILTER DIAGNOSTIC ===\n');

// 1. Find all elements containing "[missing]" text
console.log('1. SEARCHING FOR "[missing]" TEXT:');
const allElements = document.querySelectorAll('*');
const missingElements = Array.from(allElements).filter(el => {
    return el.textContent.includes('[missing]') && el.children.length === 0;
});
console.log(`Found ${missingElements.length} elements with "[missing]" text:`);
missingElements.forEach((el, i) => {
    console.log(`  [${i}] ${el.tagName}.${el.className}`);
    console.log(`      Text: "${el.textContent}"`);
    console.log(`      Parent: ${el.parentElement?.tagName}.${el.parentElement?.className}`);
});

// 2. Find React Select components
console.log('\n2. REACT SELECT COMPONENTS:');
const reactSelects = document.querySelectorAll('[class*="react-select"], [class*="Select__"], [id*="react-select"]');
console.log(`Found ${reactSelects.length} React Select elements`);
reactSelects.forEach((el, i) => {
    console.log(`  [${i}] ${el.tagName}.${el.className}`);
    console.log(`      ID: ${el.id}`);
    console.log(`      Text: "${el.textContent.substring(0, 100)}..."`);
});

// 3. Find any select/dropdown elements
console.log('\n3. NATIVE SELECT ELEMENTS:');
const selects = document.querySelectorAll('select');
console.log(`Found ${selects.length} select elements`);
selects.forEach((sel, i) => {
    console.log(`  [${i}] ID: ${sel.id}, Name: ${sel.name}, Options: ${sel.options.length}`);
    if (sel.options.length > 0) {
        console.log(`      First option: "${sel.options[0].text}"`);
    }
});

// 4. Search for filter-related attributes
console.log('\n4. ELEMENTS WITH "filter" IN ATTRIBUTES:');
const filterAttrs = document.querySelectorAll('[data-filter], [data-testid*="filter"], [aria-label*="filter" i]');
console.log(`Found ${filterAttrs.length} elements with filter attributes`);
filterAttrs.forEach((el, i) => {
    console.log(`  [${i}] ${el.tagName}.${el.className}`);
    console.log(`      Attributes:`, {
        'data-filter': el.getAttribute('data-filter'),
        'data-testid': el.getAttribute('data-testid'),
        'aria-label': el.getAttribute('aria-label')
    });
});

// 5. Search the React fiber tree (if accessible)
console.log('\n5. REACT FIBER TREE INSPECTION:');
const root = document.getElementById('trelliscope-root');
if (root) {
    const fiberKey = Object.keys(root).find(key => key.startsWith('__react'));
    if (fiberKey) {
        console.log(`Found React fiber key: ${fiberKey}`);
        const fiber = root[fiberKey];
        console.log('Fiber type:', fiber?.type);
        console.log('Fiber props:', Object.keys(fiber?.memoizedProps || {}));
    } else {
        console.log('Cannot access React fiber tree (React 18+ protection)');
    }
} else {
    console.log('Root element not found');
}

// 6. Check for any console errors or warnings that might be relevant
console.log('\n6. CHECKING FOR STORED ERRORS:');
console.log('(Check the Console tab for any red error messages)');

// 7. Inspect the actual filter sidebar/panel
console.log('\n7. FILTER PANEL STRUCTURE:');
const panels = document.querySelectorAll('[class*="panel"], [class*="Panel"], [class*="sidebar"], [class*="Sidebar"]');
console.log(`Found ${panels.length} potential panel elements`);
panels.forEach((panel, i) => {
    const text = panel.textContent;
    if (text.includes('Country') || text.includes('country') || text.includes('Filter')) {
        console.log(`  [${i}] ${panel.tagName}.${panel.className}`);
        console.log(`      Contains: ${text.substring(0, 200)}`);
        // Look for children
        const children = Array.from(panel.children);
        console.log(`      Children: ${children.length}`);
        children.slice(0, 5).forEach((child, j) => {
            console.log(`        [${j}] ${child.tagName}.${child.className}`);
        });
    }
});

console.log('\n=== DIAGNOSTIC COMPLETE ===');
console.log('Please copy all output above and share it.');
